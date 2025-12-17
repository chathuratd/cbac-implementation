from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import time
from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.services.vector_store import VectorStoreService
from app.services.document_store import DocumentStoreService
from app.services.clustering import ClusteringService
from app.services.core_analyzer import CoreAnalyzerService
from app.services.analysis_store import AnalysisStore
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analysis", tags=["Analysis"])

# Initialize analysis store
analysis_store = AnalysisStore()


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_user_behaviors(
    request: AnalysisRequest,
    force: bool = False
) -> AnalysisResponse:
    """
    Main endpoint: Analyze user behaviors and derive core behavioral patterns.
    
    Process:
    1. Fetch behaviors from Qdrant (with embeddings)
    2. Check if behaviors changed (incremental analysis)
    3. Cluster behaviors semantically using HDBSCAN
    4. Derive generalized core behaviors from clusters
    5. Return core behaviors with confidence scores and evidence chains
    
    Args:
        request: AnalysisRequest with user_id and optional parameters
        force: If True, force re-analysis even if no behavior changes detected
        
    Returns:
        AnalysisResponse with derived core behaviors
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting analysis for user: {request.user_id} (force={force})")
        
        # Step 1: Fetch behaviors from Qdrant
        vector_service = VectorStoreService()
        behaviors = vector_service.get_behaviors_by_user(request.user_id)
        
        if not behaviors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No behaviors found for user {request.user_id}"
            )
        
        logger.info(f"Fetched {len(behaviors)} behaviors")
        
        # Step 2: Incremental Analysis - Check if behaviors changed
        if not force:
            previous_analysis = analysis_store.load_previous_analysis(request.user_id)
            
            if previous_analysis:
                # Extract behavior IDs from previous analysis
                prev_behavior_ids = set()
                if "core_behaviors" in previous_analysis:
                    for cb in previous_analysis["core_behaviors"]:
                        if "evidence_chain" in cb:
                            prev_behavior_ids.update(cb["evidence_chain"])
                
                # Get current behavior IDs
                curr_behavior_ids = set(b.behavior_id for b in behaviors)
                
                # Check if behaviors changed
                if prev_behavior_ids == curr_behavior_ids:
                    processing_time = (time.time() - start_time) * 1000
                    logger.info(
                        f"No behavior changes detected for user {request.user_id}, "
                        f"returning cached analysis (took {processing_time:.2f}ms)"
                    )
                    
                    # Convert to AnalysisResponse format
                    from app.models.schemas import CoreBehavior
                    from datetime import datetime
                    
                    core_behaviors = [
                        CoreBehavior(**cb) for cb in previous_analysis.get("core_behaviors", [])
                    ]
                    
                    return AnalysisResponse(
                        user_id=request.user_id,
                        core_behaviors=core_behaviors,
                        total_behaviors_analyzed=previous_analysis.get("total_behaviors_analyzed", len(behaviors)),
                        num_clusters=previous_analysis.get("num_clusters", 0),
                        metadata={
                            **previous_analysis.get("metadata", {}),
                            "from_cache": True,
                            "cache_retrieval_time_ms": round(processing_time, 2)
                        }
                    )
                else:
                    new_behaviors = curr_behavior_ids - prev_behavior_ids
                    removed_behaviors = prev_behavior_ids - curr_behavior_ids
                    logger.info(
                        f"Behavior changes detected for user {request.user_id}: "
                        f"{len(new_behaviors)} new, {len(removed_behaviors)} removed. Re-analyzing..."
                    )
        
        # Step 2: Cluster behaviors
        clustering_service = ClusteringService(
            min_cluster_size=request.min_cluster_size
        )
        clusters, labels = clustering_service.cluster_behaviors(behaviors)
        
        logger.info(f"Created {len(clusters)} clusters")
        
        # Step 3: Load previous analysis for change detection
        previous_analysis = analysis_store.load_previous_analysis(request.user_id)
        
        # Step 4: Derive core behaviors with promotion/rejection logic
        analyzer_service = CoreAnalyzerService()
        core_behaviors, rejection_stats = analyzer_service.derive_core_behaviors(
            user_id=request.user_id,
            behaviors=behaviors,
            clusters=clusters,
            labels=labels
        )
        
        # Step 5: Update versions and timestamps based on previous analysis
        core_behaviors = analyzer_service.update_versions_and_timestamps(
            core_behaviors=core_behaviors,
            previous_analysis=previous_analysis
        )
        
        # Step 6: Calculate behavior status (Active/Degrading/Historical/Retired)
        core_behaviors = analyzer_service.calculate_behavior_status(
            core_behaviors=core_behaviors,
            current_behaviors=behaviors,
            previous_analysis=previous_analysis
        )
        
        # Step 7: Detect changes from previous analysis
        changes_detected = analyzer_service.detect_changes(
            current_core_behaviors=core_behaviors,
            previous_analysis=previous_analysis
        )
        
        # Step 8: Calculate quality metrics
        import numpy as np
        embeddings = np.array([b.embedding for b in behaviors])
        quality_metrics = clustering_service.calculate_quality_metrics(embeddings, labels)
        
        # Build response
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        response = AnalysisResponse(
            user_id=request.user_id,
            core_behaviors=core_behaviors,
            total_behaviors_analyzed=len(behaviors),
            num_clusters=len(clusters),
            metadata={
                "processing_time_ms": round(processing_time, 2),
                "quality_metrics": quality_metrics,
                "clustering_params": {
                    "min_cluster_size": clustering_service.min_cluster_size,
                    "min_samples": clustering_service.min_samples
                },
                "promotion_stats": {
                    "clusters_evaluated": rejection_stats["clusters_evaluated"],
                    "promoted_to_core": rejection_stats["promoted_to_core"],
                    "rejected": rejection_stats["rejected"],
                    "emerging_patterns": rejection_stats["emerging_patterns"],
                    "rejection_reasons": rejection_stats["rejection_reasons"]
                },
                "changes_detected": changes_detected
            }
        )
        
        # Step 9: Save current analysis for future change detection
        analysis_data = {
            "user_id": request.user_id,
            "core_behaviors": [cb.model_dump() for cb in core_behaviors],
            "total_behaviors_analyzed": len(behaviors),
            "num_clusters": len(clusters),
            "analysis_timestamp": response.analysis_timestamp.isoformat()
        }
        analysis_store.save_analysis(request.user_id, analysis_data)
        
        logger.info(
            f"Analysis completed for user {request.user_id} in {processing_time:.2f}ms: "
            f"{len(core_behaviors)} core behaviors identified"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/{user_id}/history", response_model=Dict[str, Any])
async def get_analysis_history(
    user_id: str,
    limit: int = 10,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Retrieve all past analyses for a user.
    
    Args:
        user_id: User ID
        limit: Maximum number of results (default 10)
        offset: Number of results to skip (default 0)
        
    Returns:
        Dictionary with user_id, analyses list, and total_count
    """
    try:
        analyses = analysis_store.list_user_analyses(user_id, limit=limit, offset=offset)
        
        # Get total count (without pagination)
        all_analyses = analysis_store.list_user_analyses(user_id, limit=1000)
        
        return {
            "user_id": user_id,
            "analyses": analyses,
            "total_count": len(all_analyses),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting analysis history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis history: {str(e)}"
        )


@router.get("/{user_id}/latest", response_model=Dict[str, Any])
async def get_latest_analysis(user_id: str) -> Dict[str, Any]:
    """
    Get most recent analysis without re-clustering.
    
    Args:
        user_id: User ID
        
    Returns:
        Cached analysis results
    """
    try:
        analysis = analysis_store.get_latest_analysis(user_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No analysis found for user {user_id}. Run POST /analysis first."
            )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get latest analysis: {str(e)}"
        )


@router.get("/by-id/{analysis_id}", response_model=Dict[str, Any])
async def get_analysis_by_id(analysis_id: str) -> Dict[str, Any]:
    """
    Retrieve specific analysis by ID.
    
    Args:
        analysis_id: Analysis ID (format: user_id_timestamp)
        
    Returns:
        Full analysis JSON
    """
    try:
        analysis = analysis_store.get_analysis_by_id(analysis_id)
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis by ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis: {str(e)}"
        )


@router.get("/{user_id}/stats", response_model=Dict[str, Any])
async def get_analysis_stats(user_id: str) -> Dict[str, Any]:
    """
    Get statistics about user's analysis history.
    
    Args:
        user_id: User ID
        
    Returns:
        Statistics dictionary
    """
    try:
        stats = analysis_store.get_analysis_stats(user_id)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting analysis stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis stats: {str(e)}"
        )


@router.delete("/by-id/{analysis_id}", response_model=Dict[str, Any])
async def delete_analysis_by_id(analysis_id: str) -> Dict[str, Any]:
    """
    Delete specific analysis by ID.
    
    Args:
        analysis_id: Analysis ID to delete
        
    Returns:
        Success message
    """
    try:
        deleted = analysis_store.delete_analysis(analysis_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found"
            )
        
        return {
            "message": f"Analysis {analysis_id} deleted successfully",
            "analysis_id": analysis_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete analysis: {str(e)}"
        )


@router.delete("/{user_id}/all", response_model=Dict[str, Any])
async def delete_all_user_analyses(user_id: str) -> Dict[str, Any]:
    """
    Delete all analyses for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Success message with count
    """
    try:
        count = analysis_store.delete_all_user_analyses(user_id)
        
        return {
            "message": f"Deleted {count} analyses for user {user_id}",
            "user_id": user_id,
            "deleted_count": count
        }
        
    except Exception as e:
        logger.error(f"Error deleting user analyses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user analyses: {str(e)}"
        )


@router.get("/{user_id}/summary", response_model=Dict[str, Any])
async def get_analysis_summary(user_id: str) -> Dict[str, Any]:
    """
    Get a quick summary of user's behavior data without full analysis.
    
    Args:
        user_id: User ID to summarize
        
    Returns:
        Summary statistics
    """
    try:
        vector_service = VectorStoreService()
        behaviors = vector_service.get_behaviors_by_user(user_id)
        
        if not behaviors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No behaviors found for user {user_id}"
            )
        
        # Calculate summary stats
        import numpy as np
        
        summary = {
            "user_id": user_id,
            "total_behaviors": len(behaviors),
            "domains": list(set(b.domain for b in behaviors)),
            "expertise_levels": list(set(b.expertise_level for b in behaviors)),
            "avg_reinforcement_count": float(np.mean([b.reinforcement_count for b in behaviors])),
            "avg_credibility": float(np.mean([b.credibility for b in behaviors])),
            "avg_clarity_score": float(np.mean([b.clarity_score for b in behaviors])),
            "total_prompts": sum(len(b.prompt_history_ids) for b in behaviors)
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )
