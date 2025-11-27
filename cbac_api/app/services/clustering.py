import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from typing import List, Tuple, Dict, Any
from app.config.settings import settings
from app.models.schemas import Behavior, Cluster
import logging

logger = logging.getLogger(__name__)


class ClusteringService:
    """Service for semantic clustering of behaviors using DBSCAN"""
    
    def __init__(
        self,
        min_cluster_size: int = None,
        min_samples: int = None,
        cluster_selection_epsilon: float = None
    ):
        self.min_cluster_size = min_cluster_size or settings.MIN_CLUSTER_SIZE
        self.min_samples = min_samples or settings.MIN_SAMPLES
        self.eps = cluster_selection_epsilon or 0.5  # DBSCAN epsilon parameter
        
    def cluster_behaviors(self, behaviors: List[Behavior]) -> Tuple[List[Cluster], np.ndarray]:
        """
        Cluster behaviors based on their embeddings using HDBSCAN.
        
        Args:
            behaviors: List of Behavior objects with embeddings
            
        Returns:
            Tuple of (List of Cluster objects, cluster labels array)
        """
        if not behaviors:
            logger.warning("No behaviors to cluster")
            return [], np.array([])
        
        # Extract embeddings
        embeddings = np.array([b.embedding for b in behaviors])
        
        if len(embeddings) < self.min_cluster_size:
            logger.warning(
                f"Too few behaviors ({len(embeddings)}) for clustering "
                f"(min_cluster_size={self.min_cluster_size}). Creating single cluster."
            )
            # Put all in one cluster
            labels = np.zeros(len(embeddings), dtype=int)
        else:
            # Perform DBSCAN clustering
            clusterer = DBSCAN(
                eps=self.eps,
                min_samples=self.min_samples,
                metric='euclidean'
            )
            labels = clusterer.fit_predict(embeddings)
        
        # Build cluster objects
        clusters = self._build_clusters(behaviors, labels, embeddings)
        
        logger.info(
            f"Clustered {len(behaviors)} behaviors into {len(clusters)} clusters "
            f"({np.sum(labels == -1)} noise points)"
        )
        
        return clusters, labels
    
    def _build_clusters(
        self,
        behaviors: List[Behavior],
        labels: np.ndarray,
        embeddings: np.ndarray
    ) -> List[Cluster]:
        """
        Build Cluster objects from clustering results.
        
        Args:
            behaviors: Original behavior objects
            labels: Cluster assignment labels
            embeddings: Behavior embeddings
            
        Returns:
            List of Cluster objects
        """
        clusters = []
        unique_labels = set(labels)
        
        for cluster_id in unique_labels:
            if cluster_id == -1:  # Skip noise points
                continue
            
            # Get behaviors in this cluster
            cluster_mask = labels == cluster_id
            cluster_behavior_indices = np.where(cluster_mask)[0]
            cluster_behaviors = [behaviors[i] for i in cluster_behavior_indices]
            cluster_embeddings = embeddings[cluster_mask]
            
            # Calculate centroid
            centroid = np.mean(cluster_embeddings, axis=0).tolist()
            
            # Calculate coherence score (using average distance to centroid)
            distances = np.linalg.norm(
                cluster_embeddings - np.array(centroid),
                axis=1
            )
            coherence_score = float(1.0 / (1.0 + np.mean(distances)))
            
            # Select representative behaviors (closest to centroid)
            num_representatives = min(3, len(cluster_behaviors))
            closest_indices = np.argsort(distances)[:num_representatives]
            representative_texts = [
                cluster_behaviors[i].behavior_text
                for i in closest_indices
            ]
            
            cluster = Cluster(
                cluster_id=int(cluster_id),
                behavior_ids=[b.behavior_id for b in cluster_behaviors],
                centroid=centroid,
                size=len(cluster_behaviors),
                coherence_score=coherence_score,
                representative_behaviors=representative_texts
            )
            clusters.append(cluster)
        
        return clusters
    
    def calculate_quality_metrics(
        self,
        embeddings: np.ndarray,
        labels: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate clustering quality metrics.
        
        Args:
            embeddings: Behavior embeddings
            labels: Cluster labels
            
        Returns:
            Dictionary of quality metrics
        """
        metrics = {}
        
        # Filter out noise points for silhouette score
        valid_mask = labels != -1
        if np.sum(valid_mask) > 1 and len(set(labels[valid_mask])) > 1:
            try:
                silhouette = silhouette_score(
                    embeddings[valid_mask],
                    labels[valid_mask]
                )
                metrics["silhouette_score"] = float(silhouette)
            except Exception as e:
                logger.warning(f"Could not calculate silhouette score: {e}")
                metrics["silhouette_score"] = 0.0
        else:
            metrics["silhouette_score"] = 0.0
        
        # Noise ratio
        noise_ratio = float(np.sum(labels == -1) / len(labels))
        metrics["noise_ratio"] = noise_ratio
        
        # Number of clusters
        metrics["num_clusters"] = int(len(set(labels)) - (1 if -1 in labels else 0))
        
        return metrics
