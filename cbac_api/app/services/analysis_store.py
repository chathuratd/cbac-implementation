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
            str: Analysis ID of saved file
        """
        timestamp = int(datetime.utcnow().timestamp())
        analysis_id = f"{user_id}_{timestamp}"
        
        # Add metadata
        analysis_result["saved_at"] = datetime.utcnow().isoformat()
        analysis_result["user_id"] = user_id
        analysis_result["analysis_id"] = analysis_id
        analysis_result["version"] = "1.0"
        
        # Save with timestamp
        timestamped_filename = f"{analysis_id}.json"
        timestamped_filepath = self.storage_dir / timestamped_filename
        
        # Also save as latest
        latest_filename = f"{user_id}_latest.json"
        latest_filepath = self.storage_dir / latest_filename
        
        # Save to both files
        try:
            with open(timestamped_filepath, 'w') as f:
                json.dump(analysis_result, f, indent=2)
            with open(latest_filepath, 'w') as f:
                json.dump(analysis_result, f, indent=2)
            logger.info(f"Saved analysis {analysis_id} to {timestamped_filepath} and {latest_filepath}")
            return analysis_id
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
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve specific analysis by ID.
        
        Args:
            analysis_id: Analysis ID (format: user_id_timestamp)
            
        Returns:
            Dict or None if not found
        """
        filepath = self.storage_dir / f"{analysis_id}.json"
        
        if not filepath.exists():
            logger.debug(f"Analysis {analysis_id} not found")
            return None
        
        try:
            with open(filepath, 'r') as f:
                result = json.load(f)
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
        List all analyses for a user with pagination.
        
        Args:
            user_id: User ID
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of analysis metadata dictionaries
        """
        analyses = []
        
        # Find all analysis files for this user
        pattern = f"{user_id}_*.json"
        for filepath in self.storage_dir.glob(pattern):
            # Skip the _latest.json file as it's a duplicate
            if filepath.stem.endswith("_latest"):
                continue
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Extract metadata
                analysis_id = data.get("analysis_id", filepath.stem)
                timestamp_str = data.get("saved_at", "")
                
                # Parse timestamp from analysis_id if not in data
                if not timestamp_str and "_" in analysis_id:
                    try:
                        ts = int(analysis_id.split("_")[-1])
                        timestamp_str = datetime.fromtimestamp(ts).isoformat()
                    except:
                        pass
                
                num_core_behaviors = len(data.get("core_behaviors", []))
                total_behaviors = data.get("total_behaviors_analyzed", 0)
                
                analyses.append({
                    "analysis_id": analysis_id,
                    "timestamp": timestamp_str,
                    "num_core_behaviors": num_core_behaviors,
                    "total_behaviors": total_behaviors
                })
            except Exception as e:
                logger.warning(f"Error reading analysis file {filepath}: {e}")
                continue
        
        # Sort by timestamp (newest first)
        analyses.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        return analyses[offset:offset + limit]
    
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
        Get statistics about user's analysis history.
        
        Args:
            user_id: User ID
            
        Returns:
            Statistics dictionary
        """
        analyses = self.list_user_analyses(user_id, limit=1000)  # Get all
        
        if not analyses:
            return {
                "user_id": user_id,
                "total_analyses": 0,
                "first_analysis": None,
                "last_analysis": None,
                "avg_core_behaviors": 0,
                "avg_total_behaviors": 0
            }
        
        timestamps = [a["timestamp"] for a in analyses if a["timestamp"]]
        core_behavior_counts = [a["num_core_behaviors"] for a in analyses]
        total_behavior_counts = [a["total_behaviors"] for a in analyses]
        
        return {
            "user_id": user_id,
            "total_analyses": len(analyses),
            "first_analysis": min(timestamps) if timestamps else None,
            "last_analysis": max(timestamps) if timestamps else None,
            "avg_core_behaviors": sum(core_behavior_counts) / len(core_behavior_counts) if core_behavior_counts else 0,
            "avg_total_behaviors": sum(total_behavior_counts) / len(total_behavior_counts) if total_behavior_counts else 0,
            "min_core_behaviors": min(core_behavior_counts) if core_behavior_counts else 0,
            "max_core_behaviors": max(core_behavior_counts) if core_behavior_counts else 0
        }
