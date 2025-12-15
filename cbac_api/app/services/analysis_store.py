import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AnalysisStore:
    """Store and retrieve analysis results for change detection"""
    
    def __init__(self, storage_dir: str = "./analysis_results"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"AnalysisStore initialized at {self.storage_dir}")
    
    def save_analysis(self, user_id: str, analysis_result: Dict[str, Any]) -> str:
        """
        Save analysis result to disk.
        
        Args:
            user_id: User ID
            analysis_result: Complete analysis result to save
            
        Returns:
            str: Path to saved file
        """
        timestamp = datetime.utcnow().isoformat()
        filename = f"{user_id}_latest.json"
        filepath = self.storage_dir / filename
        
        # Add metadata
        analysis_result["saved_at"] = timestamp
        analysis_result["user_id"] = user_id
        
        # Save to file
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis_result, f, indent=2)
            logger.info(f"Saved analysis for user {user_id} to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error saving analysis for user {user_id}: {e}")
            raise
    
    def load_previous_analysis(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load previous analysis result for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict or None if no previous analysis exists
        """
        filename = f"{user_id}_latest.json"
        filepath = self.storage_dir / filename
        
        if not filepath.exists():
            logger.debug(f"No previous analysis found for user {user_id}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                result = json.load(f)
            logger.info(f"Loaded previous analysis for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error loading previous analysis for user {user_id}: {e}")
            return None
    
    def delete_analysis(self, user_id: str) -> bool:
        """
        Delete analysis result for user.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if deleted, False if didn't exist
        """
        filename = f"{user_id}_latest.json"
        filepath = self.storage_dir / filename
        
        if filepath.exists():
            try:
                filepath.unlink()
                logger.info(f"Deleted analysis for user {user_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting analysis for user {user_id}: {e}")
                return False
        
        logger.debug(f"No analysis to delete for user {user_id}")
        return False
    
    def get_all_user_ids(self) -> List[str]:
        """
        Get list of all user IDs with stored analyses.
        
        Returns:
            List of user IDs
        """
        user_ids = []
        for filepath in self.storage_dir.glob("*_latest.json"):
            user_id = filepath.stem.replace("_latest", "")
            user_ids.append(user_id)
        return user_ids
