from pymongo import MongoClient
from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.models.schemas import Prompt
import logging

logger = logging.getLogger(__name__)


class DocumentStoreService:
    """Service for querying MongoDB document database"""
    
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DATABASE]
        self.prompts_collection = self.db[settings.MONGODB_COLLECTION_PROMPTS]
        self.behaviors_collection = self.db[settings.MONGODB_COLLECTION_BEHAVIORS]
        
    def get_prompts_by_ids(self, prompt_ids: List[str]) -> List[Prompt]:
        """
        Fetch prompts by their IDs from MongoDB.
        
        Args:
            prompt_ids: List of prompt IDs to fetch
            
        Returns:
            List of Prompt objects
        """
        try:
            # Query MongoDB for prompts with matching IDs
            cursor = self.prompts_collection.find(
                {"prompt_id": {"$in": prompt_ids}}
            )
            
            prompts = []
            for doc in cursor:
                # Remove MongoDB's _id field
                doc.pop("_id", None)
                prompt = Prompt(**doc)
                prompts.append(prompt)
            
            logger.info(f"Retrieved {len(prompts)} prompts out of {len(prompt_ids)} requested")
            return prompts
            
        except Exception as e:
            logger.error(f"Error fetching prompts: {e}")
            raise
    
    def get_prompts_by_user(self, user_id: str) -> List[Prompt]:
        """
        Fetch all prompts for a specific user from MongoDB.
        
        Args:
            user_id: The user ID to filter prompts
            
        Returns:
            List of Prompt objects
        """
        try:
            cursor = self.prompts_collection.find({"user_id": user_id})
            
            prompts = []
            for doc in cursor:
                doc.pop("_id", None)
                prompt = Prompt(**doc)
                prompts.append(prompt)
            
            logger.info(f"Retrieved {len(prompts)} prompts for user {user_id}")
            return prompts
            
        except Exception as e:
            logger.error(f"Error fetching prompts for user {user_id}: {e}")
            raise
    
    def check_connection(self) -> bool:
        """Check if MongoDB is accessible"""
        try:
            self.client.server_info()
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False
    
    def get_behaviors_by_ids(self, behavior_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch behaviors by their IDs from MongoDB.
        
        Args:
            behavior_ids: List of behavior IDs to fetch
            
        Returns:
            List of behavior dictionaries with behavior_text and metadata
        """
        try:
            # Query MongoDB for behaviors with matching IDs
            cursor = self.behaviors_collection.find(
                {"behavior_id": {"$in": behavior_ids}}
            )
            
            behaviors = []
            for doc in cursor:
                # Remove MongoDB's _id field
                doc.pop("_id", None)
                behaviors.append(doc)
            
            logger.info(f"Retrieved {len(behaviors)} behaviors out of {len(behavior_ids)} requested")
            return behaviors
            
        except Exception as e:
            logger.error(f"Error fetching behaviors: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the prompts collection"""
        try:
            stats = self.db.command("collStats", settings.MONGODB_COLLECTION_PROMPTS)
            return {
                "collection_name": settings.MONGODB_COLLECTION_PROMPTS,
                "count": stats.get("count", 0),
                "size": stats.get("size", 0),
                "avg_obj_size": stats.get("avgObjSize", 0)
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}
