import numpy as np
from typing import List, Dict, Any, Tuple, Optional
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
            
            # Get confidence breakdown
            confidence_breakdown = self._get_confidence_breakdown(
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
                confidence_components=confidence_breakdown,
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
        Calculate temporal stability based on variance in time gaps between observations.
        
        High stability = behaviors observed at regular intervals (low variance in gaps)
        Low stability = sporadic observations or recent spike (high variance in gaps)
        
        Formula: 1 - min(1.0, std_dev(gaps) / mean(gaps))
        Uses coefficient of variation to measure regularity.
        
        Args:
            behaviors: Behaviors in the cluster
            
        Returns:
            Stability score (0.0 to 1.0)
        """
        if len(behaviors) < 2:
            # Single behavior or empty - no temporal pattern
            return 0.0
        
        # Get timestamps (use last_seen field)
        timestamps = sorted([b.last_seen for b in behaviors])
        
        # Calculate gaps between observations
        time_gaps = [
            timestamps[i+1] - timestamps[i] 
            for i in range(len(timestamps) - 1)
        ]
        
        if not time_gaps:
            return 0.0
        
        # Calculate variance in gaps
        mean_gap = np.mean(time_gaps)
        std_gap = np.std(time_gaps)
        
        # Edge case: all observations at same time
        if mean_gap == 0:
            return 0.0
        
        # Calculate stability (inverse of coefficient of variation)
        # High variance → low stability
        # Low variance → high stability
        coefficient_of_variation = std_gap / mean_gap
        stability = 1.0 - min(1.0, coefficient_of_variation)
        
        # Ensure in valid range
        return float(max(0.0, min(1.0, stability)))
    
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
    
    def _get_confidence_breakdown(
        self,
        behaviors: List[Behavior],
        cluster: Cluster
    ) -> Dict[str, float]:
        """
        Get detailed breakdown of confidence components.
        Useful for debugging and explainability.
        
        Args:
            behaviors: Behaviors in the cluster
            cluster: Cluster object
            
        Returns:
            Dictionary with component values and contributions
        """
        # Calculate components
        credibility = self._calculate_weighted_credibility(behaviors)
        stability = self._calculate_temporal_stability(behaviors)
        coherence = cluster.coherence_score
        reinforcement = self._calculate_reinforcement_depth(behaviors)
        
        total_reinforcements = sum(b.reinforcement_count for b in behaviors)
        
        return {
            "credibility_component": credibility,
            "credibility_weight": 0.35,
            "credibility_contribution": credibility * 0.35,
            
            "stability_component": stability,
            "stability_weight": 0.25,
            "stability_contribution": stability * 0.25,
            
            "coherence_component": coherence,
            "coherence_weight": 0.25,
            "coherence_contribution": coherence * 0.25,
            
            "reinforcement_component": reinforcement,
            "reinforcement_weight": 0.15,
            "reinforcement_contribution": reinforcement * 0.15,
            
            "total_reinforcements": total_reinforcements
        }
    
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
    
    def detect_changes(
        self,
        current_core_behaviors: List[CoreBehavior],
        previous_analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect changes between current and previous analysis.
        
        Identifies:
        - New core behaviors (not in previous)
        - Retired behaviors (in previous, not in current)
        - Updated behaviors (confidence change > 0.15)
        
        Args:
            current_core_behaviors: Current analysis core behaviors
            previous_analysis: Previous analysis result dict (or None)
            
        Returns:
            Dict with new, retired, and updated behaviors
        """
        if not previous_analysis or "core_behaviors" not in previous_analysis:
            # First analysis - all are new
            return {
                "new_core_behaviors": [cb.core_behavior_id for cb in current_core_behaviors],
                "retired_behaviors": [],
                "updated_behaviors": [],
                "is_first_analysis": True
            }
        
        # Build maps for comparison
        prev_behaviors = previous_analysis.get("core_behaviors", [])
        prev_map = {cb["domain_detected"]: cb for cb in prev_behaviors if "domain_detected" in cb}
        current_map = {cb.domain_detected: cb for cb in current_core_behaviors}
        
        new_behaviors = []
        retired_behaviors = []
        updated_behaviors = []
        
        # Find new behaviors
        for domain, cb in current_map.items():
            if domain not in prev_map:
                new_behaviors.append({
                    "core_behavior_id": cb.core_behavior_id,
                    "domain": domain,
                    "confidence": cb.confidence_score
                })
        
        # Find retired and updated behaviors
        for domain, prev_cb in prev_map.items():
            if domain not in current_map:
                retired_behaviors.append({
                    "core_behavior_id": prev_cb.get("core_behavior_id"),
                    "domain": domain,
                    "previous_confidence": prev_cb.get("confidence_score", 0.0)
                })
            else:
                # Check for significant confidence change
                curr_cb = current_map[domain]
                prev_confidence = prev_cb.get("confidence_score", 0.0)
                curr_confidence = curr_cb.confidence_score
                
                if abs(curr_confidence - prev_confidence) > 0.15:
                    updated_behaviors.append({
                        "core_behavior_id": curr_cb.core_behavior_id,
                        "domain": domain,
                        "previous_confidence": prev_confidence,
                        "current_confidence": curr_confidence,
                        "confidence_delta": curr_confidence - prev_confidence
                    })
        
        return {
            "new_core_behaviors": new_behaviors,
            "retired_behaviors": retired_behaviors,
            "updated_behaviors": updated_behaviors,
            "is_first_analysis": False
        }
    
    def update_versions_and_timestamps(
        self,
        core_behaviors: List[CoreBehavior],
        previous_analysis: Optional[Dict[str, Any]]
    ) -> List[CoreBehavior]:
        """
        Update version numbers and timestamps for core behaviors.
        
        Logic:
        - If behavior existed before (matched by domain): increment version, update last_updated
        - If new behavior: keep version=1, set created_at and last_updated
        
        Args:
            core_behaviors: Current core behaviors
            previous_analysis: Previous analysis result (or None)
            
        Returns:
            Updated list of core behaviors
        """
        if not previous_analysis or "core_behaviors" not in previous_analysis:
            # First analysis - all are new, versions stay at 1
            return core_behaviors
        
        # Build map of previous behaviors by domain
        prev_behaviors = previous_analysis.get("core_behaviors", [])
        prev_map = {}
        for prev_cb in prev_behaviors:
            if "domain_detected" in prev_cb:
                prev_map[prev_cb["domain_detected"]] = prev_cb
        
        # Update versions and timestamps
        current_time = int(time.time())
        for cb in core_behaviors:
            if cb.domain_detected in prev_map:
                # Existing behavior - increment version, keep created_at, update last_updated
                prev_cb = prev_map[cb.domain_detected]
                cb.version = prev_cb.get("version", 1) + 1
                cb.created_at = prev_cb.get("created_at", current_time)
                cb.last_updated = current_time
            else:
                # New behavior - version already 1, set timestamps
                cb.created_at = current_time
                cb.last_updated = current_time
        
        return core_behaviors
    
    def calculate_behavior_status(
        self,
        core_behaviors: List[CoreBehavior],
        current_behaviors: List[Behavior],
        previous_analysis: Optional[Dict[str, Any]]
    ) -> List[CoreBehavior]:
        """
        Calculate and update status for each core behavior based on support ratio.
        
        Status lifecycle:
        - Active: >= 50% of original behaviors still present
        - Degrading: 30-49% support
        - Historical: 10-29% support  
        - Retired: < 10% support
        
        Args:
            core_behaviors: Current core behaviors
            current_behaviors: All current behaviors for the user
            previous_analysis: Previous analysis result (or None)
            
        Returns:
            Updated list of core behaviors with status set
        """
        if not previous_analysis or "core_behaviors" not in previous_analysis:
            # First analysis - all are Active
            for cb in core_behaviors:
                cb.status = "Active"
                if cb.metadata:
                    cb.metadata["support_ratio"] = 1.0
            return core_behaviors
        
        # Build map of current behavior IDs
        current_behavior_ids = set(b.behavior_id for b in current_behaviors)
        
        # Build map of previous core behaviors by domain
        prev_behaviors = previous_analysis.get("core_behaviors", [])
        prev_map = {}
        for prev_cb in prev_behaviors:
            if "domain_detected" in prev_cb and "evidence_chain" in prev_cb:
                prev_map[prev_cb["domain_detected"]] = prev_cb
        
        # Calculate support ratio for each core behavior
        for cb in core_behaviors:
            if cb.domain_detected in prev_map:
                prev_cb = prev_map[cb.domain_detected]
                prev_evidence = set(prev_cb.get("evidence_chain", []))
                
                # Count how many previous behaviors are still present
                still_present = len(prev_evidence & current_behavior_ids)
                original_count = len(prev_evidence)
                
                support_ratio = still_present / original_count if original_count > 0 else 1.0
                
                # Assign status based on support ratio
                if support_ratio >= 0.5:
                    cb.status = "Active"
                elif support_ratio >= 0.3:
                    cb.status = "Degrading"
                elif support_ratio >= 0.1:
                    cb.status = "Historical"
                else:
                    cb.status = "Retired"
                
                # Add support info to metadata
                if cb.metadata:
                    cb.metadata["support_ratio"] = support_ratio
                    cb.metadata["behaviors_still_present"] = still_present
                    cb.metadata["original_behavior_count"] = original_count
            else:
                # New behavior - Active
                cb.status = "Active"
                if cb.metadata:
                    cb.metadata["support_ratio"] = 1.0
        
        return core_behaviors
