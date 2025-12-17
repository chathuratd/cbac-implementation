from pymongo import MongoClient, ASCENDING, DESCENDING
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class AnalysisStore:
    """Store and retrieve analysis results from MongoDB"""
    
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DATABASE]
        self.collection = self.db["analysis_results"]
        
        # Create indexes for performance
        self._create_indexes()
        logger.info(f"AnalysisStore initialized with MongoDB collection: analysis_results")
    
    def _create_indexes(self):
        """Create database indexes for optimal query performance"""
        try:
            # Compound index for user queries
            self.collection.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
            # Unique index for analysis_id
            self.collection.create_index("analysis_id", unique=True)
            # Index for timestamp queries
            self.collection.create_index("timestamp", DESCENDING)
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning (may already exist): {e}")
    
    def save_analysis(self, user_id: str, analysis_result: Dict[str, Any]) -> str:
        """
        Save analysis result to MongoDB.
        
        Args:
            user_id: User ID
            analysis_result: Complete analysis result to save
            
        Returns:
            str: Analysis ID of saved document
        """
        timestamp = datetime.utcnow()
        analysis_id = f"{user_id}_{int(timestamp.timestamp())}"
        
        # Prepare document
        document = {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "saved_at": timestamp.isoformat(),
            "version": "1.0",
            **analysis_result
        }
        
        try:
            # Insert into MongoDB
            self.collection.insert_one(document)
            logger.info(f"Saved analysis {analysis_id} to MongoDB")
            return analysis_id
        except Exception as e:
            logger.error(f"Error saving analysis for user {user_id}: {e}")
            raise
    
    def load_previous_analysis(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load most recent analysis result for user from MongoDB.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict or None if no previous analysis exists
        """
        try:
            # Find most recent analysis for user
            result = self.collection.find_one(
                {"user_id": user_id},
                sort=[("timestamp", DESCENDING)]
            )
            
            if not result:
                logger.debug(f"No previous analysis found for user {user_id}")
                return None
            
            # Remove MongoDB's _id field
            result.pop("_id", None)
            logger.info(f"Loaded previous analysis for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error loading previous analysis for user {user_id}: {e}")
            return None
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete specific analysis by ID from MongoDB.
        
        Args:
            analysis_id: Analysis ID to delete
            
        Returns:
            bool: True if deleted, False if didn't exist
        """
        try:
            result = self.collection.delete_one({"analysis_id": analysis_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted analysis {analysis_id}")
                return True
            else:
                logger.debug(f"Analysis {analysis_id} not found")
                return False
        except Exception as e:
            logger.error(f"Error deleting analysis {analysis_id}: {e}")
            return False
    
    def delete_all_user_analyses(self, user_id: str) -> int:
        """
        Delete all analyses for a user from MongoDB.
        
        Args:
            user_id: User ID
            
        Returns:
            int: Number of analyses deleted
        """
        try:
            result = self.collection.delete_many({"user_id": user_id})
            count = result.deleted_count
            logger.info(f"Deleted {count} analyses for user {user_id}")
            return count
        except Exception as e:
            logger.error(f"Error deleting analyses for user {user_id}: {e}")
            return 0
    
    def get_all_user_ids(self) -> List[str]:
        """
        Get list of all user IDs with stored analyses.
        
        Returns:
            List of unique user IDs
        """
        try:
            user_ids = self.collection.distinct("user_id")
            logger.info(f"Retrieved {len(user_ids)} unique user IDs")
            return user_ids
        except Exception as e:
            logger.error(f"Error getting user IDs: {e}")
            return []
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve specific analysis by ID from MongoDB.
        
        Args:
            analysis_id: Analysis ID (format: user_id_timestamp)
            
        Returns:
            Dict or None if not found
        """
        try:
            result = self.collection.find_one({"analysis_id": analysis_id})
            
            if not result:
                logger.debug(f"Analysis {analysis_id} not found")
                return None
            
            # Remove MongoDB's _id field
            result.pop("_id", None)
            logger.info(f"Loaded analysis {analysis_id}")
            return result
        except Exception as e:
            logger.error(f"Error loading analysis {analysis_id}: {e}")
            return None
    
    def list_user_analyses(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all analyses for a user with pagination from MongoDB.
        
        Args:
            user_id: User ID
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of analysis metadata dictionaries
        """
        try:
            # Query MongoDB with projection for metadata only
            cursor = self.collection.find(
                {"user_id": user_id},
                {
                    "analysis_id": 1,
                    "timestamp": 1,
                    "saved_at": 1,
                    "core_behaviors": 1,
                    "total_behaviors_analyzed": 1,
                    "_id": 0
                }
            ).sort("timestamp", DESCENDING).skip(offset).limit(limit)
            
            analyses = []
            for doc in cursor:
                # Extract metadata
                timestamp_str = doc.get("saved_at", "")
                if not timestamp_str and "timestamp" in doc:
                    timestamp_str = doc["timestamp"].isoformat() if isinstance(doc["timestamp"], datetime) else str(doc["timestamp"])
                
                num_core_behaviors = len(doc.get("core_behaviors", []))
                total_behaviors = doc.get("total_behaviors_analyzed", 0)
                
                analyses.append({
                    "analysis_id": doc.get("analysis_id"),
                    "timestamp": timestamp_str,
                    "num_core_behaviors": num_core_behaviors,
                    "total_behaviors": total_behaviors
                })
            
            logger.info(f"Retrieved {len(analyses)} analyses for user {user_id}")
            return analyses
        except Exception as e:
            logger.error(f"Error listing analyses for user {user_id}: {e}")
            return []
    
    def get_latest_analysis(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get most recent analysis for user (same as load_previous_analysis).
        
        Args:
            user_id: User ID
            
        Returns:
            Dict or None if no analysis exists
        """
        return self.load_previous_analysis(user_id)
    
    def get_analysis_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics about user's analysis history using MongoDB aggregation.
        
        Args:
            user_id: User ID
            
        Returns:
            Statistics dictionary
        """
        try:
            # Use aggregation pipeline for efficient statistics
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$project": {
                    "timestamp": 1,
                    "num_core_behaviors": {"$size": {"$ifNull": ["$core_behaviors", []]}},
                    "total_behaviors": "$total_behaviors_analyzed"
                }},
                {"$group": {
                    "_id": "$user_id",
                    "total_analyses": {"$sum": 1},
                    "first_analysis": {"$min": "$timestamp"},
                    "last_analysis": {"$max": "$timestamp"},
                    "avg_core_behaviors": {"$avg": "$num_core_behaviors"},
                    "avg_total_behaviors": {"$avg": "$total_behaviors"},
                    "min_core_behaviors": {"$min": "$num_core_behaviors"},
                    "max_core_behaviors": {"$max": "$num_core_behaviors"}
                }}
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if not result:
                return {
                    "user_id": user_id,
                    "total_analyses": 0,
                    "first_analysis": None,
                    "last_analysis": None,
                    "avg_core_behaviors": 0,
                    "avg_total_behaviors": 0,
                    "min_core_behaviors": 0,
                    "max_core_behaviors": 0
                }
            
            stats = result[0]
            return {
                "user_id": user_id,
                "total_analyses": stats.get("total_analyses", 0),
                "first_analysis": stats.get("first_analysis").isoformat() if stats.get("first_analysis") else None,
                "last_analysis": stats.get("last_analysis").isoformat() if stats.get("last_analysis") else None,
                "avg_core_behaviors": round(stats.get("avg_core_behaviors", 0), 2),
                "avg_total_behaviors": round(stats.get("avg_total_behaviors", 0), 2),
                "min_core_behaviors": stats.get("min_core_behaviors", 0),
                "max_core_behaviors": stats.get("max_core_behaviors", 0)
            }
        except Exception as e:
            logger.error(f"Error getting analysis stats for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "total_analyses": 0,
                "first_analysis": None,
                "last_analysis": None,
                "avg_core_behaviors": 0,
                "avg_total_behaviors": 0,
                "min_core_behaviors": 0,
                "max_core_behaviors": 0
            }
    
    def check_connection(self) -> bool:
        """Check if MongoDB is accessible"""
        try:
            self.client.server_info()
            return True
        except Exception as e:
            logger.error(f"MongoDB connection check failed: {e}")
            return False
