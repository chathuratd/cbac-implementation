import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter
from app.models.schemas import Behavior, Cluster, CoreBehavior
import logging
import uuid
import math
import time

logger = logging.getLogger(__name__)


class CoreAnalyzerService:
    """Service for deriving core behaviors from clusters"""
    
    # Promotion/Rejection Thresholds (from design document)
    MIN_CLUSTER_SIZE = 3
    MIN_CREDIBILITY = 0.65
    MIN_STABILITY = 0.5
    MIN_COHERENCE = 0.7
    MIN_PROMOTION_CONFIDENCE = 0.70
    
    def derive_core_behaviors(
        self,
        user_id: str,
        behaviors: List[Behavior],
        clusters: List[Cluster],
        labels: np.ndarray
    ) -> Tuple[List[CoreBehavior], Dict[str, Any]]:
        """
        Derive generalized core behaviors from behavior clusters with promotion/rejection logic.
        
        Implements Pipeline A rejection criteria:
        - Cluster size >= MIN_CLUSTER_SIZE
        - Average credibility >= MIN_CREDIBILITY
        - Temporal stability >= MIN_STABILITY
        - Coherence >= MIN_COHERENCE
        - Confidence score >= MIN_PROMOTION_CONFIDENCE
        
        Args:
            user_id: User ID
            behaviors: Original behavior objects
            clusters: Cluster objects from clustering
            labels: Cluster assignment labels
            
        Returns:
            Tuple of (List[CoreBehavior], rejection_stats_dict)
        """
        core_behaviors = []
        rejection_stats = {
            "clusters_evaluated": len(clusters),
            "promoted_to_core": 0,
            "rejected": 0,
            "emerging_patterns": 0,
            "rejection_reasons": {}
        }
        
        for cluster in clusters:
            # Get behaviors in this cluster
            cluster_behaviors = [
                b for b in behaviors
                if b.behavior_id in cluster.behavior_ids
            ]
            
            # Evaluate for promotion
            should_promote, reasons = self._evaluate_cluster_for_promotion(
                cluster_behaviors,
                cluster
            )
            
            if not should_promote:
                rejection_stats["rejected"] += 1
                for reason in reasons:
                    rejection_stats["rejection_reasons"][reason] = \
                        rejection_stats["rejection_reasons"].get(reason, 0) + 1
                
                # Check if emerging pattern (close to threshold)
                confidence_score = self._calculate_confidence_score(cluster_behaviors, cluster)
                if confidence_score >= 0.55:  # Emerging threshold
                    rejection_stats["emerging_patterns"] += 1
                    
                logger.debug(f"Cluster {cluster.cluster_id} rejected: {', '.join(reasons)}")
                continue
            
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
            
            # Assign confidence grade
            confidence_grade = self._assign_confidence_grade(
                confidence_score,
                cluster_behaviors,
                cluster
            )
            
            # Calculate temporal stability
            stability_score = self._calculate_temporal_stability(cluster_behaviors)
            
            # Detect domain (from ground truth labels)
            domain_detected = self._detect_domain(cluster_behaviors)
            
            # Build metadata
            metadata = {
                "cluster_size": cluster.size,
                "coherence_score": cluster.coherence_score,
                "avg_reinforcement_count": np.mean([b.reinforcement_count for b in cluster_behaviors]),
                "avg_credibility": np.mean([b.credibility for b in cluster_behaviors]),
                "avg_clarity_score": np.mean([b.clarity_score for b in cluster_behaviors]),
                "temporal_stability": stability_score,
            }
            
            current_time = int(time.time())
            
            core_behavior = CoreBehavior(
                core_behavior_id=f"core_{user_id}_{cluster.cluster_id}_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                generalized_statement=generalized_statement,
                confidence_score=confidence_score,
                confidence_grade=confidence_grade,
                status="Active",
                stability_score=stability_score,
                version=1,
                created_at=current_time,
                last_updated=current_time,
                evidence_chain=cluster.behavior_ids,
                cluster_id=cluster.cluster_id,
                domain_detected=domain_detected,
                metadata=metadata
            )
            
            core_behaviors.append(core_behavior)
            rejection_stats["promoted_to_core"] += 1
        
        logger.info(
            f"Derived {len(core_behaviors)} core behaviors for user {user_id} "
            f"({rejection_stats['rejected']} rejected, {rejection_stats['emerging_patterns']} emerging)"
        )
        return core_behaviors, rejection_stats
    
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
        Calculate confidence score for the core behavior using design spec formula.
        
        Formula: 0.35*credibility + 0.25*stability + 0.25*coherence + 0.15*reinforcement_depth
        
        Args:
            behaviors: Behaviors in the cluster
            cluster: Cluster object
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Component 1: Weighted average credibility (35%)
        credibility_component = self._calculate_weighted_credibility(behaviors)
        
        # Component 2: Temporal stability (25%)
        stability_component = self._calculate_temporal_stability(behaviors)
        
        # Component 3: Cluster coherence (25%)
        coherence_component = cluster.coherence_score
        
        # Component 4: Reinforcement depth - logarithmic scale (15%)
        reinforcement_component = self._calculate_reinforcement_depth(behaviors)
        
        # Weighted combination per design spec
        confidence = (
            0.35 * credibility_component +
            0.25 * stability_component +
            0.25 * coherence_component +
            0.15 * reinforcement_component
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
    
    def _evaluate_cluster_for_promotion(
        self,
        behaviors: List[Behavior],
        cluster: Cluster
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate whether a cluster should be promoted to core behavior.
        
        Implements Pipeline A rejection criteria from design document.
        
        Args:
            behaviors: Behaviors in the cluster
            cluster: Cluster object
            
        Returns:
            Tuple of (should_promote: bool, rejection_reasons: List[str])
        """
        rejection_reasons = []
        
        # Check 1: Cluster size
        if cluster.size < self.MIN_CLUSTER_SIZE:
            rejection_reasons.append(f"cluster_size_too_small ({cluster.size} < {self.MIN_CLUSTER_SIZE})")
        
        # Check 2: Average credibility
        avg_credibility = self._calculate_weighted_credibility(behaviors)
        if avg_credibility < self.MIN_CREDIBILITY:
            rejection_reasons.append(f"low_credibility ({avg_credibility:.2f} < {self.MIN_CREDIBILITY})")
        
        # Check 3: Temporal stability
        temporal_stability = self._calculate_temporal_stability(behaviors)
        if temporal_stability < self.MIN_STABILITY:
            rejection_reasons.append(f"low_stability ({temporal_stability:.2f} < {self.MIN_STABILITY})")
        
        # Check 4: Coherence
        if cluster.coherence_score < self.MIN_COHERENCE:
            rejection_reasons.append(f"low_coherence ({cluster.coherence_score:.2f} < {self.MIN_COHERENCE})")
        
        # Check 5: Overall confidence score
        confidence_score = self._calculate_confidence_score(behaviors, cluster)
        if confidence_score < self.MIN_PROMOTION_CONFIDENCE:
            rejection_reasons.append(f"low_confidence ({confidence_score:.2f} < {self.MIN_PROMOTION_CONFIDENCE})")
        
        should_promote = len(rejection_reasons) == 0
        return should_promote, rejection_reasons
    
    def _calculate_weighted_credibility(self, behaviors: List[Behavior]) -> float:
        """
        Calculate weighted average credibility based on reinforcement count.
        
        More reinforced behaviors should have higher weight in credibility calculation.
        
        Args:
            behaviors: Behaviors in the cluster
            
        Returns:
            Weighted average credibility (0.0 to 1.0)
        """
        if not behaviors:
            return 0.0
        
        total_weight = sum(b.reinforcement_count for b in behaviors)
        if total_weight == 0:
            # Fallback to simple average if no reinforcements
            return float(np.mean([b.credibility for b in behaviors]))
        
        weighted_sum = sum(b.credibility * b.reinforcement_count for b in behaviors)
        return float(weighted_sum / total_weight)
    
    def _calculate_temporal_stability(self, behaviors: List[Behavior]) -> float:
        """
        Calculate temporal stability based on variance in observation timestamps.
        
        Low variance = high stability (behaviors occur consistently over time)
        High variance = low stability (sporadic behaviors)
        
        Args:
            behaviors: Behaviors in the cluster
            
        Returns:
            Stability score (0.0 to 1.0)
        """
        if len(behaviors) < 2:
            return 1.0  # Single observation assumed stable
        
        timestamps = [b.timestamp for b in behaviors]
        
        # Calculate time variance
        time_variance = np.var(timestamps)
        
        # Normalize: lower variance = higher stability
        # Use exponential decay to map variance to [0, 1]
        # Assume variance of 1e10 (large time gaps) -> stability ~ 0
        stability = math.exp(-time_variance / 1e10)
        
        return float(np.clip(stability, 0.0, 1.0))
    
    def _calculate_reinforcement_depth(self, behaviors: List[Behavior]) -> float:
        """
        Calculate reinforcement depth using logarithmic scale.
        
        Formula: log(1 + total_reinforcement) / log(20)
        Assumes 20 total reinforcements represents maximum depth (score = 1.0)
        
        Args:
            behaviors: Behaviors in the cluster
            
        Returns:
            Reinforcement depth score (0.0 to 1.0)
        """
        total_reinforcement = sum(b.reinforcement_count for b in behaviors)
        
        # Logarithmic scale: log(1 + x) / log(20)
        depth_score = math.log(1 + total_reinforcement) / math.log(20)
        
        return float(np.clip(depth_score, 0.0, 1.0))
    
    def _assign_confidence_grade(
        self,
        confidence_score: float,
        behaviors: List[Behavior],
        cluster: Cluster
    ) -> str:
        """
        Assign confidence grade (High/Medium/Low) based on thresholds and component checks.
        
        Grading criteria:
        - High: confidence >= 0.75 AND all components >= 0.65
        - Medium: confidence >= 0.55 AND all components >= 0.45
        - Low: below Medium thresholds
        
        Args:
            confidence_score: Overall confidence score
            behaviors: Behaviors in the cluster
            cluster: Cluster object
            
        Returns:
            Confidence grade string: "High", "Medium", or "Low"
        """
        # Calculate individual components
        credibility = self._calculate_weighted_credibility(behaviors)
        stability = self._calculate_temporal_stability(behaviors)
        coherence = cluster.coherence_score
        reinforcement = self._calculate_reinforcement_depth(behaviors)
        
        # High grade criteria
        if confidence_score >= 0.75 and all([
            credibility >= 0.65,
            stability >= 0.65,
            coherence >= 0.65,
            reinforcement >= 0.65
        ]):
            return "High"
        
        # Medium grade criteria
        if confidence_score >= 0.55 and all([
            credibility >= 0.45,
            stability >= 0.45,
            coherence >= 0.45,
            reinforcement >= 0.45
        ]):
            return "Medium"
        
        # Low grade
        return "Low"
