# Phase 1 Remaining Tasks - CBAC System

**Project:** Core Behaviour Analysis Component (CBAC)  
**Document Created:** December 17, 2025  
**Target Completion:** December 30, 2025  
**Total Estimated Effort:** 18-26 hours  

---

## 📊 Current Phase 1 Status

| Feature Category | Status | Completion |
|-----------------|--------|------------|
| Core Analysis Pipeline | ✅ Complete | 100% |
| LLM Integration | ✅ Complete | 100% |
| Promotion/Rejection Logic | ✅ Complete | 100% |
| Confidence Scoring | ✅ Complete | 100% |
| API Endpoints | 🟡 Partial | 40% (2/5) |
| Data Quality | 🔴 Critical Issue | Needs Fix |
| Analysis Storage | ❌ Missing | 0% |
| Incremental Analysis | ❌ Missing | 0% |

---

## 🔴 CRITICAL PRIORITY - Must Do First

### Task 1: Fix Duplicate Core Behavior Generation
**Status:** ❌ Not Started  
**Priority:** 🔴 CRITICAL  
**Effort:** 2-3 hours  
**Blocking:** Yes - Produces incorrect results  

**Problem:**
- Same evidence chains creating multiple core behaviors
- Example: Two core behaviors with identical behavior_ids in evidence_chain
- Root cause: HDBSCAN may assign same behaviors to multiple clusters

**Implementation Steps:**

#### 1.1 Add Deduplication Logic
**File:** `cbac_api/app/services/core_analyzer.py`  
**Method:** `derive_core_behaviors()`

```python
# After line 65, before cluster evaluation loop
seen_evidence_chains = set()  # Track unique evidence sets

# Inside loop, after getting cluster behaviors (line ~70)
# Create sorted tuple for comparison
evidence_tuple = tuple(sorted(cluster_behavior_ids))

# Skip if duplicate
if evidence_tuple in seen_evidence_chains:
    logger.warning(f"Duplicate cluster detected: {cluster.cluster_id}")
    rejection_stats["rejected"] += 1
    rejection_stats["rejection_reasons"]["duplicate_evidence_chain"] = \
        rejection_stats["rejection_reasons"].get("duplicate_evidence_chain", 0) + 1
    continue

# After successful promotion
seen_evidence_chains.add(evidence_tuple)
```

#### 1.2 Add Cluster Similarity Check
**File:** `cbac_api/app/services/core_analyzer.py`  
**New Method:** `_is_similar_to_existing_core()`

```python
def _is_similar_to_existing_core(
    self,
    candidate_cluster: Cluster,
    existing_cores: List[CoreBehavior],
    similarity_threshold: float = 0.5
) -> bool:
    """
    Check if candidate cluster is too similar to existing core behavior.
    
    Args:
        candidate_cluster: Cluster being evaluated
        existing_cores: Already promoted core behaviors
        similarity_threshold: Jaccard similarity threshold (default 0.5)
        
    Returns:
        True if similar cluster already exists, False otherwise
    """
    for existing in existing_cores:
        # Calculate Jaccard similarity
        candidate_set = set(candidate_cluster.behavior_ids)
        existing_set = set(existing.evidence_chain)
        
        intersection = len(candidate_set & existing_set)
        union = len(candidate_set | existing_set)
        
        jaccard_similarity = intersection / union if union > 0 else 0
        
        if jaccard_similarity > similarity_threshold:
            logger.warning(
                f"Cluster {candidate_cluster.cluster_id} is {jaccard_similarity:.2%} "
                f"similar to existing core {existing.core_behavior_id}"
            )
            return True
    
    return False
```

#### 1.3 Update Tests
**File:** `tests/validation/validate_p0_fixes.py`

Add test case:
```python
def test_no_duplicate_core_behaviors():
    """Verify no duplicate core behaviors in analysis results"""
    # Check evidence chains are unique
    # Check Jaccard similarity < 50% between all pairs
```

**Acceptance Criteria:**
- ✅ No two core behaviors share >50% of evidence chain
- ✅ Rejection stats include "duplicate_evidence_chain" reason
- ✅ Test validation passes for all users

---

## 🟠 HIGH PRIORITY - Phase 1A

### Task 2: Implement Missing Analysis Retrieval Endpoints
**Status:** ❌ Not Started  
**Priority:** 🟠 High  
**Effort:** 4-6 hours  

**Missing Endpoints:**

#### 2.1 GET /analysis/{user_id}/history
**File:** `cbac_api/app/routers/analysis.py`

**Purpose:** Retrieve all past analyses for a user  
**Response:**
```json
{
  "user_id": "user_4_1765826173",
  "analyses": [
    {
      "analysis_id": "user_4_1765826173_latest",
      "timestamp": 1765831792,
      "num_core_behaviors": 12,
      "total_behaviors": 100
    }
  ],
  "total_count": 1
}
```

**Implementation:**
- List all files in `analysis_results/` matching `user_{user_id}_*.json`
- Parse timestamps from filenames
- Return sorted by timestamp (newest first)
- Pagination support (optional)

---

#### 2.2 GET /analysis/{user_id}/latest
**File:** `cbac_api/app/routers/analysis.py`

**Purpose:** Get most recent analysis without re-clustering  
**Response:** Same as `POST /analysis` but from stored file

**Implementation:**
- Load `analysis_results/user_{user_id}_*_latest.json`
- If not exists, return 404 with message "No analysis found. Run POST /analysis first"
- Return cached analysis results

**Benefits:**
- Fast response (~10ms vs 30s for full analysis)
- Consistent results across multiple queries
- Reduces API costs (no LLM calls)

---

#### 2.3 GET /analysis/{analysis_id}
**File:** `cbac_api/app/routers/analysis.py`

**Purpose:** Retrieve specific analysis by ID  
**Response:** Full analysis JSON

**Implementation:**
- Load `analysis_results/{analysis_id}.json`
- Validate analysis_id format
- Return 404 if not found

**Example Request:**
```
GET /analysis/user_4_1765826173_1765831792
```

---

**Acceptance Criteria:**
- ✅ All 3 endpoints return correct data
- ✅ Proper error handling (404, 500)
- ✅ Tests added for each endpoint
- ✅ API documentation updated

---

### Task 3: Implement Analysis Storage Service
**Status:** ❌ Not Started  
**Priority:** 🟠 High  
**Effort:** 3-4 hours  

**Purpose:** Centralize analysis storage/retrieval logic

#### 3.1 Create AnalysisStoreService
**File:** `cbac_api/app/services/analysis_store.py` (enhance existing)

**Methods to Add:**

```python
def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve specific analysis by ID"""
    
def list_user_analyses(
    self, 
    user_id: str, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """List all analyses for a user with pagination"""
    
def get_latest_analysis(self, user_id: str) -> Optional[Dict[str, Any]]:
    """Get most recent analysis for user"""
    
def delete_analysis(self, analysis_id: str) -> bool:
    """Delete an analysis by ID"""
    
def get_analysis_stats(self, user_id: str) -> Dict[str, Any]:
    """Get statistics about user's analysis history"""
```

#### 3.2 Update Existing save_analysis()
**Enhancements:**
- Add analysis_id to saved JSON
- Include save_timestamp
- Add version tracking
- Compress old analyses (optional)

---

**Acceptance Criteria:**
- ✅ All methods implemented and tested
- ✅ Proper error handling
- ✅ Logging for all operations
- ✅ Used by new endpoints

---

## 🟡 MEDIUM PRIORITY - Phase 1B

### Task 4: Implement Incremental Analysis
**Status:** ❌ Not Started  
**Priority:** 🟡 Medium  
**Effort:** 6-8 hours  

**Purpose:** Only re-analyze when new behaviors detected

#### 4.1 Add Behavior Change Detection
**File:** `cbac_api/app/routers/analysis.py`

**Flow:**
```python
# Step 1: Get current behaviors from Qdrant
current_behaviors = vector_service.get_behaviors_by_user(user_id)

# Step 2: Load previous analysis
previous_analysis = analysis_store.load_previous_analysis(user_id)

# Step 3: Compare behavior counts
if previous_analysis:
    prev_behavior_ids = set(previous_analysis.get("behavior_ids", []))
    curr_behavior_ids = set([b.behavior_id for b in current_behaviors])
    
    # Check if behaviors changed
    if prev_behavior_ids == curr_behavior_ids:
        logger.info("No new behaviors, returning cached analysis")
        return previous_analysis
    
    new_behaviors = curr_behavior_ids - prev_behavior_ids
    logger.info(f"Found {len(new_behaviors)} new behaviors, re-analyzing")

# Step 4: Proceed with full analysis only if needed
```

#### 4.2 Add Force Re-analyze Parameter
**Endpoint:** `POST /analysis?force=true`

Allow users to force full re-analysis even if no changes detected.

---

**Benefits:**
- 🚀 99% faster for repeat queries (10ms vs 30s)
- 💰 Reduces LLM API costs (no redundant generations)
- 📊 Consistent results for same data

**Acceptance Criteria:**
- ✅ Returns cached analysis when no behavior changes
- ✅ Re-analyzes when new behaviors added
- ✅ Force parameter works correctly
- ✅ Tests validate caching behavior

---

### Task 5: Enhance Change Detection
**Status:** 🟡 Partial (basic detection exists)  
**Priority:** 🟡 Medium  
**Effort:** 2-3 hours  

**Current:** Detects new/retired/updated behaviors  
**Missing:** More granular change types

#### 5.1 Add Change Significance Scoring
**File:** `cbac_api/app/services/core_analyzer.py`  
**Method:** `detect_changes()`

**New Change Types:**
- `strengthened`: Confidence increased >0.20
- `weakened`: Confidence decreased >0.20
- `minor_update`: Confidence changed 0.10-0.20
- `stable`: Confidence changed <0.10

#### 5.2 Add Change Explanations
```json
{
  "change_type": "strengthened",
  "explanation": "User's gardening pattern confidence increased from 0.72 to 0.89 (+0.17) due to 3 new related behaviors",
  "new_behaviors_added": 3,
  "confidence_delta": 0.17
}
```

---

**Acceptance Criteria:**
- ✅ All change types properly classified
- ✅ Explanations generated for each change
- ✅ Tests validate classification logic

---

## 🟢 LOW PRIORITY - Phase 1C

### Task 6: Update Documentation
**Status:** ❌ Not Started  
**Priority:** 🟢 Low  
**Effort:** 1-2 hours  

**Files to Update:**

#### 6.1 API Specification
**File:** `docs/specifications/API_SPECIFICATION.md`

Updates needed:
- Add LLM generation documentation
- Document cache service behavior
- Update response schemas with new fields
- Add new endpoint documentation

#### 6.2 Architecture Documentation
**File:** `docs/architecture/cbac_system_flow_v2.md`

Updates needed:
- Add LLM service to architecture diagram
- Document MongoDB behaviors collection
- Update data flow diagrams
- Add caching layer

#### 6.3 Implementation Status
**File:** `docs/implementation/FEATURE_IMPLEMENTATION_STATUS.md`

Updates needed:
- Mark completed features as done
- Update completion percentages
- Add LLM integration section
- Update endpoint counts

---

**Acceptance Criteria:**
- ✅ All documentation reflects current implementation
- ✅ Code examples are accurate
- ✅ Architecture diagrams updated
- ✅ No outdated information

---

## 📋 Summary Checklist

### Critical (Must Complete for Phase 1)
- [ ] Task 1: Fix duplicate core behaviors (2-3h)
- [ ] Task 2: Analysis retrieval endpoints (4-6h)
- [ ] Task 3: Analysis storage service (3-4h)

**Subtotal: 9-13 hours**

### High Priority (Should Complete)
- [ ] Task 4: Incremental analysis (6-8h)
- [ ] Task 5: Enhanced change detection (2-3h)

**Subtotal: 8-11 hours**

### Nice to Have
- [ ] Task 6: Documentation updates (1-2h)

**Subtotal: 1-2 hours**

---

## 🎯 Recommended Execution Order

1. **Week 1 (Days 1-3):** Critical tasks
   - Day 1: Task 1 (Duplicate detection)
   - Day 2-3: Task 2 & 3 (Endpoints + Storage)

2. **Week 2 (Days 4-7):** High priority
   - Day 4-5: Task 4 (Incremental analysis)
   - Day 6: Task 5 (Change detection)
   - Day 7: Task 6 (Documentation)

---

## ✅ Already Completed (Recent Work)

These Phase 1 features are **DONE**:

1. ✅ Core behavior promotion/rejection logic
   - Cluster size validation (min 3)
   - Credibility threshold (0.65)
   - Stability threshold (0.5)
   - Coherence threshold (0.7)
   - Confidence threshold (0.70)

2. ✅ Confidence scoring system
   - 4-component weighted formula
   - Credibility (35%)
   - Temporal stability (25%)
   - Cluster coherence (25%)
   - Reinforcement depth (15%)

3. ✅ LLM-based statement generation
   - Azure OpenAI integration (gpt-4o-mini)
   - Sophisticated prompt engineering
   - Template-based fallback
   - Error handling

4. ✅ Semantic caching
   - In-memory cache with TTL (7 days)
   - Cache key generation from behavior texts
   - Reduces API costs significantly
   - Cache statistics tracking

5. ✅ MongoDB integration
   - behaviors collection support
   - Behavior text retrieval
   - Data loading scripts
   - 483 behaviors loaded

6. ✅ Temporal stability calculation
   - Time gap analysis
   - Regularity scoring
   - Handles edge cases

7. ✅ Version and status management
   - Behavior lifecycle tracking
   - Active/Degrading/Historical/Retired states
   - Support ratio calculation

---

## 📞 Questions or Issues?

- Check `P0_FIXES_TODO.md` for detailed implementation guidance
- Review `FEATURE_IMPLEMENTATION_STATUS.md` for current state
- See `API_SPECIFICATION.md` for endpoint specifications
- Consult `cbac_system_flow_v2.md` for architecture details

---

**Document Version:** 1.0  
**Last Updated:** December 17, 2025  
**Next Review:** After Task 1 completion
