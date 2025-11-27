from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List, Dict, Any
from app.config.settings import settings
from app.models.schemas import Behavior
import logging

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for querying Qdrant vector database"""
    
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION
        
    def get_behaviors_by_user(self, user_id: str) -> List[Behavior]:
        """
        Fetch all behaviors for a specific user from Qdrant.
        Returns behaviors with embeddings already computed.
        
        Args:
            user_id: The user ID to filter behaviors
            
        Returns:
            List of Behavior objects with embeddings
        """
        try:
            # Query Qdrant with filter on user_id payload field
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                ),
                limit=1000,  # Adjust based on expected max behaviors per user
                with_payload=True,
                with_vectors=True
            )
            
            behaviors = []
            for point in results[0]:  # results is tuple (points, next_page_offset)
                # Extract payload and vector
                payload = point.payload
                vector = point.vector
                
                # Create Behavior object
                behavior = Behavior(
                    **payload,
                    embedding=vector
                )
                behaviors.append(behavior)
            
            logger.info(f"Retrieved {len(behaviors)} behaviors for user {user_id}")
            return behaviors
            
        except Exception as e:
            logger.error(f"Error fetching behaviors for user {user_id}: {e}")
            raise
    
    def check_connection(self) -> bool:
        """Check if Qdrant is accessible"""
        try:
            collections = self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant connection failed: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)}
