import numpy as np
from typing import List, Dict, Any
from collections import Counter
from app.models.schemas import Behavior, Cluster, CoreBehavior
import logging
import uuid

logger = logging.getLogger(__name__)


class CoreAnalyzerService:
    """Service for deriving core behaviors from clusters"""
    
    def derive_core_behaviors(
        self,
        user_id: str,
        behaviors: List[Behavior],
        clusters: List[Cluster],
        labels: np.ndarray
    ) -> List[CoreBehavior]:
        """
        Derive generalized core behaviors from behavior clusters.
        
        Args:
            user_id: User ID
            behaviors: Original behavior objects
            clusters: Cluster objects from clustering
            labels: Cluster assignment labels
            
        Returns:
            List of CoreBehavior objects
        """
        core_behaviors = []
        
        for cluster in clusters:
            # Get behaviors in this cluster
            cluster_behaviors = [
                b for b in behaviors
                if b.behavior_id in cluster.behavior_ids
            ]
            
            # Derive generalized statement
            generalized_statement = self._generate_generalized_statement(
                cluster_behaviors,
                cluster
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                cluster_behaviors,
                cluster
            )
            
            # Detect domain (from ground truth labels)
            domain_detected = self._detect_domain(cluster_behaviors)
            
            # Build metadata
            metadata = {
                "cluster_size": cluster.size,
                "coherence_score": cluster.coherence_score,
                "avg_reinforcement_count": np.mean([b.reinforcement_count for b in cluster_behaviors]),
                "avg_credibility": np.mean([b.credibility for b in cluster_behaviors]),
                "avg_clarity_score": np.mean([b.clarity_score for b in cluster_behaviors]),
            }
            
            core_behavior = CoreBehavior(
                core_behavior_id=f"core_{user_id}_{cluster.cluster_id}_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                generalized_statement=generalized_statement,
                confidence_score=confidence_score,
                evidence_chain=cluster.behavior_ids,
                cluster_id=cluster.cluster_id,
                domain_detected=domain_detected,
                metadata=metadata
            )
            
            core_behaviors.append(core_behavior)
        
        logger.info(f"Derived {len(core_behaviors)} core behaviors for user {user_id}")
        return core_behaviors
    
    def _generate_generalized_statement(
        self,
        behaviors: List[Behavior],
        cluster: Cluster
    ) -> str:
        """
        Generate a generalized statement from cluster behaviors.
        
        For Phase 1, using template-based generation.
        Phase 2 will use LLM-based generation.
        
        Args:
            behaviors: Behaviors in the cluster
            cluster: Cluster object
            
        Returns:
            Generalized statement string
        """
        # Extract common patterns
        domains = [b.domain for b in behaviors]
        domain_counts = Counter(domains)
        primary_domain = domain_counts.most_common(1)[0][0] if domain_counts else "general"
        
        expertise_levels = [b.expertise_level for b in behaviors]
        expertise_counts = Counter(expertise_levels)
        primary_expertise = expertise_counts.most_common(1)[0][0] if expertise_counts else "intermediate"
        
        # Count key indicators
        avg_clarity = np.mean([b.clarity_score for b in behaviors])
        avg_reinforcement = np.mean([b.reinforcement_count for b in behaviors])
        
        # Template-based generation
        if avg_clarity > 0.7 and avg_reinforcement > 3:
            pattern = "demonstrates deep and iterative engagement"
        elif avg_reinforcement > 3:
            pattern = "shows consistent follow-up behavior"
        elif avg_clarity > 0.7:
            pattern = "exhibits high-clarity understanding"
        else:
            pattern = "displays regular interest"
        
        statement = (
            f"User {pattern} in {primary_domain} at {primary_expertise} level "
            f"(based on {len(behaviors)} related behaviors)"
        )
        
        return statement
    
    def _calculate_confidence_score(
        self,
        behaviors: List[Behavior],
        cluster: Cluster
    ) -> float:
        """
        Calculate confidence score for the core behavior.
        
        Factors:
        - Cluster coherence (how tightly behaviors are grouped)
        - Cluster size (more evidence = higher confidence)
        - Average response quality
        - Interaction consistency
        
        Args:
            behaviors: Behaviors in the cluster
            cluster: Cluster object
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Component 1: Cluster coherence (from clustering)
        coherence_weight = 0.3
        coherence_score = cluster.coherence_score
        
        # Component 2: Evidence strength (normalized cluster size)
        evidence_weight = 0.3
        # Assume 10+ behaviors is "strong evidence" (score = 1.0)
        evidence_score = min(1.0, cluster.size / 10.0)
        
        # Component 3: Average credibility
        quality_weight = 0.2
        avg_credibility = np.mean([b.credibility for b in behaviors])
        
        # Component 4: Reinforcement consistency (low variance = high consistency)
        consistency_weight = 0.2
        reinforcement_counts = [b.reinforcement_count for b in behaviors]
        if len(reinforcement_counts) > 1:
            consistency_score = 1.0 - min(1.0, np.std(reinforcement_counts) / np.mean(reinforcement_counts))
        else:
            consistency_score = 1.0
        
        # Weighted combination
        confidence = (
            coherence_weight * coherence_score +
            evidence_weight * evidence_score +
            quality_weight * avg_credibility +
            consistency_weight * consistency_score
        )
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def _detect_domain(self, behaviors: List[Behavior]) -> str:
        """
        Detect the primary domain from behavior labels.
        
        Args:
            behaviors: Behaviors in the cluster
            
        Returns:
            Detected domain string
        """
        domains = [b.domain for b in behaviors]
        domain_counts = Counter(domains)
        
        if not domain_counts:
            return "unknown"
        
        primary_domain, count = domain_counts.most_common(1)[0]
        
        # If domain is not consistent (< 70% agreement), mark as mixed
        if count / len(behaviors) < 0.7:
            return f"mixed_{primary_domain}"
        
        return primary_domain
