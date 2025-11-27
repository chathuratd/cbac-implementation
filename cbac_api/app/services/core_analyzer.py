import numpy as np
import math
import time
from typing import List, Dict, Any, Tuple, Optional
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
    ) -> Tuple[List[CoreBehavior], Dict[str, Any]]:
        """
        Derive generalized core behaviors from behavior clusters.
        IMPLEMENTS PROMOTION LOGIC: Clusters must pass evaluation to become core behaviors.
        
        Args:
            user_id: User ID
            behaviors: Original behavior objects
            clusters: Cluster objects from clustering
            labels: Cluster assignment labels
            
        Returns:
            Tuple of (List of CoreBehavior objects, evaluation_stats dict)
        """
        core_behaviors = []
        evaluation_stats = {
            "total_clusters": len(clusters),
            "promoted": 0,
            "rejected": 0,
            "emerging": 0,
            "rejection_reasons": []
        }
        
        for cluster in clusters:
            # Get behaviors in this cluster
            cluster_behaviors = [
                b for b in behaviors
                if b.behavior_id in cluster.behavior_ids
            ]
            
            # CRITICAL FIX 1: Evaluate cluster for promotion
            promotion_result, reason = self._evaluate_cluster_for_promotion(cluster, cluster_behaviors)
            
            if promotion_result is None:
                # Cluster rejected
                evaluation_stats["rejected"] += 1
                evaluation_stats["rejection_reasons"].append({
                    "cluster_id": cluster.cluster_id,
                    "reason": reason,
                    "size": len(cluster_behaviors)
                })
                logger.debug(f"Cluster {cluster.cluster_id} rejected: {reason}")
                continue
            
            if promotion_result.get("status") == "emerging":
                # Cluster is emerging but not stable enough yet
                evaluation_stats["emerging"] += 1
                logger.debug(f"Cluster {cluster.cluster_id} marked as emerging (low stability)")
                continue
            
            # Cluster promoted - create core behavior
            confidence_score = promotion_result["confidence"]
            confidence_components = promotion_result["components"]
            confidence_grade = promotion_result["grade"]
            
            # Derive generalized statement
            generalized_statement = self._generate_generalized_statement(
                cluster_behaviors,
                cluster
            )
            
            # Detect domain (from ground truth labels)
            domain_detected = self._detect_domain(cluster_behaviors)
            
            # Build metadata with confidence breakdown
            metadata = {
                "cluster_size": cluster.size,
                "coherence_score": cluster.coherence_score,
                "avg_reinforcement_count": float(np.mean([b.reinforcement_count for b in cluster_behaviors])),
                "avg_credibility": float(np.mean([b.credibility for b in cluster_behaviors])),
                "avg_clarity_score": float(np.mean([b.clarity_score for b in cluster_behaviors])),
                "confidence_components": confidence_components,
                "confidence_grade": confidence_grade,
                "temporal_stability": confidence_components["stability_score"],
                "promotion_reason": "passed_all_criteria"
            }
            
            core_behavior = CoreBehavior(
                core_behavior_id=f"core_{user_id}_{cluster.cluster_id}_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                generalized_statement=generalized_statement,
                confidence_score=confidence_score,
                confidence_grade=confidence_grade,
                confidence_components=confidence_components,
                evidence_chain=cluster.behavior_ids,
                cluster_id=cluster.cluster_id,
                domain_detected=domain_detected,
                metadata=metadata,
                version=1,
                created_at=int(time.time()),
                last_updated=int(time.time()),
                status="active"
            )
            
            core_behaviors.append(core_behavior)
            evaluation_stats["promoted"] += 1
        
        logger.info(
            f"Evaluated {len(clusters)} clusters for user {user_id}: "
            f"{evaluation_stats['promoted']} promoted, "
            f"{evaluation_stats['rejected']} rejected, "
            f"{evaluation_stats['emerging']} emerging"
        )
        return core_behaviors, evaluation_stats
    
    def _generate_generalized_statement(
        self,
        behaviors: List[Behavior],
        cluster: Cluster
    ) -> str:
    def _evaluate_cluster_for_promotion(
        self,
        cluster: Cluster,
        behaviors: List[Behavior]
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        CRITICAL FIX 1: Evaluate if cluster qualifies as core behavior.
        Implements Pipeline A from design document (Section 3).
        
        Args:
            cluster: Cluster object
            behaviors: Behaviors in the cluster
            
        Returns:
            Tuple of (promotion_result dict or None, reason string)
            - None means rejection
            - {"status": "emerging"} means not stable enough
            - {"status": "promoted", "confidence": float, ...} means accepted
        """
        # Check 1: Minimum cluster size (3 behaviors minimum)
        if len(behaviors) < 3:
            return None, "insufficient_evidence"
        
        # Calculate components
        aggregate_credibility = self._calculate_weighted_credibility(behaviors)
        stability_score = self._calculate_temporal_stability(behaviors)
        semantic_coherence = cluster.coherence_score
        
        # Check 2: Credibility threshold
        if aggregate_credibility < 0.65:
            return None, "low_credibility"
        
        # Check 3: Stability threshold (mark as emerging if too low)
        if stability_score < 0.5:
            return {"status": "emerging", "stability": stability_score}, "low_stability"
        
        # Check 4: Coherence threshold
        if semantic_coherence < 0.7:
            return None, "low_coherence"
        
        # Calculate promotion confidence
        confidence, components = self._calculate_promotion_confidence(
            aggregate_credibility,
            stability_score,
            semantic_coherence,
            behaviors
        )
        
        # Check 5: Promotion confidence threshold
        if confidence < 0.70:
            return None, "below_confidence_threshold"
        
        # Assign confidence grade
        confidence_grade = self._assign_confidence_grade(confidence, components)
        
        # Cluster qualifies for promotion
        return {
            "status": "promoted",
            "confidence": confidence,
            "components": components,
            "grade": confidence_grade
        }, "promoted"
    
    def _calculate_weighted_credibility(self, behaviors: List[Behavior]) -> float:
        """
        CRITICAL FIX 2: Calculate weighted credibility aggregate.
        Weight by reinforcement_count instead of simple average.
        
        Formula: Σ(credibility × reinforcement) / Σ(reinforcement)
        """
        total_weight = sum(b.reinforcement_count for b in behaviors)
        if total_weight == 0:
            return float(np.mean([b.credibility for b in behaviors]))
        
        weighted_sum = sum(b.credibility * b.reinforcement_count for b in behaviors)
        return float(weighted_sum / total_weight)
    
    def _calculate_temporal_stability(self, behaviors: List[Behavior]) -> float:
        """
        CRITICAL FIX 3: Calculate temporal stability score (25% of confidence).
        High stability = behaviors observed consistently over time.
        Low stability = sporadic or recent spike.
        
        Formula: 1 - (std(time_gaps) / mean(time_gaps))
        """
        if len(behaviors) < 2:
            return 0.0
        
        # Get timestamps and sort
        timestamps = sorted([b.last_seen for b in behaviors])
        
        # Calculate time gaps between observations
        time_gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        if len(time_gaps) == 0 or all(gap == 0 for gap in time_gaps):
            return 0.0
        
        # Calculate variance
        mean_gap = np.mean(time_gaps)
        std_gap = np.std(time_gaps)
        
        if mean_gap == 0:
            return 0.0
        
        # High stability = low variance (regular intervals)
        stability = 1.0 - (std_gap / mean_gap)
        return float(max(0.0, min(1.0, stability)))
    
    def _calculate_promotion_confidence(
        self,
        aggregate_credibility: float,
        stability_score: float,
        semantic_coherence: float,
        behaviors: List[Behavior]
    ) -> Tuple[float, Dict[str, float]]:
        """
        CRITICAL FIX 4: Calculate promotion confidence per design spec CBC formula.
        
        CBC = (35% × Cred_agg) + (25% × Stab_score) + (25% × Sem_coh) + (15% × Reinf_depth)
        
        Returns:
            Tuple of (confidence_score, components_dict)
        """
        # Component 1: Weighted credibility aggregate (35%)
        cred_agg = aggregate_credibility
        
        # Component 2: Temporal stability (25%)
        stab_score = stability_score
        
        # Component 3: Semantic coherence (25%)
        sem_coh = semantic_coherence
        
        # Component 4: Reinforcement depth - logarithmic (15%)
        total_reinforcements = sum(b.reinforcement_count for b in behaviors)
        reinf_depth = math.log(1 + total_reinforcements) / math.log(20)  # 20 as threshold
        reinf_depth = min(1.0, reinf_depth)  # Cap at 1.0
        
        # Final confidence with correct weights: 35%, 25%, 25%, 15%
        confidence = (
            0.35 * cred_agg +
            0.25 * stab_score +
            0.25 * sem_coh +
            0.15 * reinf_depth
        )
        
        components = {
            "weighted_credibility": float(cred_agg),
            "stability_score": float(stab_score),
            "semantic_coherence": float(sem_coh),
            "reinforcement_depth": float(reinf_depth),
            "total_reinforcements": int(total_reinforcements)
        }
        
        return float(np.clip(confidence, 0.0, 1.0)), components
    
    def _assign_confidence_grade(self, confidence: float, components: Dict[str, float]) -> str:
        """
        CRITICAL FIX 5: Assign High/Medium/Low confidence grade.
        
        Criteria:
        - High: confidence >= 0.75 AND all components >= 0.65
        - Medium: confidence >= 0.55 AND all components >= 0.45
        - Low: otherwise
        """
        component_values = [
            components["weighted_credibility"],
            components["stability_score"],
            components["semantic_coherence"],
            components["reinforcement_depth"]
        ]
        
        all_components_high = all(v >= 0.65 for v in component_values)
        all_components_medium = all(v >= 0.45 for v in component_values)
        
        if confidence >= 0.75 and all_components_high:
            return "High"
        elif confidence >= 0.55 and all_components_medium:
            return "Medium"
        else:
            return "Low"
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
