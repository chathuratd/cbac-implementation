from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
import time
from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.services.vector_store import VectorStoreService
from app.services.document_store import DocumentStoreService
from app.services.clustering import ClusteringService
from app.services.core_analyzer import CoreAnalyzerService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_user_behaviors(request: AnalysisRequest) -> AnalysisResponse:
    """
    Main endpoint: Analyze user behaviors and derive core behavioral patterns.
    
    Process:
    1. Fetch behaviors from Qdrant (with embeddings)
    2. Cluster behaviors semantically using HDBSCAN
    3. Derive generalized core behaviors from clusters
    4. Return core behaviors with confidence scores and evidence chains
    
    Args:
        request: AnalysisRequest with user_id and optional parameters
        
    Returns:
        AnalysisResponse with derived core behaviors
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting analysis for user: {request.user_id}")
        
        # Step 1: Fetch behaviors from Qdrant
        vector_service = VectorStoreService()
        behaviors = vector_service.get_behaviors_by_user(request.user_id)
        
        if not behaviors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No behaviors found for user {request.user_id}"
            )
        
        logger.info(f"Fetched {len(behaviors)} behaviors")
        
        # Step 2: Cluster behaviors
        clustering_service = ClusteringService(
            min_cluster_size=request.min_cluster_size
        )
        clusters, labels = clustering_service.cluster_behaviors(behaviors)
        
        logger.info(f"Created {len(clusters)} clusters")
        
        # Step 3: Derive core behaviors with promotion/rejection logic
        analyzer_service = CoreAnalyzerService()
        core_behaviors, rejection_stats = analyzer_service.derive_core_behaviors(
            user_id=request.user_id,
            behaviors=behaviors,
            clusters=clusters,
            labels=labels
        )
        
        # Step 4: Calculate quality metrics
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
                }
            }
        )
        
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
