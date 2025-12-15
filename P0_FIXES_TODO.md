# P0 Critical Fixes & Phase 1 Completion - TODO List

**Project:** CBAC - Core Behaviour Analysis Component  
**Status:** 🔴 Critical bugs identified - system produces incorrect results  
**Created:** December 15, 2025  
**Target Completion:** December 30, 2025 (2 weeks)  

---

## 📊 Current Status Summary

| Category | Current | Target | Status |
|----------|---------|--------|--------|
| **Algorithm Correctness** | 40% | 100% | 🔴 Critical bugs |
| **Endpoints Implemented** | 3/29 (10%) | 18/29 (62%) | 🔴 Missing 15 endpoints |
| **Phase 1 Features** | 40% | 100% | 🔴 Incomplete |
| **Production Ready** | No | Yes | 🔴 Blocking issues |

**Estimated Total Effort:** 70-94 hours (~2-2.5 weeks full-time)

---

## 🔴 P0: CRITICAL FIXES (Must Do First)

**Priority:** BLOCKING - System produces incorrect results  
**Total Effort:** 16-22 hours  
**Target:** Complete before ANY new features  

---

### ☐ Fix 1: Implement Core Behavior Promotion Logic
**File:** `cbac_api/app/services/core_analyzer.py`  
**Priority:** 🔴 CRITICAL  
**Effort:** 6-8 hours  
**Status:** ❌ Not Started  

**Problem:**
- Current code promotes ALL clusters to core behaviors
- No evaluation or rejection logic
- Violates design specification (Pipeline A - Section 3)

**Implementation Steps:**

#### Step 1.1: Add Promotion Evaluation Method (2-3 hours)
```python
def _evaluate_cluster_for_promotion(
    self, 
    cluster: Cluster, 
    behaviors: List[Behavior]
) -> Tuple[Optional[Dict], Optional[Dict]]:
    """
    Evaluate if cluster qualifies for core behavior promotion.
    
    Returns:
        (result_dict, rejection_dict)
        - If promoted: ({"status": "promoted", "confidence": 0.85}, None)
        - If rejected: (None, {"reason": "low_credibility", "details": {...}})
        - If emerging: ({"status": "emerging"}, {"reason": "low_stability", ...})
    """
    
    # Check 1: Minimum cluster size
    if len(behaviors) < self.min_cluster_size:
        return None, {
            "reason": "insufficient_evidence",
            "cluster_size": len(behaviors),
            "required_size": self.min_cluster_size
        }
    
    # Check 2: Aggregate credibility (weighted)
    agg_credibility = self._calculate_weighted_credibility(behaviors)
    if agg_credibility < 0.65:
        return None, {
            "reason": "low_credibility",
            "aggregate_credibility": agg_credibility,
            "threshold": 0.65
        }
    
    # Check 3: Temporal stability
    stability_score = self._calculate_temporal_stability(behaviors)
    if stability_score < 0.5:
        # Mark as "emerging pattern" - not rejected, not promoted
        return {
            "status": "emerging",
            "stability_score": stability_score
        }, {
            "reason": "low_stability",
            "stability_score": stability_score,
            "threshold": 0.5
        }
    
    # Check 4: Semantic coherence
    if cluster.coherence_score < 0.7:
        return None, {
            "reason": "low_coherence",
            "coherence_score": cluster.coherence_score,
            "threshold": 0.7
        }
    
    # Calculate final promotion confidence
    promotion_confidence = self._calculate_promotion_confidence(
        agg_credibility, 
        stability_score, 
        cluster.coherence_score, 
        behaviors
    )
    
    # Check 5: Promotion threshold
    if promotion_confidence < 0.70:
        return None, {
            "reason": "below_promotion_threshold",
            "confidence": promotion_confidence,
            "threshold": 0.70
        }
    
    # PASSED ALL CHECKS - Promote to core behavior
    return {
        "status": "promoted",
        "confidence": promotion_confidence,
        "components": {
            "credibility": agg_credibility,
            "stability": stability_score,
            "coherence": cluster.coherence_score
        }
    }, None
```

**Test Cases to Add:**
- [ ] Test cluster with < 3 behaviors → rejected
- [ ] Test cluster with low credibility (< 0.65) → rejected
- [ ] Test cluster with low stability (< 0.5) → emerging
- [ ] Test cluster with low coherence (< 0.7) → rejected
- [ ] Test cluster with confidence < 0.70 → rejected
- [ ] Test valid cluster → promoted

#### Step 1.2: Add Weighted Credibility Calculation (1 hour)
```python
def _calculate_weighted_credibility(self, behaviors: List[Behavior]) -> float:
    """
    Calculate weighted average credibility.
    Weight by reinforcement_count per design spec.
    
    Formula: Σ(credibility × reinforcement) / Σ(reinforcement)
    """
    total_weight = sum(b.reinforcement_count for b in behaviors)
    
    if total_weight == 0:
        # Fallback to simple average if no reinforcements
        return np.mean([b.credibility for b in behaviors])
    
    weighted_sum = sum(
        b.credibility * b.reinforcement_count 
        for b in behaviors
    )
    
    return weighted_sum / total_weight
```

**Test Cases:**
- [ ] All behaviors with reinforcement_count = 0 → simple average
- [ ] Mixed reinforcement counts → weighted correctly
- [ ] Single behavior → returns its credibility

#### Step 1.3: Update derive_core_behaviors Method (2-3 hours)
```python
def derive_core_behaviors(
    self,
    user_id: str,
    behaviors: List[Behavior],
    clusters: List[Cluster],
    labels: np.ndarray
) -> Dict[str, Any]:
    """
    Derive core behaviors from clusters with promotion evaluation.
    
    Returns dict with:
    - core_behaviors: List of promoted core behaviors
    - rejected_clusters: List of rejected clusters with reasons
    - emerging_patterns: List of emerging patterns (low stability)
    - statistics: Summary stats
    """
    core_behaviors = []
    rejected_clusters = []
    emerging_patterns = []
    
    for cluster in clusters:
        # Get behaviors in this cluster
        cluster_behaviors = [
            b for b in behaviors
            if b.behavior_id in cluster.behavior_ids
        ]
        
        # Evaluate for promotion
        result, rejection_info = self._evaluate_cluster_for_promotion(
            cluster, cluster_behaviors
        )
        
        if result is None:
            # REJECTED
            rejected_clusters.append({
                "cluster_id": cluster.cluster_id,
                "size": len(cluster_behaviors),
                "rejection_info": rejection_info
            })
            logger.info(
                f"Cluster {cluster.cluster_id} rejected: "
                f"{rejection_info['reason']}"
            )
            
        elif result.get("status") == "emerging":
            # EMERGING PATTERN (not stable enough yet)
            emerging_patterns.append({
                "cluster_id": cluster.cluster_id,
                "size": len(cluster_behaviors),
                "stability_score": result["stability_score"],
                "behaviors": cluster.behavior_ids
            })
            logger.info(
                f"Cluster {cluster.cluster_id} marked as emerging pattern"
            )
            
        else:
            # PROMOTED - Create core behavior
            promotion_confidence = result["confidence"]
            
            # Generate generalized statement
            generalized_statement = self._generate_generalized_statement(
                cluster_behaviors, cluster
            )
            
            # Detect domain
            domain_detected = self._detect_domain(cluster_behaviors)
            
            # Build metadata
            metadata = {
                "cluster_size": cluster.size,
                "coherence_score": cluster.coherence_score,
                "avg_reinforcement_count": np.mean([b.reinforcement_count for b in cluster_behaviors]),
                "avg_credibility": result["components"]["credibility"],
                "avg_clarity_score": np.mean([b.clarity_score for b in cluster_behaviors]),
                "temporal_stability": result["components"]["stability"]
            }
            
            core_behavior = CoreBehavior(
                core_behavior_id=f"core_{user_id}_{cluster.cluster_id}_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                generalized_statement=generalized_statement,
                confidence_score=promotion_confidence,
                evidence_chain=cluster.behavior_ids,
                cluster_id=cluster.cluster_id,
                domain_detected=domain_detected,
                metadata=metadata
            )
            
            core_behaviors.append(core_behavior)
            logger.info(
                f"Cluster {cluster.cluster_id} promoted to core behavior "
                f"(confidence: {promotion_confidence:.2f})"
            )
    
    # Return comprehensive results
    return {
        "core_behaviors": core_behaviors,
        "rejected_clusters": rejected_clusters,
        "emerging_patterns": emerging_patterns,
        "statistics": {
            "total_clusters": len(clusters),
            "promoted": len(core_behaviors),
            "rejected": len(rejected_clusters),
            "emerging": len(emerging_patterns),
            "promotion_rate": len(core_behaviors) / len(clusters) if clusters else 0
        }
    }
```

**Test Cases:**
- [ ] Mix of valid/invalid clusters → correct categorization
- [ ] All clusters rejected → empty core_behaviors list
- [ ] All clusters promoted → full core_behaviors list
- [ ] Statistics calculated correctly

#### Step 1.4: Update Analysis Router (1 hour)
```python
# In cbac_api/app/routers/analysis.py
# Update to handle new return structure

analysis_results = analyzer_service.derive_core_behaviors(...)

# Extract components
core_behaviors = analysis_results["core_behaviors"]
rejected = analysis_results["rejected_clusters"]
emerging = analysis_results["emerging_patterns"]
stats = analysis_results["statistics"]

# Build response with rejection info
response = AnalysisResponse(
    user_id=request.user_id,
    core_behaviors=core_behaviors,
    total_behaviors_analyzed=len(behaviors),
    num_clusters=len(clusters),
    metadata={
        "processing_time_ms": round(processing_time, 2),
        "quality_metrics": quality_metrics,
        "clustering_params": {...},
        "promotion_statistics": stats,
        "rejected_clusters": rejected,
        "emerging_patterns": emerging
    }
)
```

**Validation:**
- [ ] Response includes rejection info
- [ ] Response includes emerging patterns
- [ ] Response includes promotion statistics

---

### ☐ Fix 2: Implement Temporal Stability Score
**File:** `cbac_api/app/services/core_analyzer.py`  
**Priority:** 🔴 CRITICAL  
**Effort:** 3-4 hours  
**Status:** ❌ Not Started  
**Blocks:** Fix 1, Fix 3  

**Problem:**
- Missing 25% of confidence calculation
- No time-based variance analysis
- Confidence scores artificially inflated

**Implementation Steps:**

#### Step 2.1: Add Temporal Stability Method (2-3 hours)
```python
def _calculate_temporal_stability(self, behaviors: List[Behavior]) -> float:
    """
    Calculate temporal stability from time variance.
    
    High stability = behaviors observed consistently over time (low variance)
    Low stability = sporadic observations or recent spike (high variance)
    
    Formula: 1 - (std_dev(time_gaps) / mean(time_gaps))
    
    Returns:
        float: Stability score 0.0-1.0
    """
    if len(behaviors) < 2:
        # Single behavior or empty - no temporal data
        return 0.0
    
    # Get timestamps (last_seen field)
    timestamps = sorted([b.last_seen for b in behaviors])
    
    # Calculate gaps between observations
    time_gaps = [
        timestamps[i+1] - timestamps[i] 
        for i in range(len(timestamps) - 1)
    ]
    
    if not time_gaps:
        return 0.0
    
    # Calculate variance
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
    return max(0.0, min(1.0, stability))
```

**Test Cases:**
- [ ] 2 behaviors same time → stability = 0.0
- [ ] Regular intervals (e.g., daily) → high stability (~0.9)
- [ ] Irregular intervals → low stability (~0.3-0.5)
- [ ] Recent spike after long gap → very low stability
- [ ] Single behavior → stability = 0.0

#### Step 2.2: Add Temporal Analysis Utilities (1 hour)
```python
def _analyze_temporal_patterns(self, behaviors: List[Behavior]) -> Dict[str, Any]:
    """
    Analyze temporal patterns in behaviors.
    Useful for debugging and understanding stability.
    """
    if len(behaviors) < 2:
        return {"pattern": "insufficient_data"}
    
    timestamps = sorted([b.last_seen for b in behaviors])
    time_gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps) - 1)]
    
    # Convert seconds to days for readability
    gaps_days = [gap / 86400 for gap in time_gaps]
    
    return {
        "pattern": "regular" if np.std(gaps_days) < np.mean(gaps_days) * 0.5 else "irregular",
        "mean_gap_days": np.mean(gaps_days),
        "std_gap_days": np.std(gaps_days),
        "min_gap_days": np.min(gaps_days),
        "max_gap_days": np.max(gaps_days),
        "total_span_days": (timestamps[-1] - timestamps[0]) / 86400,
        "observation_count": len(behaviors)
    }
```

**Validation:**
- [ ] Temporal patterns correctly classified
- [ ] Metadata useful for debugging

---

### ☐ Fix 3: Fix Confidence Calculation Formula
**File:** `cbac_api/app/services/core_analyzer.py`  
**Priority:** 🔴 CRITICAL  
**Effort:** 4-5 hours  
**Status:** ❌ Not Started  
**Depends On:** Fix 2  

**Problem:**
- Wrong formula (missing temporal stability)
- Wrong weights (30/30/20/20 instead of 35/25/25/15)
- Simple average instead of weighted credibility
- Variance instead of logarithmic reinforcement

**Implementation Steps:**

#### Step 3.1: Rewrite Confidence Calculation (3-4 hours)
```python
def _calculate_promotion_confidence(
    self,
    aggregate_credibility: float,
    temporal_stability: float,
    semantic_coherence: float,
    behaviors: List[Behavior]
) -> float:
    """
    Calculate promotion confidence using correct formula from design spec.
    
    CBC = (w1 × Cred_agg) + (w2 × Stab_score) + (w3 × Sem_coh) + (w4 × Reinf_depth)
    
    Weights: 35%, 25%, 25%, 15%
    
    Components:
    1. Cred_agg: Weighted credibility aggregate (already calculated)
    2. Stab_score: Temporal stability (already calculated)
    3. Sem_coh: Semantic coherence from clustering
    4. Reinf_depth: Logarithmic reinforcement depth
    
    Args:
        aggregate_credibility: Weighted average credibility
        temporal_stability: Temporal variance-based stability
        semantic_coherence: Cluster coherence score
        behaviors: List of behaviors in cluster
        
    Returns:
        float: Final confidence score (0.0-1.0)
    """
    
    # Component 1: Weighted Credibility (35%)
    cred_component = aggregate_credibility
    
    # Component 2: Temporal Stability (25%)
    stab_component = temporal_stability
    
    # Component 3: Semantic Coherence (25%)
    coh_component = semantic_coherence
    
    # Component 4: Reinforcement Depth (15%)
    # Logarithmic scale: log(1 + total_reinforcements) / log(threshold)
    total_reinforcements = sum(b.reinforcement_count for b in behaviors)
    
    # Using threshold of 20 (behaviors with 20+ reinforcements score 1.0)
    if total_reinforcements > 0:
        reinf_component = math.log(1 + total_reinforcements) / math.log(20)
        reinf_component = min(1.0, reinf_component)  # Cap at 1.0
    else:
        reinf_component = 0.0
    
    # Final confidence with correct weights
    confidence = (
        0.35 * cred_component +
        0.25 * stab_component +
        0.25 * coh_component +
        0.15 * reinf_component
    )
    
    # Ensure valid range
    confidence = max(0.0, min(1.0, confidence))
    
    logger.debug(
        f"Confidence calculation: "
        f"cred={cred_component:.3f}(35%), "
        f"stab={stab_component:.3f}(25%), "
        f"coh={coh_component:.3f}(25%), "
        f"reinf={reinf_component:.3f}(15%) "
        f"→ final={confidence:.3f}"
    )
    
    return confidence
```

**Test Cases:**
- [ ] All components = 1.0 → confidence = 1.0
- [ ] All components = 0.0 → confidence = 0.0
- [ ] Mixed components → weighted correctly
- [ ] Reinforcement = 20 → reinf_component = 1.0
- [ ] Reinforcement = 0 → reinf_component = 0.0
- [ ] Weights sum to 1.0

#### Step 3.2: Add Confidence Component Breakdown (1 hour)
```python
def _get_confidence_breakdown(
    self,
    aggregate_credibility: float,
    temporal_stability: float,
    semantic_coherence: float,
    behaviors: List[Behavior],
    final_confidence: float
) -> Dict[str, float]:
    """
    Return detailed breakdown of confidence components.
    Useful for debugging and explainability.
    """
    total_reinforcements = sum(b.reinforcement_count for b in behaviors)
    reinf_component = min(1.0, math.log(1 + total_reinforcements) / math.log(20))
    
    return {
        "credibility_component": aggregate_credibility,
        "credibility_weight": 0.35,
        "credibility_contribution": aggregate_credibility * 0.35,
        
        "stability_component": temporal_stability,
        "stability_weight": 0.25,
        "stability_contribution": temporal_stability * 0.25,
        
        "coherence_component": semantic_coherence,
        "coherence_weight": 0.25,
        "coherence_contribution": semantic_coherence * 0.25,
        
        "reinforcement_component": reinf_component,
        "reinforcement_weight": 0.15,
        "reinforcement_contribution": reinf_component * 0.15,
        
        "total_reinforcements": total_reinforcements,
        "final_confidence": final_confidence
    }
```

**Validation:**
- [ ] Contributions sum to final_confidence
- [ ] All weights present
- [ ] Useful for debugging

---

### ☐ Fix 4: Add Confidence Grading
**File:** `cbac_api/app/services/core_analyzer.py`, `cbac_api/app/models/schemas.py`  
**Priority:** 🔴 CRITICAL  
**Effort:** 2-3 hours  
**Status:** ❌ Not Started  
**Depends On:** Fix 3  

**Problem:**
- No human-readable confidence grade
- Users can't quickly assess quality

**Implementation Steps:**

#### Step 4.1: Update CoreBehavior Schema (30 min)
```python
# In cbac_api/app/models/schemas.py

class CoreBehavior(BaseModel):
    core_behavior_id: str
    user_id: str
    generalized_statement: str
    confidence_score: float
    confidence_grade: str  # NEW: "High" | "Medium" | "Low"
    confidence_components: Optional[Dict[str, float]] = None  # NEW: breakdown
    evidence_chain: List[str]
    cluster_id: int
    domain_detected: str
    metadata: Dict[str, Any]
    
    # NEW: Status and versioning fields
    status: str = "active"  # "active" | "degrading" | "historical" | "retired"
    version: int = 1
    created_at: Optional[int] = None
    last_updated: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "core_behavior_id": "core_user_001_cluster_01_a3f8c2d1",
                "user_id": "user_stable_users_01",
                "generalized_statement": "prefers visual learning methods",
                "confidence_score": 0.85,
                "confidence_grade": "High",
                "confidence_components": {
                    "credibility_component": 0.82,
                    "stability_component": 0.78,
                    "coherence_component": 0.84,
                    "reinforcement_component": 0.92
                },
                "evidence_chain": ["beh_001", "beh_023", "beh_045"],
                "cluster_id": 1,
                "domain_detected": "learning",
                "status": "active",
                "version": 1
            }
        }
```

#### Step 4.2: Add Grading Method (1-1.5 hours)
```python
def _assign_confidence_grade(
    self, 
    confidence: float, 
    components: Dict[str, float]
) -> str:
    """
    Assign High/Medium/Low grade based on overall confidence 
    AND individual component thresholds.
    
    Grading Criteria:
    - High: confidence >= 0.75 AND all components >= 0.65
    - Medium: confidence >= 0.55 AND all components >= 0.45
    - Low: Otherwise
    
    Args:
        confidence: Final confidence score
        components: Dict with component values
        
    Returns:
        str: "High" | "Medium" | "Low"
    """
    
    # Extract component values
    component_values = [
        components.get("credibility_component", 0.0),
        components.get("stability_component", 0.0),
        components.get("coherence_component", 0.0),
        components.get("reinforcement_component", 0.0)
    ]
    
    # Check thresholds
    all_components_high = all(v >= 0.65 for v in component_values)
    all_components_medium = all(v >= 0.45 for v in component_values)
    
    # Assign grade
    if confidence >= 0.75 and all_components_high:
        grade = "High"
    elif confidence >= 0.55 and all_components_medium:
        grade = "Medium"
    else:
        grade = "Low"
    
    logger.debug(
        f"Confidence grade: {grade} "
        f"(confidence={confidence:.3f}, components={component_values})"
    )
    
    return grade
```

**Test Cases:**
- [ ] confidence=0.85, all components high → "High"
- [ ] confidence=0.65, mixed components → "Medium"
- [ ] confidence=0.45, low components → "Low"
- [ ] Edge case: high confidence but low component → "Medium" or "Low"

#### Step 4.3: Integrate Grading into Derivation (30 min)
```python
# In derive_core_behaviors method

# Get confidence breakdown
breakdown = self._get_confidence_breakdown(
    agg_credibility, stability_score, cluster.coherence_score, 
    cluster_behaviors, promotion_confidence
)

# Assign grade
confidence_grade = self._assign_confidence_grade(
    promotion_confidence, breakdown
)

# Create core behavior with grade
core_behavior = CoreBehavior(
    # ... existing fields ...
    confidence_score=promotion_confidence,
    confidence_grade=confidence_grade,
    confidence_components=breakdown,
    # ... rest of fields ...
)
```

**Validation:**
- [ ] All core behaviors have confidence_grade
- [ ] All core behaviors have confidence_components
- [ ] Grades match confidence scores

---

### ☐ Fix 5: Implement Change Detection
**Files:** `cbac_api/app/services/core_analyzer.py`, `cbac_api/app/routers/analysis.py`  
**Priority:** 🔴 CRITICAL  
**Effort:** 4-5 hours  
**Status:** ❌ Not Started  

**Problem:**
- API claims to return change detection but doesn't implement it
- No persistence of previous analysis
- False information in responses

**Implementation Steps:**

#### Step 5.1: Add Analysis Persistence (2 hours)
```python
# Create new file: cbac_api/app/services/analysis_store.py

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

class AnalysisStore:
    """Store and retrieve analysis results for change detection"""
    
    def __init__(self, storage_dir: str = "./analysis_results"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_analysis(self, user_id: str, analysis_result: Dict[str, Any]) -> str:
        """
        Save analysis result to disk.
        
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
        with open(filepath, 'w') as f:
            json.dump(analysis_result, f, indent=2)
        
        return str(filepath)
    
    def load_previous_analysis(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load previous analysis result for user.
        
        Returns:
            Dict or None if no previous analysis exists
        """
        filename = f"{user_id}_latest.json"
        filepath = self.storage_dir / filename
        
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading previous analysis: {e}")
            return None
    
    def delete_analysis(self, user_id: str) -> bool:
        """Delete analysis result for user"""
        filename = f"{user_id}_latest.json"
        filepath = self.storage_dir / filename
        
        if filepath.exists():
            filepath.unlink()
            return True
        return False
```

#### Step 5.2: Add Change Detection Method (2 hours)
```python
# In cbac_api/app/services/core_analyzer.py

def _detect_changes(
    self,
    current_core_behaviors: List[CoreBehavior],
    previous_analysis: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare current analysis vs previous to detect changes.
    
    Changes detected:
    - New core behaviors (didn't exist before)
    - Updated core behaviors (confidence change > 0.15)
    - Retired core behaviors (no longer qualify)
    
    Args:
        current_core_behaviors: Newly derived core behaviors
        previous_analysis: Previous analysis result dict
        
    Returns:
        Dict with new, updated, retired lists
    """
    
    if not previous_analysis or "core_behaviors" not in previous_analysis:
        # First analysis - everything is new
        return {
            "new_core_behaviors": [cb.core_behavior_id for cb in current_core_behaviors],
            "updated_core_behaviors": [],
            "retired_core_behaviors": [],
            "is_first_analysis": True
        }
    
    # Build maps
    prev_behaviors = previous_analysis["core_behaviors"]
    prev_map = {cb["core_behavior_id"]: cb for cb in prev_behaviors}
    curr_map = {cb.core_behavior_id: cb for cb in current_core_behaviors}
    
    prev_ids = set(prev_map.keys())
    curr_ids = set(curr_map.keys())
    
    # Detect new behaviors
    new_ids = curr_ids - prev_ids
    
    # Detect retired behaviors
    retired_ids = prev_ids - curr_ids
    
    # Detect updated behaviors (confidence change > 0.15)
    updated = []
    for cb_id in prev_ids & curr_ids:
        prev_conf = prev_map[cb_id]["confidence_score"]
        curr_conf = curr_map[cb_id].confidence_score
        conf_delta = abs(curr_conf - prev_conf)
        
        if conf_delta > 0.15:
            updated.append({
                "core_behavior_id": cb_id,
                "previous_confidence": prev_conf,
                "current_confidence": curr_conf,
                "confidence_delta": conf_delta,
                "direction": "increased" if curr_conf > prev_conf else "decreased",
                "previous_grade": prev_map[cb_id].get("confidence_grade", "Unknown"),
                "current_grade": curr_map[cb_id].confidence_grade
            })
    
    return {
        "new_core_behaviors": list(new_ids),
        "updated_core_behaviors": updated,
        "retired_core_behaviors": list(retired_ids),
        "is_first_analysis": False,
        "total_changes": len(new_ids) + len(updated) + len(retired_ids)
    }
```

**Test Cases:**
- [ ] First analysis → all new, none updated/retired
- [ ] Same behaviors → no changes
- [ ] Added behavior → detected in new
- [ ] Removed behavior → detected in retired
- [ ] Confidence change < 0.15 → not in updated
- [ ] Confidence change > 0.15 → detected in updated

#### Step 5.3: Integrate into Analysis Router (1 hour)
```python
# In cbac_api/app/routers/analysis.py

from app.services.analysis_store import AnalysisStore

# Initialize store
analysis_store = AnalysisStore()

@router.post("", response_model=AnalysisResponse)
async def analyze_user_behaviors(request: AnalysisRequest):
    # ... existing code ...
    
    # Derive core behaviors
    derivation_results = analyzer_service.derive_core_behaviors(...)
    core_behaviors = derivation_results["core_behaviors"]
    
    # Load previous analysis
    previous_analysis = analysis_store.load_previous_analysis(request.user_id)
    
    # Detect changes
    changes = analyzer_service._detect_changes(core_behaviors, previous_analysis)
    
    # Build response
    response_dict = {
        "user_id": request.user_id,
        "core_behaviors": [cb.dict() for cb in core_behaviors],
        "total_behaviors_analyzed": len(behaviors),
        "num_clusters": len(clusters),
        "metadata": {
            # ... existing metadata ...
            "changes_from_previous": changes
        }
    }
    
    # Save current analysis for next time
    analysis_store.save_analysis(request.user_id, response_dict)
    
    return AnalysisResponse(**response_dict)
```

**Validation:**
- [ ] First analysis saved correctly
- [ ] Second analysis detects changes
- [ ] Changes appear in API response
- [ ] Previous analysis loaded correctly

---

### ☐ Fix 6: Add Core Behavior Versioning
**Files:** `cbac_api/app/models/schemas.py`, `cbac_api/app/services/core_analyzer.py`  
**Priority:** 🟡 HIGH  
**Effort:** 3-4 hours  
**Status:** ❌ Not Started  
**Depends On:** Fix 5  

**Problem:**
- No version tracking for core behaviors
- Can't track evolution over time
- No created_at/last_updated timestamps

**Implementation Steps:**

#### Step 6.1: Schema Already Updated in Fix 4 ✅
- version field added
- created_at field added
- last_updated field added

#### Step 6.2: Add Version Management Method (2-3 hours)
```python
def _update_or_create_core_behavior(
    self,
    new_cb: CoreBehavior,
    previous_behaviors: Dict[str, Dict]
) -> CoreBehavior:
    """
    Update existing core behavior version or create new one.
    
    Args:
        new_cb: Newly derived core behavior
        previous_behaviors: Map of previous core behaviors by ID
        
    Returns:
        CoreBehavior with correct version and timestamps
    """
    import time
    
    current_time = int(time.time())
    
    if new_cb.core_behavior_id in previous_behaviors:
        # Update existing - increment version
        prev = previous_behaviors[new_cb.core_behavior_id]
        new_cb.version = prev.get("version", 1) + 1
        new_cb.created_at = prev.get("created_at", current_time)
        new_cb.last_updated = current_time
        
        logger.info(
            f"Updated core behavior {new_cb.core_behavior_id} "
            f"to version {new_cb.version}"
        )
    else:
        # Create new
        new_cb.version = 1
        new_cb.created_at = current_time
        new_cb.last_updated = current_time
        
        logger.info(
            f"Created new core behavior {new_cb.core_behavior_id} "
            f"version 1"
        )
    
    return new_cb
```

#### Step 6.3: Integrate Versioning (1 hour)
```python
# In derive_core_behaviors method

# Load previous analysis
previous_analysis = # ... passed from router or loaded here ...
prev_behaviors_map = {}
if previous_analysis and "core_behaviors" in previous_analysis:
    prev_behaviors_map = {
        cb["core_behavior_id"]: cb 
        for cb in previous_analysis["core_behaviors"]
    }

# When creating core behavior
core_behavior = CoreBehavior(...)

# Apply versioning
core_behavior = self._update_or_create_core_behavior(
    core_behavior, 
    prev_behaviors_map
)

core_behaviors.append(core_behavior)
```

**Test Cases:**
- [ ] First analysis → version = 1
- [ ] Second analysis, same behavior → version = 2
- [ ] Third analysis, same behavior → version = 3
- [ ] New behavior in second analysis → version = 1
- [ ] Timestamps set correctly

---

### ☐ Fix 7: Add Status Lifecycle Management
**File:** `cbac_api/app/services/core_analyzer.py`  
**Priority:** 🟡 MEDIUM  
**Effort:** 3-4 hours  
**Status:** ❌ Not Started  
**Depends On:** Fix 5, Fix 6  

**Problem:**
- No tracking of degrading behaviors
- Can't handle behaviors that lose support
- No Active/Degrading/Historical/Retired status

**Implementation Steps:**

#### Step 7.1: Add Status Calculation Method (2-3 hours)
```python
def _calculate_behavior_status(
    self,
    core_behavior: CoreBehavior,
    current_behaviors: List[Behavior],
    previous_cluster_info: Optional[Dict]
) -> Tuple[str, float]:
    """
    Calculate lifecycle status based on support ratio.
    
    Status definitions:
    - Active: support_ratio >= 0.5 (≥50% of original behaviors still present)
    - Degrading: 0.3 <= support_ratio < 0.5 (30-49% support)
    - Historical: 0 < support_ratio < 0.3 (<30% support)
    - Retired: support_ratio == 0 (no supporting behaviors)
    
    Args:
        core_behavior: Core behavior to evaluate
        current_behaviors: Current behavior list
        previous_cluster_info: Info about original cluster
        
    Returns:
        Tuple of (status, support_ratio)
    """
    
    # Get original cluster size
    if previous_cluster_info:
        original_size = previous_cluster_info.get("cluster_size", len(core_behavior.evidence_chain))
    else:
        # First analysis - use current evidence chain size
        original_size = len(core_behavior.evidence_chain)
    
    # Count current supporting behaviors
    current_behavior_ids = {b.behavior_id for b in current_behaviors}
    supporting_behaviors = [
        bid for bid in core_behavior.evidence_chain
        if bid in current_behavior_ids
    ]
    
    # Calculate support ratio
    support_ratio = len(supporting_behaviors) / original_size if original_size > 0 else 0.0
    
    # Assign status
    if support_ratio >= 0.5:
        status = "active"
    elif support_ratio >= 0.3:
        status = "degrading"
    elif support_ratio > 0:
        status = "historical"
    else:
        status = "retired"
    
    logger.debug(
        f"Status for {core_behavior.core_behavior_id}: {status} "
        f"(support_ratio={support_ratio:.2f}, "
        f"supporting={len(supporting_behaviors)}/{original_size})"
    )
    
    return status, support_ratio
```

**Test Cases:**
- [ ] All behaviors present (100%) → active
- [ ] 50% behaviors present → active
- [ ] 40% behaviors present → degrading
- [ ] 20% behaviors present → historical
- [ ] 0% behaviors present → retired

#### Step 7.2: Integrate Status Tracking (1 hour)
```python
# In derive_core_behaviors or analysis router

# After creating core behaviors
for core_behavior in core_behaviors:
    # Calculate status
    status, support_ratio = self._calculate_behavior_status(
        core_behavior,
        current_behaviors,
        previous_cluster_info  # from previous analysis
    )
    
    core_behavior.status = status
    
    # Add support ratio to metadata
    core_behavior.metadata["support_ratio"] = support_ratio
    core_behavior.metadata["original_cluster_size"] = original_size
```

**Validation:**
- [ ] Status calculated correctly
- [ ] Support ratio in metadata
- [ ] Retired behaviors flagged

---

## ✅ P0 VALIDATION CHECKLIST

After completing all P0 fixes, validate:

### Algorithm Validation
- [ ] Run test with 35 behaviors - some clusters should be rejected
- [ ] Confidence scores should be lower than before (more selective)
- [ ] Temporal stability component affects scores
- [ ] Weighted credibility differs from simple average
- [ ] Confidence grades assigned correctly (High/Medium/Low)

### Change Detection Validation
- [ ] First analysis: all behaviors marked as "new"
- [ ] Second analysis: detects actual changes
- [ ] Updated behaviors detected when confidence changes > 0.15
- [ ] Retired behaviors detected
- [ ] Changes appear in API response

### Versioning Validation
- [ ] First analysis: all versions = 1
- [ ] Second analysis: existing behaviors increment version
- [ ] New behaviors start at version = 1
- [ ] Timestamps set correctly

### Status Validation
- [ ] Behaviors with full support → "active"
- [ ] Behaviors with partial support → "degrading"
- [ ] Behaviors with minimal support → "historical"
- [ ] Behaviors with no support → "retired"

### Response Validation
- [ ] API response includes rejection statistics
- [ ] API response includes emerging patterns
- [ ] API response includes change detection
- [ ] API response includes confidence grades
- [ ] API response includes confidence components

---

## 🔄 P1: PHASE 1 COMPLETION

**Priority:** HIGH - Complete after P0 fixes  
**Total Effort:** 39-49 hours  
**Target:** Full Phase 1 functionality  

---

### ☐ Task 1: Add Unit Tests for P0 Fixes
**Files:** `cbac_api/tests/test_core_analyzer.py` (new)  
**Priority:** 🟡 HIGH  
**Effort:** 3-4 hours  
**Status:** ❌ Not Started  

**Tests Needed:**

#### Promotion Logic Tests
```python
def test_promotion_logic_insufficient_evidence():
    """Cluster with < 3 behaviors should be rejected"""
    pass

def test_promotion_logic_low_credibility():
    """Cluster with credibility < 0.65 should be rejected"""
    pass

def test_promotion_logic_low_stability():
    """Cluster with stability < 0.5 should be marked emerging"""
    pass

def test_promotion_logic_low_coherence():
    """Cluster with coherence < 0.7 should be rejected"""
    pass

def test_promotion_logic_below_threshold():
    """Cluster with confidence < 0.70 should be rejected"""
    pass

def test_promotion_logic_success():
    """Valid cluster should be promoted"""
    pass
```

#### Temporal Stability Tests
```python
def test_temporal_stability_regular_intervals():
    """Regular intervals should give high stability"""
    pass

def test_temporal_stability_irregular_intervals():
    """Irregular intervals should give low stability"""
    pass

def test_temporal_stability_single_behavior():
    """Single behavior should return 0.0"""
    pass
```

#### Confidence Calculation Tests
```python
def test_confidence_calculation_weights():
    """Verify weights sum to 1.0 and are applied correctly"""
    pass

def test_confidence_calculation_components():
    """Verify each component calculated correctly"""
    pass

def test_confidence_grading():
    """Verify High/Medium/Low grades assigned correctly"""
    pass
```

#### Change Detection Tests
```python
def test_change_detection_first_analysis():
    """First analysis should mark all as new"""
    pass

def test_change_detection_no_changes():
    """Identical analysis should show no changes"""
    pass

def test_change_detection_new_behaviors():
    """New behaviors should be detected"""
    pass

def test_change_detection_confidence_change():
    """Confidence change > 0.15 should be detected"""
    pass
```

---

### ☐ Task 2: Improve Template Generation
**File:** `cbac_api/app/services/core_analyzer.py`  
**Priority:** 🟡 MEDIUM  
**Effort:** 3-4 hours  
**Status:** ❌ Not Started  

**Goal:** Extract semantic patterns instead of using fixed templates

**Implementation:**
```python
def _generate_generalized_statement(
    self,
    behaviors: List[Behavior],
    cluster: Cluster
) -> str:
    """
    Generate generalized statement with better pattern extraction.
    Phase 2 will replace with LLM, but this is better than current templates.
    """
    
    # Extract common terms
    behavior_texts = [b.behavior_text for b in behaviors]
    common_terms = self._extract_common_terms(behavior_texts)
    
    # Identify action patterns
    action_verbs = self._identify_action_verbs(behavior_texts)
    
    # Identify preference indicators
    preferences = self._identify_preferences(behavior_texts)
    
    # Generate statement from patterns
    if preferences and action_verbs:
        # Example: "prefers visual + learning" → "prefers visual learning methods"
        statement = f"{preferences[0]} {action_verbs[0]}"
    elif common_terms:
        # Use most common terms
        statement = " ".join(common_terms[:3])
    else:
        # Fallback to old templates
        statement = self._generate_fallback_statement(behaviors, cluster)
    
    return statement

def _extract_common_terms(self, texts: List[str]) -> List[str]:
    """Extract terms appearing in multiple behaviors"""
    from collections import Counter
    
    # Simple word frequency (can be improved with NLP)
    all_words = []
    for text in texts:
        words = text.lower().split()
        all_words.extend([w for w in words if len(w) > 3])  # Filter short words
    
    # Get most common
    counts = Counter(all_words)
    return [word for word, count in counts.most_common(5) if count >= 2]

def _identify_action_verbs(self, texts: List[str]) -> List[str]:
    """Identify action verbs in behaviors"""
    # Simple verb detection (Phase 2 can use proper NLP)
    verbs = ["prefers", "enjoys", "likes", "uses", "demonstrates", "shows", "requests"]
    found_verbs = []
    
    for text in texts:
        text_lower = text.lower()
        for verb in verbs:
            if verb in text_lower:
                found_verbs.append(verb)
                break
    
    return list(set(found_verbs))

def _identify_preferences(self, texts: List[str]) -> List[str]:
    """Identify preference indicators"""
    # Simple preference detection
    preferences = []
    indicators = ["visual", "collaborative", "hands-on", "structured", "flexible"]
    
    for text in texts:
        text_lower = text.lower()
        for indicator in indicators:
            if indicator in text_lower:
                preferences.append(indicator)
    
    return list(set(preferences))
```

**Test Cases:**
- [ ] Multiple behaviors with "visual" → "prefers visual ..."
- [ ] Multiple behaviors with "collaborative" → "enjoys collaborative ..."
- [ ] No common terms → fallback template

---

### ☐ Task 3: Implement Missing Analysis Endpoints
**File:** `cbac_api/app/routers/analysis.py`  
**Priority:** 🟡 HIGH  
**Effort:** 10-12 hours  
**Status:** ❌ Not Started  

#### Endpoint 3.1: POST /analysis/analyze/incremental (4-5 hours)
```python
@router.post("/analyze/incremental")
async def analyze_incremental(request: IncrementalAnalysisRequest):
    """
    Incremental analysis - assign new behaviors to existing clusters.
    
    Requires:
    - Previous analysis with centroids
    - List of new behaviors
    
    Process:
    1. Load existing centroids
    2. Assign new behaviors to nearest centroid (if distance < 0.80)
    3. Update centroids
    4. Create new clusters for orphans (if >= 3)
    5. Re-evaluate core behaviors for updated clusters
    """
    # Implementation details...
    pass
```

**Sub-tasks:**
- [ ] Implement centroid persistence (JSON)
- [ ] Implement assignment logic
- [ ] Implement centroid update
- [ ] Implement orphan pool management
- [ ] Test with incremental data

#### Endpoint 3.2: GET /analysis/results/{user_id} (2 hours)
```python
@router.get("/results/{user_id}")
async def get_analysis_results(
    user_id: str,
    include_evidence: bool = False,
    version: Optional[int] = None
):
    """
    Retrieve latest (or specific version) analysis results.
    """
    # Load from AnalysisStore
    analysis = analysis_store.load_previous_analysis(user_id)
    
    if not analysis:
        raise HTTPException(404, "No analysis found")
    
    # Filter by version if specified
    # Add evidence details if requested
    
    return analysis
```

**Sub-tasks:**
- [ ] Implement version filtering
- [ ] Implement evidence inclusion
- [ ] Test retrieval

#### Endpoint 3.3: GET /analysis/history/{user_id} (2-3 hours)
```python
@router.get("/history/{user_id}")
async def get_analysis_history(
    user_id: str,
    limit: int = 10,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None
):
    """
    Retrieve historical analysis results.
    
    Requires implementing history storage (multiple versions).
    """
    # Implementation with history storage
    pass
```

**Sub-tasks:**
- [ ] Implement history storage (not just latest)
- [ ] Implement filtering by date range
- [ ] Implement pagination
- [ ] Test history retrieval

#### Endpoint 3.4: DELETE /analysis/reset/{user_id} (1-2 hours)
```python
@router.delete("/reset/{user_id}")
async def reset_user_analysis(user_id: str):
    """
    Reset all analysis state for user.
    Clears:
    - Core behaviors
    - Cluster centroids
    - Analysis history
    - Cache entries
    """
    # Delete from AnalysisStore
    deleted = analysis_store.delete_analysis(user_id)
    
    # Delete centroids if exist
    # Delete cache entries if implemented
    
    return {
        "user_id": user_id,
        "reset_timestamp": int(time.time()),
        "cleared_items": {
            "analysis_history": 1 if deleted else 0,
            "centroids": 0,  # TODO
            "cache_entries": 0  # TODO Phase 2
        }
    }
```

**Sub-tasks:**
- [ ] Implement deletion
- [ ] Test reset
- [ ] Verify next analysis is fresh

---

### ☐ Task 4: Implement Clustering Endpoints
**File:** `cbac_api/app/routers/clustering.py` (new)  
**Priority:** 🟡 MEDIUM  
**Effort:** 8-10 hours  
**Status:** ❌ Not Started  

#### Endpoint 4.1: POST /clustering/cluster/full (3-4 hours)
```python
@router.post("/cluster/full")
async def force_full_clustering(request: FullClusteringRequest):
    """
    Force full re-clustering from scratch.
    Ignores existing centroids.
    """
    pass
```

#### Endpoint 4.2: GET /clustering/centroids/{user_id} (2 hours)
```python
@router.get("/centroids/{user_id}")
async def get_user_centroids(user_id: str):
    """
    Retrieve stored cluster centroids for user.
    """
    pass
```

#### Endpoint 4.3: GET /clustering/clusters/{user_id} (2-3 hours)
```python
@router.get("/clusters/{user_id}")
async def get_cluster_details(
    user_id: str,
    cluster_id: Optional[str] = None,
    include_members: bool = False
):
    """
    Get detailed cluster information.
    """
    pass
```

#### Endpoint 4.4: POST /clustering/validate (1-2 hours)
```python
@router.post("/validate")
async def validate_cluster_quality(request: ClusterValidationRequest):
    """
    Validate clustering quality with metrics.
    """
    pass
```

---

### ☐ Task 5: Implement Core Behavior Management Endpoints
**File:** `cbac_api/app/routers/core_behaviors.py` (new)  
**Priority:** 🟡 MEDIUM  
**Effort:** 8-10 hours  
**Status:** ❌ Not Started  

#### Endpoint 5.1: GET /core-behaviors/list/{user_id} (2 hours)
```python
@router.get("/list/{user_id}")
async def list_core_behaviors(
    user_id: str,
    min_confidence: float = 0.0,
    sort_by: str = "confidence",
    limit: Optional[int] = None
):
    """
    List all core behaviors for user with filtering.
    """
    pass
```

#### Endpoint 5.2: GET /core-behaviors/{core_behavior_id} (2 hours)
```python
@router.get("/{core_behavior_id}")
async def get_core_behavior(
    core_behavior_id: str,
    include_evidence: bool = True,
    include_source_behaviors: bool = False
):
    """
    Get detailed information about specific core behavior.
    """
    pass
```

#### Endpoint 5.3: GET /core-behaviors/evidence/{core_behavior_id} (2-3 hours)
```python
@router.get("/evidence/{core_behavior_id}")
async def get_evidence_chain(
    core_behavior_id: str,
    include_prompts: bool = False,
    include_metrics: bool = True
):
    """
    Retrieve detailed evidence chain.
    """
    pass
```

#### Endpoint 5.4: POST /core-behaviors/compare (2-3 hours)
```python
@router.post("/compare")
async def compare_core_behaviors(request: CompareRequest):
    """
    Compare different versions or temporal states.
    """
    pass
```

---

### ☐ Task 6: Enhanced Evidence Chains
**File:** `cbac_api/app/services/core_analyzer.py`  
**Priority:** 🟡 MEDIUM  
**Effort:** 4-5 hours  
**Status:** ❌ Not Started  

**Add to CoreBehavior metadata:**
```python
"evidence_chain_details": {
    "derivation_timestamp": 1732500000,
    "source_behaviors": [
        {
            "behavior_id": "beh_001",
            "contribution_weight": 0.35,
            "credibility": 0.85,
            "reinforcement_count": 5
        }
    ],
    "prompt_references": [
        {
            "prompt_id": "prompt_001",
            "timestamp": 1732180002,
            "behavior_ids_triggered": ["beh_001", "beh_023"]
        }
    ],
    "clustering_evidence": {
        "cluster_id": "cluster_01",
        "cluster_size": 12,
        "semantic_coherence": 0.82,
        "silhouette_score": 0.71
    },
    "derivation_logic": {
        "method": "template_based",  # or "llm_generalization" in Phase 2
        "template_version": "v1.0"
    },
    "confidence_calculation": {
        # Already have this from Fix 3.2
    }
}
```

---

### ☐ Task 7: Quality Metrics in Response
**File:** `cbac_api/app/routers/analysis.py`  
**Priority:** 🟡 LOW  
**Effort:** 2-3 hours  
**Status:** ❌ Not Started  

**Add to AnalysisResponse metadata:**
```python
"quality_metrics": {
    "overall_confidence": avg(core_behavior_confidences),
    "clustering_silhouette_score": silhouette_score,
    "promotion_rate": promoted / total_clusters,
    "avg_cluster_coherence": avg(cluster_coherences),
    "temporal_stability_avg": avg(temporal_stabilities)
}
```

---

## 📅 Recommended Schedule

### Week 1: P0 Critical Fixes
- **Day 1-2:** Fix 1 - Promotion Logic (8 hours)
- **Day 2-3:** Fix 2 - Temporal Stability + Fix 3 - Confidence (7 hours)
- **Day 3-4:** Fix 4 - Grading + Fix 5 - Change Detection (7 hours)
- **Day 4-5:** Fix 6 - Versioning + Fix 7 - Status Lifecycle (7 hours)
- **Day 5:** P0 Validation + Testing (4 hours)

**Week 1 Total: ~33 hours**

### Week 2: P1 Phase 1 Completion
- **Day 6-7:** Task 1 - Unit Tests + Task 2 - Better Templates (7 hours)
- **Day 7-8:** Task 3 - Analysis Endpoints (12 hours)
- **Day 9:** Task 4 - Clustering Endpoints (10 hours)
- **Day 10:** Task 5 - Core Behavior Endpoints (10 hours)
- **Day 10:** Task 6 & 7 - Evidence + Quality Metrics (7 hours)

**Week 2 Total: ~46 hours**

### Week 3: Buffer & Documentation
- Integration testing
- Documentation updates
- Bug fixes
- Performance optimization

---

## ✅ Success Criteria

### P0 Complete When:
- [ ] All 7 critical fixes implemented
- [ ] Some clusters are rejected (not all promoted)
- [ ] Confidence scores calculated correctly (4 components, correct weights)
- [ ] Change detection working (detects new/updated/retired)
- [ ] Confidence grades assigned (High/Medium/Low)
- [ ] Versioning working (increments correctly)
- [ ] Status lifecycle working (Active/Degrading/Historical/Retired)
- [ ] All P0 validation tests pass

### Phase 1 Complete When:
- [ ] All P0 fixes complete
- [ ] Unit tests written and passing
- [ ] 18/29 endpoints implemented (Phase 1 scope)
- [ ] Evidence chains detailed
- [ ] Quality metrics in responses
- [ ] Documentation updated
- [ ] System produces correct results per design spec

---

## 🚨 Red Flags to Watch For

- [ ] **Confidence scores still too high** → Check if promotion logic actually rejecting
- [ ] **All clusters still promoted** → Promotion thresholds too low
- [ ] **Changes not detected** → AnalysisStore not persisting
- [ ] **Versions not incrementing** → Version logic not integrated
- [ ] **Tests passing but results wrong** → Tests validating wrong behavior

---

## 📝 Notes

**DO NOT:**
- Skip P0 fixes to work on Phase 2 features
- Proceed to endpoints before fixing core algorithm
- Deploy to production before P0 validation passes

**DO:**
- Fix issues in order (P0 before P1)
- Test each fix individually before moving to next
- Update documentation as you go
- Commit after each major fix

**REMEMBER:**
- Current system produces **incorrect results**
- P0 fixes are **BLOCKING** everything else
- Phase 2 features (LLM, cache, incremental) can wait
- Getting **correct results** is priority #1

---

**Last Updated:** December 15, 2025  
**Next Review:** After P0 fixes complete  
**Owner:** Development Team  
**Status:** 🔴 IN PROGRESS - P0 Fixes Required
