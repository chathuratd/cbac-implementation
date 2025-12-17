from fastapi import APIRouter, status
from typing import Dict, Any
from app.models.schemas import HealthResponse
from app.services.vector_store import VectorStoreService
from app.services.document_store import DocumentStoreService
from app.services.analysis_store import AnalysisStore
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """
    Health check endpoint - verify system status and database connections.
    
    Returns:
        HealthResponse with overall status and dependency status
    """
    dependencies = {}
    overall_status = "healthy"
    
    # Check Qdrant connection
    try:
        vector_service = VectorStoreService()
        qdrant_ok = vector_service.check_connection()
        dependencies["qdrant"] = "connected" if qdrant_ok else "disconnected"
        if not qdrant_ok:
            overall_status = "degraded"
    except Exception as e:
        dependencies["qdrant"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    # Check MongoDB connection
    try:
        doc_service = DocumentStoreService()
        mongo_ok = doc_service.check_connection()
        dependencies["mongodb"] = "connected" if mongo_ok else "disconnected"
        if not mongo_ok:
            overall_status = "degraded"
    except Exception as e:
        dependencies["mongodb"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    # Check Analysis Store (MongoDB)
    try:
        analysis_store = AnalysisStore()
        analysis_ok = analysis_store.check_connection()
        dependencies["analysis_store"] = "connected" if analysis_ok else "disconnected"
        if not analysis_ok:
            overall_status = "degraded"
    except Exception as e:
        dependencies["analysis_store"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    response = HealthResponse(
        status=overall_status,
        version="0.2.0",
        dependencies=dependencies,
        timestamp=datetime.utcnow()
    )
    
    return response


@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics() -> Dict[str, Any]:
    """
    Get system metrics and statistics.
    
    Returns:
        Dictionary with database statistics and system metrics
    """
    metrics = {}
    
    # Qdrant metrics
    try:
        vector_service = VectorStoreService()
        qdrant_info = vector_service.get_collection_info()
        metrics["qdrant"] = qdrant_info
    except Exception as e:
        metrics["qdrant"] = {"error": str(e)}
    
    # MongoDB metrics
    try:
        doc_service = DocumentStoreService()
        mongo_stats = doc_service.get_collection_stats()
        metrics["mongodb"] = mongo_stats
    except Exception as e:
        metrics["mongodb"] = {"error": str(e)}
    
    # Analysis Store metrics
    try:
        analysis_store = AnalysisStore()
        user_ids = analysis_store.get_all_user_ids()
        total_analyses = analysis_store.collection.count_documents({})
        metrics["analysis_store"] = {
            "total_analyses": total_analyses,
            "unique_users": len(user_ids),
            "collection": "analysis_results"
        }
    except Exception as e:
        metrics["analysis_store"] = {"error": str(e)}
    
    return metrics


@router.get("/status/{component}")
async def get_component_status(component: str) -> Dict[str, Any]:
    """
    Get detailed status for a specific component.
    
    Args:
        component: Component name ("qdrant", "mongodb")
        
    Returns:
        Detailed component status
    """
    if component.lower() == "qdrant":
        try:
            vector_service = VectorStoreService()
            info = vector_service.get_collection_info()
            return {
                "component": "qdrant",
                "status": "operational",
                "details": info
            }
        except Exception as e:
            return {
                "component": "qdrant",
                "status": "error",
                "error": str(e)
            }
    
    elif component.lower() == "mongodb":
        try:
            doc_service = DocumentStoreService()
            stats = doc_service.get_collection_stats()
            return {
                "component": "mongodb",
                "status": "operational",
                "details": stats
            }
        except Exception as e:
            return {
                "component": "mongodb",
                "status": "error",
                "error": str(e)
            }
    
    else:
        return {
            "component": component,
            "status": "unknown",
            "error": "Component not found"
        }
