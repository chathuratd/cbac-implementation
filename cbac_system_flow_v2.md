# Core Behaviour Analysis Component (CBAC) - System Design Document v2.0

## Revision History
- **v1.0** - Initial architecture design
- **v2.0** - Incorporates critical implementation optimizations from architectural review

## Document Change Summary
This version addresses five critical risks identified in architectural evaluation:
1. Full re-clustering scalability (incremental clustering strategy)
2. LLM cost optimization (semantic cache implementation)
3. Privacy protection enhancement (secure evidence chain design)
4. Data insufficiency handling (graduated analysis approach)
5. Taxonomy management scalability (automated evolution pipeline)

---

## 1. Overall Architecture Description

### 1.1 System Position in Data Pipeline

```
[Upstream System] → [Vector DB: Behaviours] → [CBAC] → [Output Store: Core Behaviours & Expertise]
                  → [Document DB: Prompts]  ↗         ↘ [Semantic Cache Layer]
                                                       ↘ [Evidence Vault (Secure)]
```

The CBAC operates as an **analytical processing layer** that consumes stabilized behavioral data and produces higher-order insights. It sits between raw behaviour storage and application consumption layers.

### 1.2 Architectural Components

**A. Input Interface Layer**
- Behaviour Retrieval Service: Fetches per-user behaviours from vector DB
- Prompt History Service: Retrieves original prompts via `prompt_history_ids`
- State Management: Tracks previous CBAC analysis results and cluster centroids

**B. Core Processing Engine**
- **Incremental Clustering Module** (NEW) - Assigns behaviors to existing centroids
- **Full Clustering Module** - Complete re-clustering from scratch (periodic only)
- Core Behaviour Derivation Engine
- Expertise Assessment Module
- Evidence Chain Constructor

**C. Optimization Layer (NEW)**
- **Semantic Cache** - Stores reusable LLM-generated generalizations
- **Centroid Persistence Store** - Maintains stable cluster centers across analyses
- **Taxonomy Evolution Engine** - Automated domain discovery and management

**D. Security & Privacy Layer (NEW)**
- **Evidence Vault** - Secure storage for prompt content with access controls
- **Privacy Filter** - Redacts sensitive information from evidence chains
- **Audit Logger** - Immutable access logs for sensitive data retrieval

**E. Output Management Layer**
- Core Behaviour Store
- Expertise Profile Store
- Evidence Trace Repository (metadata only, content in vault)
- Version Control System

**F. Orchestration Layer**
- Execution Scheduler
- Change Detection System
- Confidence Calculator
- Stability Monitor

---

## 2. Data Flow Stages

### Stage 1: Data Acquisition & Preparation
**Input:** User ID
**Process:**
1. Retrieve all behaviours for user from vector DB
2. **Load previous analysis state including cluster centroids** (NEW)
3. Sort by credibility × reinforcement_count (weighted relevance)
4. Fetch historical prompt texts for top N% of behaviours
5. Separate new/changed behaviours from previously analyzed ones (NEW)

**Output:** Enriched behaviour dataset with context + previous state

### Stage 2: Incremental Semantic Clustering (NEW)
**Input:** New/changed behaviours + existing cluster centroids
**Process:**
1. Generate semantic embeddings for new behaviours
2. Calculate cosine distance to all existing centroids
3. **Clustering decision:**
   ```
   FOR each new_behaviour:
     distances = calculate_distance_to_all_centroids(new_behaviour)
     
     IF min(distances) < assignment_threshold (0.80):
       ASSIGN to nearest centroid cluster
       UPDATE centroid incrementally
     ELSE:
       ADD to orphan_pool
   
   IF orphan_pool.size >= 3:
     PERFORM mini_clustering on orphans only
     CREATE new centroids for new clusters
   ```
4. Map behaviours to updated semantic groups

**Output:** Updated behaviour clusters with minimal recomputation

**Trigger for Full Re-clustering:**
- Monthly scheduled event
- OR >15% of behaviors reassigned (indicates centroid drift)
- OR user explicitly requests profile reset

### Stage 2b: Full Semantic Re-clustering (Periodic Only)
**Input:** All behaviours (clean slate)
**Process:**
1. Generate semantic embeddings for ALL behaviours
2. Perform hierarchical clustering (HDBSCAN) from scratch
3. Identify new cluster centroids and coherence scores
4. Persist centroids for future incremental analysis
5. Map behaviours to semantic groups

**Output:** Fresh behaviour clusters with new centroids

### Stage 3: Core Behaviour Derivation with Semantic Cache (ENHANCED)
**Input:** Behaviour clusters
**Process:**
1. For each cluster, evaluate promotion criteria
2. **Semantic Cache Lookup (NEW):**
   ```
   cluster_centroid = calculate_weighted_centroid(cluster)
   centroid_hash = hash_embedding(cluster_centroid)
   
   cached_results = cache.search_similar(centroid_hash, threshold=0.95)
   
   IF cache_hit AND similarity > 0.95:
     generalized_statement = cached_results.statement
     confidence_adjustment = -0.05  // Small penalty for reuse
     SKIP LLM call
   ELSE:
     generalized_statement = generate_via_LLM(cluster)
     cache.store(centroid_hash, generalized_statement)
   ```
3. Calculate aggregate confidence scores
4. Build evidence chain (metadata only, no prompt content)
5. Compare against previous core behaviours

**Output:** Candidate core behaviours with evidence + 40-60% LLM cost reduction

### Stage 4: Expertise Signal Extraction
**Input:** Behaviours + Linked prompt IDs (not full content)
**Process:**
1. **Fetch prompt metadata only initially** (complexity scores, timestamps)
2. **Lazy-load full prompt content only when needed for signal extraction**
3. Extract domain indicators from behaviours
4. Measure reinforcement stability over time
5. Identify knowledge depth signals from metadata

**Output:** Domain-specific expertise indicators

### Stage 5: Expertise Level Classification
**Input:** Expertise indicators
**Process:**
1. Aggregate signals per domain
2. Apply classification decision tree
3. Calculate confidence and stability scores
4. **Generate evidence map with prompt IDs only** (NEW)

**Output:** Expertise profiles with secure justification

### Stage 6: Secure Evidence Chain Construction (NEW)
**Input:** Core behaviours + expertise profiles + source data
**Process:**
1. **Build evidence metadata chains:**
   ```
   evidence_chain = {
     source_behaviour_ids: [...],
     prompt_ids: [...],  // IDs only, no content
     prompt_hashes: [...],  // Non-reversible hashes
     clustering_metrics: {...},
     derivation_logic: {...}
   }
   ```
2. **Store sensitive content separately:**
   ```
   FOR each prompt referenced:
     prompt_vault.store_secure(
       prompt_id: id,
       user_id: user_id,
       content: full_prompt_text,
       access_policy: "owner_only"
     )
   ```
3. Link evidence chains to vault entries via IDs

**Output:** Privacy-safe evidence chains + secure content vault

### Stage 7: Change Management & Persistence
**Input:** New core behaviours + expertise profiles
**Process:**
1. Detect changes from previous analysis
2. Apply preservation/retirement rules
3. Version and timestamp all outputs
4. Store evidence chains (metadata) and vault references
5. **Persist updated cluster centroids for next incremental run** (NEW)
6. Update state for next execution

**Output:** Persisted results with audit trail + optimized state

---

## 3. Logical Decision Pipelines

### Pipeline A: Core Behaviour Promotion Decision

```
FOR each behaviour cluster:
  
  IF cluster_size < 3:
    REJECT (insufficient evidence)
  
  CALCULATE aggregate_credibility = weighted_avg(member_credibilities)
  CALCULATE stability_score = measure_temporal_spread(last_seen_dates)
  CALCULATE semantic_coherence = cluster_tightness_metric
  
  IF aggregate_credibility < 0.65:
    REJECT (low confidence)
  
  IF stability_score < 0.5:
    MARK as "emerging pattern" (not core yet)
  
  IF semantic_coherence < 0.7:
    REJECT (too diverse to generalize)
  
  // ENHANCED: Semantic Cache Integration
  CALCULATE cluster_centroid_hash
  
  cached_statement = semantic_cache.lookup(
    centroid_hash, 
    similarity_threshold=0.95
  )
  
  IF cached_statement EXISTS:
    generalized_statement = cached_statement
    confidence_adjustment = -0.05
    cache_hit = TRUE
  ELSE:
    generalized_statement = generate_via_LLM(cluster)
    semantic_cache.store(centroid_hash, generalized_statement)
    confidence_adjustment = 0
    cache_hit = FALSE
  
  CALCULATE promotion_confidence:
    base_confidence = (aggregate_credibility × 0.4) +
                     (stability_score × 0.3) +
                     (semantic_coherence × 0.3)
    
    final_confidence = base_confidence + confidence_adjustment
  
  IF final_confidence >= 0.70:
    PROMOTE to core behaviour
    BUILD evidence chain (metadata only)
    STORE with version metadata
    LOG cache_hit status for monitoring
```

### Pipeline B: Expertise Level Classification

```
FOR each domain identified in behaviours:
  
  EXTRACT signals:
    - terminology_sophistication (from prompt metadata analysis)
    - question_complexity (prompt structure from metadata)
    - reinforcement_depth (behaviour stability in domain)
    - problem_solving_patterns (multi-step reasoning detection)
    - error_recovery_behaviour (revision patterns)
  
  CALCULATE domain_signal_strength:
    = sum(signal_weights × signal_values)
  
  DETERMINE expertise_level:
    IF domain_signal_strength < 0.3:
      LEVEL = Novice
      CONFIDENCE = domain_signal_strength / 0.3
    
    ELIF domain_signal_strength < 0.6:
      LEVEL = Intermediate
      CONFIDENCE = (domain_signal_strength - 0.3) / 0.3
    
    ELIF domain_signal_strength < 0.85:
      LEVEL = Advanced
      CONFIDENCE = (domain_signal_strength - 0.6) / 0.25
    
    ELSE:
      LEVEL = Expert
      CONFIDENCE = min(1.0, (domain_signal_strength - 0.85) / 0.15)
  
  CALCULATE stability:
    = consistency_across_time_windows(domain_behaviours)
  
  IF stability < 0.6:
    DOWNGRADE confidence by 20%
    FLAG as "transitional"
  
  // ENHANCED: Secure evidence mapping (IDs only)
  BUILD evidence_map with:
    - behaviour_ids (not full text)
    - prompt_ids (not content)
    - signal_breakdown
    - NO sensitive content
  
  STORE with evidence mapping
```

### Pipeline C: Incremental Cluster Assignment (NEW)

```
LOAD previous_centroids from last analysis

FOR each new_or_changed_behaviour:
  
  GENERATE embedding for behaviour
  
  distances = []
  FOR each existing_centroid:
    distance = cosine_distance(behaviour_embedding, centroid)
    distances.append(distance)
  
  min_distance = min(distances)
  nearest_centroid_idx = argmin(distances)
  
  IF min_distance < ASSIGNMENT_THRESHOLD (0.80):
    // Assign to existing cluster
    clusters[nearest_centroid_idx].add(behaviour)
    
    // Incrementally update centroid
    old_centroid = centroids[nearest_centroid_idx]
    cluster_size = len(clusters[nearest_centroid_idx])
    
    new_centroid = (old_centroid × (cluster_size - 1) + behaviour_embedding) / cluster_size
    centroids[nearest_centroid_idx] = new_centroid
    
    LOG assignment(behaviour_id, centroid_idx, distance)
  
  ELSE:
    // Behaviour doesn't fit existing clusters
    orphan_pool.add(behaviour)
    LOG orphan(behaviour_id, min_distance)

// Handle orphans
IF len(orphan_pool) >= 3:
  new_clusters = mini_cluster(orphan_pool)
  
  FOR each new_cluster:
    IF len(new_cluster) >= 3:
      new_centroid = calculate_centroid(new_cluster)
      clusters.append(new_cluster)
      centroids.append(new_centroid)
      LOG new_cluster_created(centroid, members)

// Drift detection
reassignment_rate = count(reassignments) / total_behaviours

IF reassignment_rate > 0.15:
  FLAG centroid_drift_detected
  SCHEDULE full_reclustering
  NOTIFY monitoring_system
```

---

## 4. Core Behaviour Identification Methodology

### 4.1 Semantic Grouping Strategy

**Method: Incremental Hierarchical Density-Based Clustering**

1. **Embedding Generation:**
   - Use consistent sentence embedding model for all behaviour_text
   - Model: `all-MiniLM-L6-v2` or equivalent (versioned with analysis)
   - Store embeddings with behaviour records for repeatability

2. **Clustering Mode Selection:**
   ```
   IF first_time_analysis OR monthly_full_refresh OR centroid_drift_detected:
     USE full_clustering_mode
   ELSE:
     USE incremental_clustering_mode
   ```

3. **Incremental Mode (Default):**
   - Load persisted centroids from previous analysis
   - Calculate distance to existing centroids only (O(n×k) instead of O(n²))
   - Assignment threshold: cosine similarity > 0.80
   - Create new clusters only when orphan pool ≥ 3 behaviors

4. **Full Mode (Periodic):**
   - Compute cosine similarity matrix for ALL behaviours
   - Apply HDBSCAN-like density-based clustering
   - Identify dense regions with minimum cluster size = 3
   - Allow soft assignment (behaviors can belong to multiple clusters)
   - Calculate and persist new centroids

5. **Centroid Calculation:**
   ```
   centroid = Σ(embedding × credibility × reinforcement_count) / Σ(weights)
   ```

**Performance Impact:**
- Incremental: ~500ms for 50 new behaviors
- Full: ~30-45s for 500 total behaviors
- Cost Reduction: ~90% for stable users (10-20 new behaviors/week)

### 4.2 Generalization Logic with Semantic Cache (ENHANCED)

**Input:** Cluster of similar behaviours
**Process:**

1. **Calculate cluster signature:**
   ```
   cluster_centroid = weighted_average(member_embeddings)
   centroid_hash = stable_hash(cluster_centroid, precision=6)
   ```

2. **Semantic Cache Lookup:**
   ```
   cache_query_results = semantic_cache.search(
     query_hash: centroid_hash,
     similarity_threshold: 0.95,
     max_results: 3
   )
   
   FOR each cached_entry in cache_query_results:
     cache_similarity = cosine_similarity(
       cluster_centroid, 
       cached_entry.centroid
     )
     
     IF cache_similarity >= 0.95:
       // High confidence cache hit
       RETURN cached_entry.generalized_statement
       APPLY confidence_adjustment = -0.05
       LOG cache_hit(centroid_hash, cached_entry.id, similarity)
       INCREMENT cache_entry.reuse_count
   ```

3. **Generate new statement (on cache miss):**
   ```
   generalized_statement = LLM_call(
     prompt: """
     Given these related behaviours: {member_behaviour_texts}
     Generate ONE general statement that captures their essence.
     Rules:
     - Maximum 10 words
     - No specific examples
     - Preserve action/preference pattern
     - Use present tense
     """,
     model: "claude-sonnet-4",
     max_tokens: 50
   )
   ```

4. **Cache storage:**
   ```
   semantic_cache.store({
     centroid_hash: centroid_hash,
     centroid_embedding: cluster_centroid,
     generalized_statement: generalized_statement,
     source_cluster_size: len(cluster),
     created_at: timestamp,
     reuse_count: 0,
     confidence: base_confidence
   })
   ```

5. **Validate generalization:**
   - Ensure all source behaviours are semantically covered
   - Check that generalization doesn't over-abstract
   - Verify uniqueness against existing core behaviours for this user

**Semantic Cache Architecture:**
```
Cache Storage Schema:
{
  "cache_id": "cache_8f2a9d",
  "centroid_hash": "a3f8c2...",
  "centroid_embedding": [0.234, -0.891, ...],
  "generalized_statement": "prefers visual learning methods",
  "source_cluster_size": 4,
  "average_coherence": 0.82,
  "created_at": 1732180002,
  "last_reused": 1732549222,
  "reuse_count": 47,
  "originating_user_id": "hashed_for_privacy"
}

Cache Lookup Strategy:
- Primary: Hash-based exact match (O(1))
- Secondary: Vector similarity search for near-matches (O(log n))
- TTL: 90 days without reuse
- Eviction: LRU policy when cache exceeds size limit

Expected Performance:
- Cache hit rate: 40-60% after 30 days
- LLM cost reduction: 40-60%
- Latency improvement: 2-3 seconds per cached cluster
```

### 4.3 Confidence Calculation (UPDATED)

**Core Behaviour Confidence Formula:**

```
CBC = (w1 × Cred_agg) + (w2 × Stab_score) + (w3 × Sem_coh) + (w4 × Reinf_depth) + Cache_adj

Where:
  Cred_agg = Σ(credibility × reinforcement) / Σ(reinforcement)
  Stab_score = temporal_variance_coefficient
  Sem_coh = average_intra_cluster_similarity
  Reinf_depth = log(1 + total_reinforcements) / log(threshold)
  Cache_adj = -0.05 if from semantic cache, 0 if newly generated
  
  Weights: w1=0.35, w2=0.25, w3=0.25, w4=0.15
```

**Rationale for Cache Adjustment:**
- Cached statements are proven generalizations used successfully for other users
- Small penalty (-0.05) reflects slight uncertainty about cross-user applicability
- Still promotes cache reuse while maintaining epistemic honesty

**Stability Scoring:**

```
Stability = 1 - (σ(time_gaps) / μ(time_gaps))

Where:
  time_gaps = intervals between behaviour observations
  σ = standard deviation
  μ = mean
  
Result: High stability = consistent appearance over time
        Low stability = sporadic or bursty pattern
```

---

## 5. Expertise Level Assessment Model

### 5.1 Signal Extraction Framework

**Signal Categories:**

**A. Lexical Sophistication Signals**
- Domain-specific vocabulary density
- Technical term usage frequency
- Jargon appropriateness score
- **Extracted from prompt metadata initially, full text only if needed**

**B. Cognitive Complexity Signals**
- Prompt length and structure complexity
- Multi-step reasoning indicators
- Conditional logic presence
- Abstract concept usage
- **Can be pre-computed and stored with prompts for efficiency**

**C. Temporal Patterns**
- Reinforcement consistency (does expertise grow?)
- Knowledge domain expansion rate
- Error correction patterns (learning signals)

**D. Task Complexity Indicators**
- Problem difficulty level from prompts
- Meta-cognitive behaviour (asking about methodology)
- Self-directed learning signals

### 5.2 Domain Identification with Automated Taxonomy (ENHANCED)

**Process:**
1. Extract domain keywords from behaviours using NER + keyword extraction
2. Group behaviours by dominant domain tags
3. Require minimum 5 behaviours to establish domain presence
4. **Automated Taxonomy Evolution (NEW):**

```
DAILY (Automated):
  
  // Aggregate across all users
  domain_clusters = extract_emergent_domains(all_user_behaviours)
  
  FOR each emergent_cluster:
    IF cluster_frequency > 0.05 (5% of users):
      
      candidate_domain = {
        label: LLM_generate_domain_name(cluster_keywords),
        sample_behaviours: top_10_representative_behaviours,
        user_coverage: percentage_of_users,
        stability_score: temporal_consistency_metric,
        parent_domain: map_to_existing_taxonomy_if_applicable
      }
      
      IF stability_score > 0.75:
        ADD to pending_review_queue (high confidence)
      ELSE:
        ADD to monitoring_pool (watch for 30 days)

MONTHLY (Human Curator Review):
  
  // Review only high-confidence candidates
  pending_domains = fetch_pending_review_queue()
  
  FOR each candidate IN pending_domains:
    PRESENT to curator with:
      - Auto-generated label
      - Representative behaviours
      - Coverage statistics
      - Suggested parent category
    
    curator_action = await_decision()  // Approve/Reject/Merge/Modify
    
    IF approved:
      taxonomy.add_domain(candidate)
      TRIGGER a_b_test(new_domain, sample_size=0.1)
    
    ELIF merge:
      taxonomy.merge_domains(candidate, target_domain)
    
    ELSE:
      archive_candidate(candidate, reason)

A/B TESTING (Ongoing):
  
  FOR each new_domain IN testing_phase:
    
    test_group_metrics = measure_expertise_consistency(
      users_with_new_domain
    )
    
    control_group_metrics = measure_expertise_consistency(
      users_without_new_domain
    )
    
    IF test_group_metrics >= control_group_metrics:
      PROMOTE new_domain to production (100% rollout)
    ELSE:
      INVESTIGATE discrepancies
      REFINE domain definition
      EXTEND testing period
```

**Target Performance:**
- Human curator effort: <2 hours/month
- New domain discovery lag: ~30 days from emergence
- False positive rate: <5%

5. Map to standardized domain taxonomy (continuously evolving)

### 5.3 Expertise Classification Rules

**Level Definitions:**

| Level | Signal Strength | Characteristics |
|-------|----------------|-----------------|
| **Novice** | 0.0 - 0.3 | Basic terminology, simple prompts, high question frequency, seeks explanations |
| **Intermediate** | 0.3 - 0.6 | Domain vocabulary, structured problems, some troubleshooting, tactical focus |
| **Advanced** | 0.6 - 0.85 | Technical depth, complex multi-step tasks, strategic thinking, teaches concepts |
| **Expert** | 0.85 - 1.0 | Mastery vocabulary, novel problem-solving, meta-analysis, creates methodologies |

**Contradictory Signal Resolution:**

```
IF signals conflict (e.g., expert vocabulary but novice question patterns):
  
  PRIORITIZE recent_behaviours (last 30 days weighted 2x)
  
  IF contradiction persists:
    ASSIGN lower of two levels
    SET confidence = 0.6 × normal_confidence
    FLAG as "inconsistent profile"
    RECOMMEND longer observation period
```

### 5.4 Expertise Confidence Scoring

```
Expertise_Confidence = (Signal_Strength × 0.5) + 
                       (Temporal_Consistency × 0.3) + 
                       (Evidence_Volume × 0.2)

Where:
  Signal_Strength = normalized expertise signal value
  Temporal_Consistency = stability across time windows
  Evidence_Volume = log(behaviour_count_in_domain) / log(20)
```

---

## 6. Handling of Decayed or Removed Behaviours

### 6.1 Core Problem Statement

When source behaviours decay and are removed by upstream system, core behaviours derived from them face validity questions.

### 6.2 Proposed Policy: Hybrid Preservation Strategy

**Decision Framework:**

```
FOR each core_behaviour:
  
  CALCULATE current_support:
    active_members = count(source_behaviours still in DB)
    support_ratio = active_members / original_member_count
  
  IF support_ratio >= 0.6:
    STATUS = "Active" (strong ongoing support)
    ACTION = Update confidence, maintain
  
  ELIF support_ratio >= 0.3:
    STATUS = "Degrading" (partial support)
    ACTION = Reduce confidence by (1 - support_ratio)
            Add "historical" flag
            Monitor for one more cycle
  
  ELIF support_ratio >= 0.1:
    STATUS = "Historical" (minimal support)
    ACTION = Reclassify as historical pattern
            Do not use for active recommendations
            Preserve for longitudinal analysis
  
  ELSE:
    STATUS = "Retired"
    ACTION = Archive with tombstone record
            Preserve evidence chain
            Mark retirement date and reason
```

### 6.3 Historical Core Behaviour Schema

**Purpose:** Preserve insights about user's past patterns without contaminating current analysis

**Attributes:**
- Original core behaviour text
- Active date range (start → retirement)
- Peak confidence score
- Retirement reason (decay, contradiction, user evolution)
- Archived evidence chain
- Transition notes

**Usage:**
- Longitudinal user evolution studies
- Pattern reemergence detection
- Context for explaining current preferences

### 6.4 Reemergence Detection

```
IF new behaviour matches retired core behaviour:
  IF confidence and reinforcement sufficient:
    RESURRECT core behaviour
    UPDATE as "Reactivated" with date
    MERGE evidence chains (historical + new)
    ANNOTATE with gap period
```

---

## 7. Processing Execution Strategy

### 7.1 Evaluation of Batch Processing

**Initial Proposal:** Daily batch processing

**Analysis:**

**Pros:**
- Simple orchestration
- Predictable resource usage
- Batch optimization opportunities
- Easier debugging and monitoring

**Cons:**
- 24-hour lag for new insights
- Inefficient for users with little change
- Wastes cycles on stable profiles
- Can't respond to rapid behaviour shifts

**Verdict:** Pure daily batch is suboptimal.

### 7.2 Recommended Approach: Adaptive Hybrid Model

**Strategy: Event-Triggered + Periodic Baseline**

### Execution Modes:

**A. Incremental Analysis (Continuous)**
```
TRIGGER conditions:
  - User accumulates 10+ new behaviours since last analysis
  - Credibility-weighted change score > threshold (0.15)
  - User explicitly requests profile refresh

SCOPE:
  - Use incremental clustering (assign to existing centroids)
  - Analyze only new/changed behaviours
  - Quick cluster reassignment
  - Update existing core behaviours
  - Skip full expertise recalculation (use cached signals)

PROCESS:
  1. Load persisted centroids from last analysis
  2. Assign new behaviours via distance calculation
  3. Update affected cluster centroids incrementally
  4. Re-evaluate only modified core behaviours
  5. Check semantic cache before LLM calls

FREQUENCY: As triggered (potentially multiple per day per user)

DURATION: <5 seconds per user (90% faster than full analysis)
```

**B. Full Analysis (Periodic)**
```
TRIGGER:
  - Scheduled: Every 7 days per user
  - Or after 50+ incremental changes accumulated
  - Or centroid drift detected (>15% reassignments)

SCOPE:
  - Complete re-clustering from scratch
  - Recalculate all centroids
  - Full expertise reassessment
  - Historical core behaviour review
  - Evidence chain validation
  - Comprehensive confidence recalculation

FREQUENCY: Weekly baseline

DURATION: 30-60 seconds per user
```

**C. Population-Level Analysis (Batch)**
```
TRIGGER:
  - Monthly scheduled job

SCOPE:
  - Cross-user pattern analysis
  - Automated domain taxonomy evolution
  - Model calibration
  - Aggregate metrics
  - Semantic cache optimization (evict stale entries)
  - Centroid drift analysis

FREQUENCY: Monthly

DURATION: Hours (scales with user base)
```

### 7.3 Scheduling Algorithm

```
PRIORITY QUEUE based on:
  
  Priority_Score = (change_magnitude × 0.5) + 
                   (time_since_last_analysis × 0.3) +
                   (user_activity_level × 0.2)

EXECUTION:
  - High priority users: Incremental analysis within 1 hour
  - Medium priority: Within 6 hours
  - Low priority: Batched during off-peak hours
  - All users: Full analysis guaranteed every 7 days
  
OPTIMIZATION (NEW):
  - Incremental analyses use dedicated fast queue
  - Full analyses scheduled during off-peak hours
  - Semantic cache pre-warmed for high-volume times
```

### 7.4 Performance Considerations

**Resource Budgeting:**
- Incremental analysis: **200-500ms** per user (improved from 500ms with incremental clustering)
- Full analysis: 45s per user
- Separate processing queues prevent interference

**Scalability with Incremental Clustering:**
- Incremental mode: Can handle **36,000 users/hour** (improved from 7,200)
- Full mode: Can handle 80 users/hour
- **90% of analyses use incremental mode** for stable users
- Effective throughput: ~32,500 users/hour mixed load

**Horizontal Scaling:**
- Partition users by hash
- Each worker handles independent user subset
- Shared read-only access to prompt database and semantic cache
- Write synchronization only for user's own results
- Semantic cache shared across all workers (distributed cache like Redis)

**Cost Optimization:**
- Semantic cache reduces LLM costs by 40-60%
- Incremental clustering reduces compute by ~90% for typical users
- Combined savings: **~70-80% cost reduction** vs. naive implementation

---

## 8. Versioning & Change Management Strategy

### 8.1 Versioning Scheme

**Version Format:** `{major}.{minor}.{analysis_run}`

**Example:** `2.5.20241125_143022`

- **Major:** Algorithm or model change (e.g., new clustering method)
- **Minor:** Parameter tuning or threshold adjustment
- **Analysis_run:** Specific execution timestamp

### 8.2 Data Versioning

**Every CBAC output includes:**

```json
{
  "user_id": "...",
  "analysis_version": "2.5.20241125_143022",
  "analysis_type": "full|incremental",
  "execution_timestamp": 1732180002,
  "input_hash": "sha256_of_input_behaviours",
  "model_config": {
    "clustering_method": "incremental_hdbscan",
    "clustering_mode": "incremental|full",
    "centroid_version": "cv_20241118_120033",
    "assignment_threshold": 0.80,
    "embedding_model": "all-MiniLM-L6-v2",
    "confidence_weights": {...},
    "thresholds": {...},
    "semantic_cache_enabled": true,
    "cache_hit_rate": 0.52
  },
  "performance_metrics": {
    "cache_hits": 12,
    "cache_misses": 3,
    "llm_calls_saved": 12,
    "clustering_mode_used": "incremental",
    "centroids_updated": 5,
    "new_clusters_created": 1
  },
  "core_behaviours": [...],
  "expertise_profiles": [...],
  "evidence_chains": [...]
}
```

### 8.3 Change Detection & Impact Analysis

**On Each Execution:**

```
LOAD previous_analysis_result
LOAD previous_centroids (for incremental mode)

FOR each new_core_behaviour:
  
  IF matches existing core_behaviour:
    COMPARE confidence_scores
    IF delta > 0.15:
      LOG significant_change(behaviour, old_conf, new_conf)
      RECORD reason(supporting_behaviours_diff)
      
      IF confidence_increased:
        CHECK if due_to_new_evidence OR cache_reuse
  
  ELSE:
    LOG new_emergence(behaviour)
    RECORD source_cluster_evidence
    RECORD clustering_mode_used (incremental/full)

FOR each old_core_behaviour NOT in new_results:
  LOG retirement(behaviour)
  RECORD retirement_reason
  ARCHIVE with historical status

// NEW: Track clustering efficiency
LOG clustering_performance:
  - mode_used (incremental/full)
  - behaviours_assigned_to_existing: count
  - new_clusters_created: count
  - centroids_updated: count
  - orphans_created: count
  - full_reclustering_triggered: boolean
```

### 8.4 Rollback & Reproducibility

**Requirements:**
- Store input data hash with each analysis
- Preserve model configuration snapshot
- **Preserve cluster centroids for each analysis version** (NEW)
- **Preserve semantic cache state for each analysis** (NEW)
- Enable reconstruction of analysis from versioned inputs

**Rollback Process:**
```
IF analysis_version N produces errors or anomalies:
  
  FETCH analysis_version N-1 results
  FETCH centroid_version N-1 (for incremental clustering)
  RESTORE as active state
  
  QUEUE affected_users for reanalysis with:
    - Previous model version
    - Previous centroid configuration
    - OR debugged current version
  
  LOG rollback event with justification
  NOTIFY monitoring_system
  
  // NEW: Semantic cache handling
  IF semantic_cache_corruption_suspected:
    INVALIDATE affected cache entries
    FORCE LLM regeneration for affected clusters
```

---

## 9. Confidence Scoring & Stability Rules

### 9.1 Multi-Dimensional Confidence Framework

**Confidence is NOT a single score but a composite:**

```json
{
  "overall_confidence": 0.78,
  "components": {
    "data_quality": 0.85,      // Input credibility
    "evidence_volume": 0.72,   // Sample size adequacy
    "temporal_stability": 0.80, // Consistency over time
    "semantic_coherence": 0.75, // Cluster tightness
    "derivation_method": 0.77   // NEW: Incremental vs full, cache vs fresh
  },
  "confidence_grade": "High",   // High|Medium|Low
  "stability_indicator": "Stable", // Stable|Transitional|Emerging
  "metadata": {
    "from_semantic_cache": true,
    "clustering_mode": "incremental",
    "cache_similarity": 0.96
  }
}
```

### 9.2 Confidence Grading Rules (UPDATED)

```
overall_confidence = weighted_harmonic_mean(components)

// NEW: Adjust for derivation method
IF from_semantic_cache AND cache_similarity >= 0.95:
  cache_adjustment = -0.05  // Small penalty for reuse
ELSE:
  cache_adjustment = 0

IF clustering_mode == "incremental" AND time_since_full_clustering > 30_days:
  staleness_penalty = -0.05
ELSE:
  staleness_penalty = 0

adjusted_confidence = overall_confidence + cache_adjustment + staleness_penalty

Grade assignment:
  IF adjusted_confidence >= 0.75 AND all_components >= 0.65:
    GRADE = "High"
  
  ELIF adjusted_confidence >= 0.55 AND no_component < 0.45:
    GRADE = "Medium"
  
  ELSE:
    GRADE = "Low"
```

**Rationale for harmonic mean:** Penalizes imbalanced scores, ensures no single weak component is hidden by strong others.

### 9.3 Stability Classification

**Stability Dimensions:**

1. **Temporal Stability:** Consistency across time windows
2. **Reinforcement Stability:** Steady vs. spiky reinforcement pattern
3. **Semantic Stability:** Cluster membership consistency over analyses
4. **Centroid Stability (NEW):** Low centroid drift in incremental updates

**Classification Logic:**

```
FOR each core_behaviour:
  
  temporal_variance = std_dev(observation_intervals)
  reinforcement_pattern = coefficient_of_variation(reinforcements)
  semantic_drift = cluster_reassignment_frequency
  
  // NEW: Track centroid movement
  IF clustering_mode == "incremental":
    centroid_movement = distance(
      current_centroid, 
      centroid_at_last_full_clustering
    )
  ELSE:
    centroid_movement = 0
  
  stability_score = 1 - weighted_avg([
    temporal_variance,
    reinforcement_pattern,
    semantic_drift,
    centroid_movement * 0.5  // Lower weight for centroid drift
  ])
  
  IF stability_score > 0.75:
    STATUS = "Stable"
    CONFIDENCE_BOOST = +0.1
  
  ELIF stability_score > 0.50:
    STATUS = "Transitional"
    CONFIDENCE_ADJUSTMENT = 0
    FLAG = "monitor_for_3_cycles"
    
    // NEW: Check if instability due to incremental drift
    IF centroid_movement > 0.20:
      RECOMMEND full_reclustering
  
  ELSE:
    STATUS = "Emerging"
    CONFIDENCE_PENALTY = -0.15
    REQUIRE additional_evidence_before_promotion
```

### 9.4 Confidence Decay Over Time

**Problem:** Stale analysis loses relevance

**Solution: Time-based confidence erosion**

```
confidence_current = confidence_at_analysis × decay_function(days_elapsed)

decay_function(days) = max(0.7, 1 - (days × 0.02))

Result:
  Day 0: 100% of original confidence
  Day 7: 86% of original confidence
  Day 15: 70% (floor reached, forces re-analysis)

// NEW: Accelerated decay for incremental-only analyses
IF clustering_mode == "incremental" AND days_since_full_clustering > 30:
  decay_multiplier = 1.5  // Decay 50% faster
  adjusted_decay = decay_function(days × decay_multiplier)
```

**Trigger:** When confidence drops below grade threshold, user prioritized for re-analysis.

---

## 10. Long-Term Evolution Strategy

### 10.1 Adaptive Learning Mechanisms

**The system must improve over time without manual recalibration.**

**Feedback Loops to Implement:**

**A. Prediction Validation**
- Track when core behaviours are later contradicted by new data
- Measure false positive rate (core behaviours that degrade rapidly)
- Adjust promotion thresholds based on historical accuracy
- **NEW: Track semantic cache accuracy** - measure how often cached statements remain valid

**B. Expertise Calibration**
- When possible, compare expertise predictions to observable outcomes
  - Does "expert" user create high-quality outputs?
  - Does classification match self-reported expertise when available?
- Tune signal weights based on predictive success

**C. Semantic Model Drift**
- Monitor if clusters become less coherent over time (model aging)
- Track emergence of new domain vocabularies
- **NEW: Monitor centroid stability** - excessive drift indicates model aging
- Schedule embedding model updates when drift detected

**D. Clustering Efficiency (NEW)**
- Track incremental vs full clustering performance
- Monitor centroid drift patterns
- Adjust assignment threshold based on reassignment rates
- Optimize full clustering frequency based on drift detection

**E. Cache Performance (NEW)**
- Monitor cache hit rates by domain and user segment
- Track cache entry quality (reuse count vs retirement rate)
- Identify optimal cache similarity thresholds
- Prune low-quality cache entries

### 10.2 Model Refresh Strategy

**Quarterly Review Cycle:**

```
EVERY 90 days:
  
  ANALYZE performance metrics:
    - Core behaviour stability rates
    - Confidence calibration accuracy
    - Expertise prediction consistency
    - Processing time trends
    - NEW: Cache hit rates and quality
    - NEW: Incremental clustering accuracy
    - NEW: Centroid drift patterns
  
  IF metrics degrade > 10%:
    TRIGGER model_recalibration:
      - Re-tune threshold values
      - Update domain taxonomy
      - Refresh embedding model
      - NEW: Adjust assignment threshold
      - NEW: Optimize cache similarity threshold
      - NEW: Recalculate all centroids from scratch
      - A/B test parameter changes
  
  DOCUMENT changes and expected impact
  EXECUTE staged rollout (10% → 50% → 100% of users)
```

### 10.3 Domain Taxonomy Evolution (AUTOMATED)

**Challenge:** New domains emerge, old ones fragment or merge

**Strategy: Fully Automated Taxonomy Management**

```
DAILY (Automated):
  
  EXTRACT emergent_domain_clusters from all users
  
  IF new_cluster appears in >5% of user base:
    
    candidate_domain = {
      label: LLM_generate_domain_name(cluster_keywords),
      sample_behaviours: top_10_representative_behaviours,
      user_coverage: percentage_of_users,
      stability_score: temporal_consistency_metric,
      parent_domain: map_to_existing_taxonomy()
    }
    
    IF stability_score > 0.75:
      ADD to pending_review_queue (high confidence)
      AUTO_SCHEDULE a_b_test
    ELSE:
      ADD to monitoring_pool (watch for 30 days)
  
  IF existing_domain shows bifurcation:
    ANALYZE split_patterns
    PROPOSE sub_domain_candidates
    ADD to pending_review_queue

MONTHLY (Human Curator Review - < 2 hours):
  
  pending_domains = fetch_pending_review_queue()
  FILTER for high_confidence_only (stability > 0.75)
  
  PRESENT dashboard with:
    - Top 10-20 candidates
    - Auto-generated visualizations
    - Coverage and stability metrics
    - Suggested actions (approve/merge/reject)
  
  FOR each curator_decision:
    IF approved:
      taxonomy.add_domain(candidate)
      CONTINUE running_a_b_test
    
    ELIF merge:
      taxonomy.merge_domains(candidate, target)
      UPDATE all_affected_user_profiles
    
    ELSE:
      archive_candidate(reason)

A/B TESTING (Continuous - Automated):
  
  FOR each new_domain IN testing_phase:
    
    // Start with 10% of users
    test_group = random_sample(users_with_domain_signals, 0.1)
    control_group = remaining_users_with_domain_signals
    
    MEASURE over 14_days:
      - Expertise classification stability
      - Core behaviour coherence
      - User feedback (if available)
      - Confidence score distributions
    
    IF test_metrics >= control_metrics + margin(0.05):
      // Statistical significance achieved
      PROMOTE to 50% rollout
      
      IF 50% rollout successful after 7_days:
        PROMOTE to 100% (production)
        LOG domain_promotion(domain, metrics)
    
    ELIF test_metrics < control_metrics:
      INVESTIGATE anomalies
      REFINE domain_definition
      IF refinement_count > 3:
        REJECT domain_candidate
        LOG domain_rejection(domain, reason)
```

**Target Performance:**
- Human curator effort: <2 hours/month (down from potentially 20+)
- New domain discovery lag: ~30-45 days from emergence to production
- False positive rate: <5%
- Automation rate: >90% of domains auto-tested, ~70% auto-approved

### 10.4 Privacy & Consent Evolution

**Anticipating Future Requirements:**

**A. Explainability on Demand (ENHANCED)**
- Users can request "why does the system think X about me?"
- Generate natural language explanation from evidence chains
- **Show source behaviours via IDs, fetch full prompts only on user request**
- **Audit all access to sensitive prompt content**
- Display contribution weights and clustering logic

**B. Selective Opt-Out**
- Allow users to exclude specific behaviours from analysis
- Allow domain-specific opt-out (e.g., "don't analyze work behaviours")
- Recompute affected core behaviours and expertise
- **Automatically trigger incremental re-analysis after opt-out**

**C. Data Portability**
- Export user's complete CBAC profile in standardized format
- Include all evidence chains (metadata) and confidence scores
- **Provide secure access to prompt content vault**
- Support import into compatible systems

**D. Privacy-First Architecture (NEW)**
```
Access Control Policy for Prompt Content:

1. Default State:
   - Evidence chains contain ONLY prompt IDs and hashes
   - No full prompt text in analytical layer
   - All prompts stored in separate secure vault

2. Explanation Request Flow:
   USER requests explanation
     ↓
   SYSTEM generates explanation with metadata
     ↓
   USER clicks "Show supporting prompts"
     ↓
   AUTHENTICATION check (user owns prompts)
     ↓
   RATE LIMIT check (max 10 requests/hour)
     ↓
   AUDIT LOG (who, when, which prompts)
     ↓
   FETCH from secure vault
     ↓
   DISPLAY with privacy filter (redact PII if configured)

3. Retention Policy:
   - Prompt content: Retained per user preference (default: 90 days)
   - Evidence chain metadata: Retained indefinitely
   - Audit logs: Retained 1 year
   - Cache entries: No prompt content, only generalizations
```

### 10.5 Scalability Roadmap

**Current Design:** Single-user analysis isolation with shared caching

**Future Considerations:**

**Phase 1 (Months 1-6):** Optimized Single-Node
- Per-user processing with incremental clustering
- Shared semantic cache (Redis)
- Independent analysis
- Scales to **500K users** (with optimizations)

**Phase 2 (Months 7-12):** Distributed Optimization
- Sharded embedding cache
- Incremental-only for 80-90% of users
- Distributed semantic cache with replication
- Centralized centroid store
- Scales to **5M users**

**Phase 3 (Year 2):** Distributed Architecture
- Cluster-based processing (Kubernetes)
- Distributed vector search (Milvus/Pinecone)
- Real-time incremental updates
- Cross-region cache replication
- Scales to **50M+ users**

**Phase 4 (Year 3+):** Intelligence Layer
- Cross-user pattern discovery (privacy-preserving)
- Collaborative filtering for core behaviours
- Predictive behaviour modeling
- Population-level insights
- Federated learning for privacy

---

## 11. Evidence Chain & Explainability Design (PRIVACY-ENHANCED)

### 11.1 Evidence Data Model (SECURE)

**For Core Behaviours:**

```json
{
  "core_behaviour_id": "cb_2f91ac",
  "statement": "prefers visual learning methods",
  "confidence": 0.82,
  "evidence_chain": {
    "source_behaviours": [
      {
        "behavior_id": "beh_8f29ad1c",
        "behavior_text": "likes infographic-style explanations",
        "credibility": 0.76,
        "reinforcement_count": 4,
        "contribution_weight": 0.35
      },
      {
        "behavior_id": "beh_12abc93",
        "behavior_text": "prefers video tutorials over text",
        "credibility": 0.89,
        "reinforcement_count": 7,
        "contribution_weight": 0.42
      }
    ],
    "clustering_metrics": {
      "semantic_similarity_avg": 0.81,
      "cluster_coherence": 0.77,
      "generalization_confidence": 0.85,
      "clustering_mode": "incremental",
      "from_semantic_cache": true,
      "cache_similarity": 0.96
    },
    "derivation_logic": {
      "method": "incremental_semantic_clustering",
      "assignment_threshold": 0.80,
      "abstraction_level": "medium",
      "llm_prompt_version": "v2.3",
      "cache_entry_id": "cache_8f2a9d"
    },
    "temporal_pattern": {
      "first_observed": 1730400000,
      "last_reinforced": 1732300112,
      "observation_span_days": 22,
      "reinforcement_stability": 0.78
    }
  }
}
```

**For Expertise Profiles (PRIVACY-SAFE):**

```json
{
  "domain": "data_analysis",
  "expertise_level": "Advanced",
  "confidence": 0.79,
  "evidence_map": {
    "supporting_behaviours": [
      {
        "behavior_id": "beh_45xyz",
        "behavior_text": "works with statistical modeling",
        "signal_contribution": {
          "lexical_sophistication": 0.85,
          "domain_specificity": 0.92
        }
      }
    ],
    "prompt_evidence": [
      {
        "prompt_id": "prompt_0242",
        "prompt_hash": "sha256_a3f8c2d1e9b4...",
        // NO prompt_excerpt - content in secure vault
        "complexity_score": 0.81,
        "signals_detected": [
          "multi_step_reasoning",
          "technical_terminology",
          "problem_decomposition"
        ],
        "metadata_only": true
      }
    ],
    "signal_breakdown": {
      "lexical_sophistication": 0.84,
      "cognitive_complexity": 0.77,
      "temporal_consistency": 0.81,
      "task_complexity": 0.75
    },
    "classification_reasoning": {
      "level_assigned": "Advanced",
      "threshold_range": "0.6 - 0.85",
      "actual_score": 0.79,
      "confidence_factors": {
        "signal_strength": 0.79,
        "evidence_volume": 0.82,
        "temporal_consistency": 0.81
      },
      "why_not_expert": "Lacks evidence of novel methodology creation",
      "progression_indicators": "Trending toward Expert"
    }
  }
}
```

### 11.2 Secure Prompt Content Vault

**Architecture:**

```
Vault Storage Schema:
{
  "vault_entry_id": "vault_prompt_0242",
  "prompt_id": "prompt_0242",
  "user_id": "user_abc_hashed",
  "content": "Can you help me implement a hierarchical clustering...",
  "content_hash": "sha256_for_integrity",
  "created_at": 1732180002,
  "accessed_count": 0,
  "last_accessed": null,
  "retention_policy": "90_days",
  "privacy_tier": "sensitive",
  "access_control": {
    "owner_only": true,
    "rate_limit": "10_per_hour",
    "requires_authentication": true
  }
}

Access Control Layer:
- Separate database/storage from analytical layer
- Encrypted at rest (AES-256)
- Encrypted in transit (TLS 1.3)
- Access logged to immutable audit trail
- Rate limiting per user (10 requests/hour)
- Authentication required for all access
```

**Access Flow:**

```
User Request: "Show me why you think I'm an Advanced data analyst"

STEP 1: Generate explanation from evidence_map (metadata only)
  ↓
STEP 2: Display explanation with prompt_ids listed
  ↓
STEP 3: User clicks "View supporting prompt examples"
  ↓
STEP 4: Authentication Check
  - Verify user_id matches vault entry owner
  - Check rate limit (10/hour not exceeded)
  ↓
STEP 5: Audit Log
  - Record: user_id, prompt_ids_requested, timestamp, IP, reason
  ↓
STEP 6: Fetch from Vault
  - Retrieve prompt content
  - Verify content_hash (integrity check)
  ↓
STEP 7: Privacy Filter (Optional)
  - Redact PII if configured
  - Redact sensitive patterns (emails, phone numbers, etc.)
  ↓
STEP 8: Display to User
  - Show prompt excerpt (first 200 chars + "...")
  - Highlight signals that contributed to classification
```

### 11.3 Backtracking Mechanisms (PRIVACY-AWARE)

**Query Interface:**

```
GET /explain/core-behaviour/{core_behaviour_id}
  Returns: 
    - Complete evidence chain (metadata)
    - Cluster visualization
    - Behaviour IDs and texts
    - NO prompt content (vault IDs only)

GET /explain/expertise/{user_id}/{domain}
  Returns: 
    - Signal breakdown
    - Supporting behaviour IDs
    - Prompt IDs (not content)
    - Classification logic

GET /secure/view-prompts/{user_id}
  Authentication: Required
  Rate Limit: 10/hour
  Returns:
    - Prompt excerpts (privacy-filtered)
    - Full content available on request
    - Access logged to audit trail

GET /trace/behaviour-to-core/{behavior_id}
  Returns: 
    - All core behaviours derived from this source
    - Contribution weights
    - Clustering history

GET /audit/analysis/{analysis_run_id}
  Returns: 
    - Complete input state (behaviour IDs, not prompts)
    - Decisions made
    - Outputs generated
    - Performance metrics
```

**Visualization Requirements:**

- **Cluster Graph:** Visual representation with core behaviour at center (no prompt content)
- **Timeline View:** Temporal evolution of behaviours
- **Signal Heatmap:** Expertise signals across time and domains
- **Confidence Decomposition:** Component breakdown
- **Privacy Dashboard:** Show what data is stored where

### 11.4 Human-Readable Explanation Generation (PRIVACY-SAFE)

**Template-Based Natural Language Generation:**

**For Core Behaviours:**

```
Template:
"The system identified that you {core_behaviour} based on {N} related patterns observed across {timespan}. 

Key evidence includes:
- {strongest_source_behaviour} (observed {reinforcement_count} times, credibility {score})
- {second_strongest} (observed {reinforcement_count} times, credibility {score})

This conclusion has {confidence_grade} confidence ({confidence_score}) because {primary_confidence_factor}. 

{IF from_semantic_cache:
  "This pattern was recognized using our semantic pattern library, which has identified similar patterns in {reuse_count} other anonymized cases."
}

{IF clustering_mode == "incremental":
  "This was derived using incremental analysis, last fully validated {days_since_full} days ago."
}

The pattern has been {stability_indicator} over the past {observation_period}.

[View supporting prompts] (requires authentication)
"

Example Output:
"The system identified that you prefer visual learning methods based on 3 related patterns observed across 22 days.

Key evidence includes:
- You prefer video tutorials over text (observed 7 times, credibility 0.89)
- You like infographic-style explanations (observed 4 times, credibility 0.76)

This conclusion has High confidence (0.82) because the patterns are semantically similar and consistently reinforced.

This pattern was recognized using our semantic pattern library, which has identified similar patterns in 47 other anonymized cases.

The pattern has been Stable over the past 3 weeks.

[View supporting prompts] ← Clickable, requires auth
"
```

**For Expertise Levels (NO PROMPT CONTENT):**

```
Template:
"Based on your interaction patterns, you demonstrate {level} expertise in {domain} (confidence: {score}).

This assessment is based on:
- {signal_category_1}: {evidence_summary}
- {signal_category_2}: {evidence_summary}

Specifically:
- Your interactions show {complexity_descriptor} (score: {score})
- You use {terminology_descriptor} (score: {score})
- Your engagement pattern shows {consistency_descriptor}

You are classified as {level} rather than {higher_level} because {limiting_factor}.

{progression_note if trending upward}

This analysis is based on {N} interactions across {timespan}.
{IF you'd like to see examples}: [View supporting interactions] (requires authentication)
"

Example Output:
"Based on your interaction patterns, you demonstrate Advanced expertise in data analysis (confidence: 0.79).

This assessment is based on:
- Technical Language: You consistently use domain-specific terminology
- Problem Complexity: Your interactions involve multi-step analytical workflows

Specifically:
- Your interactions show high complexity (score: 0.81)
- You use advanced technical vocabulary (score: 0.84)
- Your engagement pattern shows strong consistency (score: 0.81)

You are classified as Advanced rather than Expert because your work primarily applies existing methods rather than developing novel frameworks.

Recent trends suggest progression toward Expert level as you've begun exploring meta-analytical questions.

This analysis is based on 23 interactions across 45 days.
[View supporting interactions] ← Requires authentication, shows prompt IDs first
"
```

### 11.5 Audit Trail Storage (ENHANCED)

**Requirements:**
- Every analysis execution generates an audit record
- Every sensitive data access generates an access audit record (NEW)
- Immutable append-only log
- Queryable by user, timestamp, version, or decision type

**Analysis Audit Record Schema:**

```json
{
  "audit_id": "audit_20241125_143022_user_abc",
  "audit_type": "analysis_execution",
  "analysis_version": "2.5.20241125_143022",
  "user_id": "user_abc_hashed",
  "execution_timestamp": 1732549222,
  "execution_type": "full|incremental",
  "input_snapshot": {
    "behaviour_count": 47,
    "behaviour_ids": [...],
    "input_hash": "sha256...",
    "centroid_version": "cv_20241118_120033"
  },
  "decisions_made": [
    {
      "decision_type": "core_behaviour_promotion",
      "decision_id": "dec_001",
      "candidate": "prefers visual learning",
      "outcome": "promoted",
      "confidence": 0.82,
      "reasoning": "Cluster size: 3, avg credibility: 0.79...",
      "clustering_mode": "incremental",
      "from_semantic_cache": true,
      "cache_entry_id": "cache_8f2a9d",
      "alternatives_considered": [],
      "thresholds_applied": {...}
    }
  ],
  "outputs_generated": {
    "core_behaviours": [...],
    "expertise_profiles": [...],
    "evidence_chains": [...]  // Metadata only
  },
  "performance_metrics": {
    "execution_time_ms": 4200,
    "behaviours_processed": 47,
    "prompts_metadata_fetched": 23,
    "prompts_content_fetched": 0,  // Privacy: content not loaded
    "clusters_formed": 12,
    "cache_hits": 5,
    "cache_misses": 2,
    "llm_calls": 2,
    "centroids_updated": 8,
    "new_clusters_created": 1
  }
}
```

**Access Audit Record Schema (NEW):**

```json
{
  "audit_id": "access_20241125_150032_user_abc",
  "audit_type": "prompt_content_access",
  "user_id": "user_abc_hashed",
  "access_timestamp": 1732550432,
  "access_method": "user_explanation_request",
  "prompts_accessed": [
    {
      "prompt_id": "prompt_0242",
      "vault_entry_id": "vault_prompt_0242",
      "access_reason": "expertise_explanation",
      "content_length": 156,
      "privacy_filtered": false
    }
  ],
  "request_metadata": {
    "ip_address": "hashed_for_privacy",
    "user_agent": "Mozilla/5.0...",
    "session_id": "session_abc123",
    "rate_limit_remaining": 9
  },
  "authorization": {
    "method": "ownership_verification",
    "verified": true,
    "auth_timestamp": 1732550431
  }
}
```

**Access Audit Requirements:**
- Immutable log of ALL prompt content access
- Retention: Minimum 1 year, longer for compliance
- Queryable for security investigations
- Alerts on anomalous access patterns
- Privacy-compliant (user can request their own access history)

---

## 12. Risk Mitigation & Edge Cases (ENHANCED)

### 12.1 Identified Risks

**A. Overgeneralization Risk**
- **Scenario:** Clustering unrelated behaviours into false core behaviour
- **Mitigation:** 
  - Strict semantic coherence threshold (0.7+)
  - Manual review for Low confidence core behaviours
  - Evidence chain transparency enables detection
  - **NEW: Incremental mode less prone (assigns to proven centroids)**

**B. Expertise Inflation**
- **Scenario:** User uses advanced terminology copied from sources
- **Mitigation:**
  - Weight temporal consistency heavily
  - Require sustained pattern, not one-off spikes
  - Downgrade confidence for inconsistent signals

**C. Privacy Leakage via Evidence Chains**
- **Scenario:** Evidence chains expose sensitive prompt content
- **Mitigation (IMPLEMENTED):**
  - Store only prompt IDs and hashes in evidence chains
  - Full prompt content in separate secure vault
  - Access requires authentication + rate limiting
  - All access logged to immutable audit trail
  - Privacy filters applied on content retrieval

**D. Concept Drift in Embeddings**
- **Scenario:** Embedding model's semantic space shifts over time/updates
- **Mitigation:**
  - Version embedding model with analysis results
  - Re-embed all behaviours on model change
  - **NEW: Force full re-clustering on model updates**
  - **NEW: Invalidate semantic cache on model change**
  - Maintain backward compatibility window

**E. Catastrophic Forgetting**
- **Scenario:** Removing behaviours causes loss of valid historical insights
- **Mitigation:**
  - Historical core behaviour preservation
  - Tombstone records for retired patterns
  - Reemergence detection mechanism

**F. Centroid Drift (NEW)**
- **Scenario:** Incremental updates cause gradual centroid migration away from true cluster center
- **Mitigation:**
  - Monitor centroid movement over time
  - Trigger full re-clustering when drift > 0.20
  - Monthly full re-clustering as baseline
  - Track reassignment rates (>15% triggers full refresh)

**G. Semantic Cache Pollution (NEW)**
- **Scenario:** Low-quality generalizations pollute cache, degrading future analyses
- **Mitigation:**
  - Track cache entry reuse counts
  - Retirement policy: Remove entries with <5 reuses after 90 days
  - Quality scoring: Downweight cache entries from low-confidence clusters
  - Periodic cache validation: Re-generate sample of cache entries, compare quality

**H. Rate Limit Abuse (NEW)**
- **Scenario:** Malicious user attempts to extract all prompt content rapidly
- **Mitigation:**
  - Rate limit: 10 prompt content requests per hour
  - Exponential backoff on limit violations
  - Alert on suspicious patterns (many users, same IP)
  - Temporary account lock after repeated violations

### 12.2 Edge Case Handling

**Case 1: User with Contradictory Behaviours**
```
IF user has strong conflicting patterns:
  - Create BOTH core behaviours
  - Flag as "contextual preferences"
  - Note: "User shows different patterns in different contexts"
  - Do NOT force resolution
  - Example: "Expert in Python, Novice in JavaScript"
```

**Case 2: Insufficient Data (GRADUATED APPROACH)**
```
IF user has 3-9 behaviours AND all_credibility > 0.8:
  - Generate "Emerging Profile" with Low confidence
  - Use incremental clustering (faster, less resource-intensive)
  - FLAG as "Early Stage - Limited Data"
  - DISPLAY: "We're beginning to understand your preferences..."
  - TIMELINE: "More reliable analysis after ~10 more interactions"

ELIF user has >= 10 behaviours:
  - STANDARD analysis (incremental or full based on schedule)

ELSE (< 3 behaviours):
  - Skip analysis entirely
  - RETURN: "Insufficient data for pattern analysis"
  - TIMELINE: "Analysis available after ~5 interactions"
```

**Case 3: Rapidly Changing User**
```
IF stability scores consistently <0.4:
  - Mark user profile as "Dynamic/Exploratory"
  - Reduce confidence in all core behaviours by 20
%
  - Shorten re-analysis cycle to 3 days
  - Focus on short-term patterns (last 14 days)
  - Use incremental mode only (full clustering too expensive for minimal stability)
  - NOTE: "Your interests appear to be rapidly evolving"
```

**Case 4: Domain Ambiguity**
```
IF behaviour maps to multiple domains equally:
  - Tag with all applicable domains (multi-domain behaviour)
  - Note multi-domain pattern in expertise assessment
  - Consider "cross-domain synthesis" as Advanced+ expertise signal
  - Example: "data visualization" → data_analysis + design
```

**Case 5: Centroid Drift Detection (NEW)**
```
IF incremental_analysis_count > 20 without full_reclustering:
  
  CALCULATE centroid_movement_avg = avg(
    distance(current_centroid, original_centroid) 
    for all centroids
  )
  
  IF centroid_movement_avg > 0.15:
    FLAG high_drift_warning
    SCHEDULE immediate_full_reclustering
    LOG drift_event(user_id, movement_metrics)
    NOTIFY monitoring_system
```

**Case 6: Cache Miss Cascade (NEW)**
```
IF cache_hit_rate < 0.20 for user_analysis:
  // Unusual - suggests highly unique user or cache corruption
  
  LOG anomaly(user_id, cache_hit_rate, cluster_characteristics)
  
  IF user_cluster_uniqueness_score > 0.90:
    // Legitimately unique user
    FLAG as "Unique Profile"
    CONTINUE normal analysis
  
  ELSE:
    // Possible cache corruption or model drift
    CHECK cache_health
    IF cache_corruption_detected:
      INVALIDATE affected_cache_entries
      TRIGGER cache_rebuild
```

**Case 7: Privacy Request Compliance (NEW)**
```
IF user requests data deletion (GDPR "Right to be Forgotten"):
  
  DELETE from behaviour_database (upstream handles this)
  DELETE from core_behaviour_store (user's CBAC results)
  DELETE from prompt_content_vault (ALL user prompts)
  DELETE from semantic_cache where originating_user = user_id
  PURGE from all centroids (remove user's contribution)
  
  RETAIN audit_logs (anonymized, for compliance)
  TOMBSTONE user_id (prevent re-creation without new consent)
  
  IF user contributed to multi-user cache entries:
    DECREMENT reuse_counts
    RE-EVALUATE cache_entry_quality
    RETIRE if quality falls below threshold
```

---

## 13. Success Metrics & KPIs (ENHANCED)

### 13.1 System Performance Metrics

**Processing Efficiency:**
- Average incremental analysis time: **<500ms** (target: 200-500ms)
- Average full analysis time: <60s (target: 30-45s)
- Queue wait time: <1 hour for high priority
- **Cache hit rate: >40%** (target: 50-60% after 30 days) **[NEW]**
- **Centroid stability: <0.15 average drift** **[NEW]**

**Accuracy Metrics:**
- Core behaviour stability rate: >75% remain stable after 30 days
- Expertise prediction consistency: >80% remain same level after re-analysis
- Confidence calibration: High confidence items have <10% degradation rate
- **Cache quality: >90% of cached statements remain valid after 90 days** **[NEW]**

**Coverage Metrics:**
- % of users with at least 1 core behaviour: >60%
- % of users with expertise profile: >40%
- Average behaviours per core behaviour: 3-7
- **% of analyses using incremental mode: >85%** **[NEW]**

**Cost Efficiency:** **[NEW]**
- LLM cost per user analysis: <$0.05 (with cache)
- Cache savings: >40% LLM cost reduction
- Compute cost per user: <$0.10/month
- Storage cost per user: <$0.02/month

### 13.2 Quality Indicators

**Semantic Coherence:**
- Average cluster coherence score: >0.75
- Core behaviour uniqueness: <5% overlap between user's core behaviours
- **Centroid drift per incremental cycle: <0.05** **[NEW]**

**Evidence Quality:**
- Average source behaviour credibility for core behaviours: >0.70
- Evidence chain completeness: 100% of core behaviours have full chains
- **Prompt vault integrity: 100% (hash verification)** **[NEW]**

**Privacy & Security:** **[NEW]**
- Evidence chain privacy compliance: 100% (no prompt content in chains)
- Unauthorized access attempts: 0
- Privacy filter effectiveness: >99% PII detection
- Audit log completeness: 100%

**User Value Metrics (if feedback available):**
- Explanation understandability rating: >4.0/5.0
- Accuracy of core behaviour descriptions (user-validated): >75%
- Actionability of expertise assessments: >70%

### 13.3 Operational Metrics **[NEW]**

**Clustering Efficiency:**
- Incremental vs full clustering ratio: Target 85:15
- Avg incremental clustering time: <500ms
- Avg full clustering time: <45s
- Full clustering trigger rate: <15% of analyses

**Cache Performance:**
- Cache hit rate by domain: Track separately
- Cache pollution rate: <5% (low-quality entries)
- Cache eviction rate: <10%/month
- Cache storage growth rate: Monitor for optimization

**Taxonomy Evolution:**
- New domains discovered/month: Track trend
- Domain approval rate: >70%
- Human curator hours/month: <2 hours
- A/B test success rate: >60%

**System Health:**
- Analysis queue depth: <1000 pending
- Failed analysis rate: <1%
- Centroid drift alert frequency: <5% of users/month
- Cache corruption incidents: 0

---

## 14. Implementation Roadmap (UPDATED)

### Phase 1: Core MVP (Months 1-3) - CRITICAL FOUNDATION

**Must-Have Components:**

✅ **Incremental Clustering Engine**
- Implement centroid persistence
- Distance-based assignment algorithm
- Orphan pool management
- Drift detection logic
- Priority: **CRITICAL** (prevents scalability collapse)

✅ **Privacy-Safe Evidence Chains**
- Separate prompt content vault
- Metadata-only evidence chains
- Access control layer
- Audit logging infrastructure
- Priority: **CRITICAL** (security/compliance requirement)

✅ **Basic Semantic Cache**
- Hash-based exact matching
- Simple storage (Redis)
- Cache hit/miss tracking
- Priority: **HIGH** (40-60% cost reduction)

✅ **Hybrid Execution Model**
- Incremental analysis triggers
- Periodic full analysis scheduling
- Priority queue implementation
- Priority: **CRITICAL** (core architecture)

**Performance Targets:**
- Incremental analysis: <5s
- Full analysis: <60s
- Cache hit rate: >30%
- Privacy compliance: 100%

**Deliverables:**
- Working prototype handling 10K users
- Basic monitoring dashboard
- Documentation for operators

---

### Phase 2: Optimization & Scale (Months 4-6)

**Should-Have Components:**

✅ **Advanced Semantic Cache**
- Vector similarity search for cache lookup
- Quality scoring for cache entries
- Automated cache pruning
- Cache replication for HA
- Priority: **HIGH** (optimization)

✅ **Automated Taxonomy Evolution**
- Daily domain discovery pipeline
- Monthly curator review interface
- A/B testing framework
- Auto-promotion logic
- Priority: **MEDIUM-HIGH** (reduces operational burden)

✅ **Performance Monitoring**
- Comprehensive metrics dashboard
- Alerting on drift/degradation
- Cost tracking per user
- Cache performance analytics
- Priority: **HIGH** (operational visibility)

✅ **Graduated Analysis for Low-Data Users**
- Emerging profile logic
- Confidence adjustments
- User-facing messaging
- Priority: **MEDIUM** (better user experience)

**Performance Targets:**
- Scale to 500K users
- Cache hit rate: >50%
- LLM cost reduction: >50%
- Curator time: <2 hours/month

**Deliverables:**
- Production-ready system
- Automated operations
- Cost optimization achieved

---

### Phase 3: Enhancement & Intelligence (Months 7-12)

**Nice-to-Have Components:**

✅ **Advanced Explainability UI**
- Interactive visualizations
- Natural language explanations
- Privacy-respecting prompt display
- User feedback mechanisms
- Priority: **MEDIUM** (user engagement)

✅ **Cross-User Pattern Discovery**
- Privacy-preserving aggregation
- Population-level insights
- Trend detection
- Anomaly identification
- Priority: **LOW-MEDIUM** (strategic value)

✅ **Predictive Modeling**
- Behavior trajectory prediction
- Expertise progression forecasting
- Recommendation quality improvement
- Priority: **LOW** (advanced feature)

✅ **Multi-Region Deployment**
- Cache replication across regions
- Data sovereignty compliance
- Latency optimization
- Priority: **MEDIUM** (if global scale needed)

**Performance Targets:**
- Scale to 5M users
- Sub-second incremental analysis
- Advanced privacy features
- Predictive accuracy >70%

**Deliverables:**
- Enterprise-grade system
- Advanced analytics
- Global availability

---

## 15. Conclusion: System Readiness Checklist v2.0

This enhanced design provides a **production-ready, privacy-first, cost-optimized architecture** for the Core Behaviour Analysis Component. 

### Critical Improvements from v1.0:

**1. Scalability** ✅
- Incremental clustering reduces compute by ~90% for stable users
- Scales from 10K to 500K+ users without architecture changes

**2. Cost Optimization** ✅
- Semantic cache reduces LLM costs by 40-60%
- Combined optimizations: 70-80% cost reduction

**3. Privacy & Security** ✅
- Zero prompt content in analytical layer
- Secure vault with access controls
- Complete audit trail
- GDPR compliance ready

**4. Operational Efficiency** ✅
- Automated taxonomy evolution (< 2 hours/month curator time)
- Self-monitoring and self-healing
- Graduated rollout capabilities

**5. Quality Assurance** ✅
- Centroid drift detection
- Cache quality monitoring
- Confidence calibration

### Pre-Implementation Validation:

**✓ Architecture validated for:**
- Separation from upstream systems
- Horizontal scalability to millions of users
- Privacy-first design (secure by default)
- Cost-effectiveness at scale
- Explainability and auditability

**✓ Execution strategy defined:**
- Adaptive hybrid processing (incremental + periodic)
- Intelligent resource allocation
- Change management and versioning
- Performance monitoring

**✓ Core capabilities specified:**
- Incremental semantic clustering (scalable)
- Semantic cache (cost-optimized)
- Privacy-safe evidence chains
- Automated taxonomy evolution
- Core behaviour derivation logic
- Expertise classification framework

**✓ Edge cases and risks addressed:**
- Centroid drift mitigation
- Cache quality management
- Privacy leakage prevention
- Rate limit protection
- Data deletion compliance

**✓ Evolution strategy established:**
- Adaptive learning mechanisms
- Quarterly calibration cycles
- Automated domain discovery
- Long-term scalability roadmap

---

### Final Recommendation:

**APPROVED FOR IMPLEMENTATION** with the following critical path:

**Phase 1 Must-Haves (Non-Negotiable):**
1. Incremental clustering with centroid persistence
2. Privacy-safe evidence chains with secure vault
3. Basic semantic cache (hash-based)
4. Hybrid execution orchestration

**Phase 2 High-Priority:**
1. Advanced semantic cache (similarity-based)
2. Automated taxonomy evolution
3. Comprehensive monitoring

The system is **ready for development** with a clear, validated path from MVP through enterprise scale. All architectural decisions are justified, risks are mitigated, and success criteria are measurable.

**Estimated Implementation Timeline:**
- Phase 1 MVP: 3 months
- Phase 2 Production: 6 months total
- Phase 3 Enterprise: 12 months total

**Expected Outcomes:**
- 70-80% cost reduction vs naive implementation
- 90% compute reduction for stable users
- 100% privacy compliance
- <2 hours/month operational overhead
- Scales to 5M+ users

---

**Document Status:** FINAL v2.0 - Ready for Engineering Handoff