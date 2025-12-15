# Core Behaviour Analysis Component (CBAC) - System Design Document

## 1. Overall Architecture Description

### 1.1 System Position in Data Pipeline

```
[Upstream System] → [Vector DB: Behaviours] → [CBAC] → [Output Store: Core Behaviours & Expertise]
                  → [Document DB: Prompts]  ↗
```

The CBAC operates as a **analytical processing layer** that consumes stabilized behavioral data and produces higher-order insights. It sits between raw behaviour storage and application consumption layers.

### 1.2 Architectural Components

**A. Input Interface Layer**
- Behaviour Retrieval Service: Fetches per-user behaviours from vector DB
- Prompt History Service: Retrieves original prompts via `prompt_history_ids`
- State Management: Tracks previous CBAC analysis results

**B. Core Processing Engine**
- Semantic Clustering Module
- Core Behaviour Derivation Engine
- Expertise Assessment Module
- Evidence Chain Constructor

**C. Output Management Layer**
- Core Behaviour Store
- Expertise Profile Store
- Evidence Trace Repository
- Version Control System

**D. Orchestration Layer**
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
2. Sort by credibility × reinforcement_count (weighted relevance)
3. Fetch historical prompt texts for top N% of behaviours
4. Load previous CBAC analysis results (if exist)

**Output:** Enriched behaviour dataset with context

### Stage 2: Semantic Analysis & Clustering
**Input:** Enriched behaviour dataset
**Process:**
1. Generate semantic embeddings for each behaviour_text
2. Perform hierarchical clustering based on semantic similarity
3. Identify cluster centroids and coherence scores
4. Map behaviours to semantic groups

**Output:** Behaviour clusters with similarity metrics

### Stage 3: Core Behaviour Derivation
**Input:** Behaviour clusters
**Process:**
1. For each cluster, evaluate promotion criteria
2. Generate generalized behaviour statement
3. Calculate aggregate confidence scores
4. Build evidence chain linking source behaviours
5. Compare against previous core behaviours

**Output:** Candidate core behaviours with evidence

### Stage 4: Expertise Signal Extraction
**Input:** Behaviours + Linked prompts
**Process:**
1. Analyze prompt complexity patterns
2. Extract domain indicators from behaviours
3. Measure reinforcement stability over time
4. Identify knowledge depth signals

**Output:** Domain-specific expertise indicators

### Stage 5: Expertise Level Classification
**Input:** Expertise indicators
**Process:**
1. Aggregate signals per domain
2. Apply classification decision tree
3. Calculate confidence and stability scores
4. Generate supporting evidence

**Output:** Expertise profiles with justification

### Stage 6: Change Management & Persistence
**Input:** New core behaviours + expertise profiles
**Process:**
1. Detect changes from previous analysis
2. Apply preservation/retirement rules
3. Version and timestamp all outputs
4. Store evidence chains
5. Update state for next execution

**Output:** Persisted results with audit trail

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
  
  GENERATE generalized_statement using LLM with constraints:
    - Must abstractly capture all members
    - Must be single, clear statement
    - Must preserve semantic intent
  
  CALCULATE promotion_confidence:
    = (aggregate_credibility × 0.4) +
      (stability_score × 0.3) +
      (semantic_coherence × 0.3)
  
  IF promotion_confidence >= 0.70:
    PROMOTE to core behaviour
    BUILD evidence chain
    STORE with version metadata
```

### Pipeline B: Expertise Level Classification

```
FOR each domain identified in behaviours:
  
  EXTRACT signals:
    - terminology_sophistication (from prompt analysis)
    - question_complexity (prompt structure analysis)
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
  
  STORE with evidence mapping
```

---

## 4. Core Behaviour Identification Methodology

### 4.1 Semantic Grouping Strategy

**Method: Hierarchical Density-Based Clustering**

1. **Embedding Generation:**
   - Use consistent sentence embedding model for all behaviour_text
   - Store embeddings with behaviour records for repeatability

2. **Distance Calculation:**
   - Compute cosine similarity matrix for all behaviours
   - Apply semantic distance threshold (e.g., similarity > 0.75)

3. **Cluster Formation:**
   - Use HDBSCAN-like logic to identify dense regions
   - Allow behaviours to belong to multiple clusters (soft assignment)
   - Maintain minimum cluster size = 3

4. **Centroid Identification:**
   - For each cluster, calculate weighted centroid:
     `centroid = Σ(embedding × credibility × reinforcement_count) / Σ(weights)`

### 4.2 Generalization Logic

**Input:** Cluster of similar behaviours
**Process:**

1. **Extract common elements:**
   - Identify shared semantic tokens
   - Remove overly specific modifiers
   - Preserve core intent

2. **Generate candidate statement:**
   - Use LLM with strict prompt:
     ```
     Given these related behaviours: [list]
     Generate ONE general statement that captures their essence.
     Rules:
     - Maximum 10 words
     - No specific examples
     - Preserve action/preference pattern
     - Use present tense
     ```

3. **Validate generalization:**
   - Ensure all source behaviours are semantically covered
   - Check that generalization doesn't over-abstract
   - Verify uniqueness against existing core behaviours

### 4.3 Confidence Calculation

**Core Behaviour Confidence Formula:**

```
CBC = (w1 × Cred_agg) + (w2 × Stab_score) + (w3 × Sem_coh) + (w4 × Reinf_depth)

Where:
  Cred_agg = Σ(credibility × reinforcement) / Σ(reinforcement)
  Stab_score = temporal_variance_coefficient
  Sem_coh = average_intra_cluster_similarity
  Reinf_depth = log(1 + total_reinforcements) / log(threshold)
  
  Weights: w1=0.35, w2=0.25, w3=0.25, w4=0.15
```

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

**B. Cognitive Complexity Signals**
- Prompt length and structure complexity
- Multi-step reasoning indicators
- Conditional logic presence
- Abstract concept usage

**C. Temporal Patterns**
- Reinforcement consistency (does expertise grow?)
- Knowledge domain expansion rate
- Error correction patterns (learning signals)

**D. Task Complexity Indicators**
- Problem difficulty level from prompts
- Meta-cognitive behaviour (asking about methodology)
- Self-directed learning signals

### 5.2 Domain Identification

**Process:**
1. Extract domain keywords from behaviours using NER + keyword extraction
2. Group behaviours by dominant domain tags
3. Require minimum 5 behaviours to establish domain presence
4. Map to standardized domain taxonomy (e.g., "programming", "creative writing", "data analysis")

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
  - Analyze only new/changed behaviours
  - Quick cluster reassignment
  - Update existing core behaviours
  - Skip full expertise recalculation

FREQUENCY: As triggered (potentially multiple per day per user)

DURATION: <5 seconds per user
```

**B. Full Analysis (Periodic)**
```
TRIGGER:
  - Scheduled: Every 7 days per user
  - Or after 50+ incremental changes accumulated

SCOPE:
  - Complete re-clustering from scratch
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
  - Domain taxonomy updates
  - Model calibration
  - Aggregate metrics

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
```

### 7.4 Performance Considerations

**Resource Budgeting:**
- Incremental analysis: 500ms per user (can handle 7,200 users/hour)
- Full analysis: 45s per user (can handle 80 users/hour)
- Separate processing queues prevent interference

**Scalability:**
- Horizontal scaling: Partition users by hash
- Each worker handles independent user subset
- Shared read-only access to prompt database
- Write synchronization only for user's own results

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
    "clustering_method": "hdbscan",
    "embedding_model": "all-MiniLM-L6-v2",
    "confidence_weights": {...},
    "thresholds": {...}
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

FOR each new_core_behaviour:
  
  IF matches existing core_behaviour:
    COMPARE confidence_scores
    IF delta > 0.15:
      LOG significant_change(behaviour, old_conf, new_conf)
      RECORD reason(supporting_behaviours_diff)
  
  ELSE:
    LOG new_emergence(behaviour)
    RECORD source_cluster_evidence

FOR each old_core_behaviour NOT in new_results:
  LOG retirement(behaviour)
  RECORD retirement_reason
  ARCHIVE with historical status
```

### 8.4 Rollback & Reproducibility

**Requirements:**
- Store input data hash with each analysis
- Preserve model configuration snapshot
- Enable reconstruction of analysis from versioned inputs

**Rollback Process:**
```
IF analysis_version N produces errors or anomalies:
  
  FETCH analysis_version N-1 results
  RESTORE as active state
  
  QUEUE affected_users for reanalysis with:
    - Previous model version
    - OR debugged current version
  
  LOG rollback event with justification
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
    "semantic_coherence": 0.75  // Cluster tightness
  },
  "confidence_grade": "High",   // High|Medium|Low
  "stability_indicator": "Stable" // Stable|Transitional|Emerging
}
```

### 9.2 Confidence Grading Rules

```
overall_confidence = weighted_harmonic_mean(components)

Grade assignment:
  IF overall_confidence >= 0.75 AND all_components >= 0.65:
    GRADE = "High"
  
  ELIF overall_confidence >= 0.55 AND no_component < 0.45:
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

**Classification Logic:**

```
FOR each core_behaviour:
  
  temporal_variance = std_dev(observation_intervals)
  reinforcement_pattern = coefficient_of_variation(reinforcements)
  semantic_drift = cluster_reassignment_frequency
  
  stability_score = 1 - weighted_avg(variances)
  
  IF stability_score > 0.75:
    STATUS = "Stable"
    CONFIDENCE_BOOST = +0.1
  
  ELIF stability_score > 0.50:
    STATUS = "Transitional"
    CONFIDENCE_ADJUSTMENT = 0
    FLAG = "monitor_for_3_cycles"
  
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

**B. Expertise Calibration**
- When possible, compare expertise predictions to observable outcomes
  - Does "expert" user create high-quality outputs?
  - Does classification match self-reported expertise when available?
- Tune signal weights based on predictive success

**C. Semantic Model Drift**
- Monitor if clusters become less coherent over time (model aging)
- Track emergence of new domain vocabularies
- Schedule embedding model updates when drift detected

### 10.2 Model Refresh Strategy

**Quarterly Review Cycle:**

```
EVERY 90 days:
  
  ANALYZE performance metrics:
    - Core behaviour stability rates
    - Confidence calibration accuracy
    - Expertise prediction consistency
    - Processing time trends
  
  IF metrics degrade > 10%:
    TRIGGER model_recalibration:
      - Re-tune threshold values
      - Update domain taxonomy
      - Refresh embedding model
      - A/B test parameter changes
  
  DOCUMENT changes and expected impact
  EXECUTE staged rollout (10% → 50% → 100% of users)
```

### 10.3 Domain Taxonomy Evolution

**Challenge:** New domains emerge, old ones fragment or merge

**Strategy: Semi-Automated Taxonomy Management**

```
MONTHLY:
  
  EXTRACT emergent_domain_clusters from all users
  
  IF new_cluster appears in >5% of user base:
    PROPOSE new_domain_label
    REVIEW by human curator
    ADD to taxonomy with:
      - Domain definition
      - Typical signal patterns
      - Expertise level indicators
  
  IF existing_domain shows bifurcation:
    PROPOSE split into sub-domains
    VALIDATE with sample user profiles
    UPDATE taxonomy hierarchy
```

### 10.4 Privacy & Consent Evolution

**Anticipating Future Requirements:**

**A. Explainability on Demand**
- Users can request "why does the system think X about me?"
- Generate natural language explanation from evidence chains
- Show source behaviours and their contribution weights

**B. Selective Opt-Out**
- Allow users to exclude specific behaviours from analysis
- Allow domain-specific opt-out (e.g., "don't analyze work behaviours")
- Recompute affected core behaviours and expertise

**C. Data Portability**
- Export user's complete CBAC profile in standardized format
- Include all evidence chains and confidence scores
- Support import into compatible systems

### 10.5 Scalability Roadmap

**Current Design:** Single-user analysis isolation

**Future Considerations:**

**Phase 1 (Months 1-6):** Current design
- Per-user processing
- Independent analysis
- Scales to 100K users

**Phase 2 (Months 7-12):** Optimization
- Shared embedding cache
- Incremental-only for 80% of users
- Scales to 1M users

**Phase 3 (Year 2):** Distributed Architecture
- Cluster-based processing
- Distributed vector search
- Real-time incremental updates
- Scales to 10M+ users

**Phase 4 (Year 3+):** Intelligence Layer
- Cross-user pattern discovery
- Collaborative filtering for core behaviours
- Predictive behaviour modeling
- Population-level insights

---

## 11. Evidence Chain & Explainability Design

### 11.1 Evidence Data Model

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
      },
      {
        "behavior_id": "beh_7def234",
        "behavior_text": "asks for diagram-based explanations",
        "credibility": 0.71,
        "reinforcement_count": 3,
        "contribution_weight": 0.23
      }
    ],
    "clustering_metrics": {
      "semantic_similarity_avg": 0.81,
      "cluster_coherence": 0.77,
      "generalization_confidence": 0.85
    },
    "derivation_logic": {
      "method": "semantic_clustering",
      "threshold_used": 0.75,
      "abstraction_level": "medium",
      "llm_prompt_version": "v2.3"
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

**For Expertise Profiles:**

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
        "prompt_excerpt": "Can you help me implement a hierarchical clustering...",
        "complexity_score": 0.81,
        "signals_detected": [
          "multi_step_reasoning",
          "technical_terminology",
          "problem_decomposition"
        ]
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
      "why_not_expert": "Lacks evidence of novel methodology creation or meta-level analysis",
      "progression_indicators": "Trending toward Expert in recent sessions"
    }
  }
}
```

### 11.2 Backtracking Mechanisms

**Query Interface:**

```
GET /explain/core-behaviour/{core_behaviour_id}
  Returns: Complete evidence chain with visual cluster representation

GET /explain/expertise/{user_id}/{domain}
  Returns: Signal breakdown, supporting prompts, classification logic

GET /trace/behaviour-to-core/{behavior_id}
  Returns: All core behaviours derived from this source behaviour

GET /audit/analysis/{analysis_run_id}
  Returns: Complete input state, decisions made, outputs generated
```

**Visualization Requirements:**

- **Cluster Graph:** Visual representation of behaviour clustering with core behaviour at center
- **Timeline View:** Temporal evolution of behaviours contributing to core behaviour
- **Signal Heatmap:** Expertise signals across time and domains
- **Confidence Decomposition:** Pie chart showing confidence component weights

### 11.3 Human-Readable Explanation Generation

**Template-Based Natural Language Generation:**

**For Core Behaviours:**

```
Template:
"The system identified that you {core_behaviour} based on {N} related patterns observed across {timespan}. 

Key evidence includes:
- {strongest_source_behaviour} (observed {reinforcement_count} times, credibility {score})
- {second_strongest} (observed {reinforcement_count} times, credibility {score})

This conclusion has {confidence_grade} confidence ({confidence_score}) because {primary_confidence_factor}. 

The pattern has been {stability_indicator} over the past {observation_period}."

Example Output:
"The system identified that you prefer visual learning methods based on 3 related patterns observed across 22 days.

Key evidence includes:
- You prefer video tutorials over text (observed 7 times, credibility 0.89)
- You like infographic-style explanations (observed 4 times, credibility 0.76)

This conclusion has High confidence (0.82) because the patterns are semantically similar and consistently reinforced.

The pattern has been Stable over the past 3 weeks."
```

**For Expertise Levels:**

```
Template:
"Based on your interaction patterns, you demonstrate {level} expertise in {domain} (confidence: {score}).

This assessment is based on:
- {signal_category_1}: {evidence_summary}
- {signal_category_2}: {evidence_summary}

Specifically:
- Your prompts show {complexity_descriptor} (score: {score})
- You use {terminology_descriptor} (score: {score})
- Your engagement pattern shows {consistency_descriptor}

You are classified as {level} rather than {higher_level} because {limiting_factor}.

{progression_note if trending upward}"

Example Output:
"Based on your interaction patterns, you demonstrate Advanced expertise in data analysis (confidence: 0.79).

This assessment is based on:
- Technical Language: You consistently use domain-specific terminology like 'hierarchical clustering', 'dimensionality reduction', and 'statistical significance'
- Problem Complexity: Your prompts involve multi-step analytical workflows and sophisticated problem decomposition

Specifically:
- Your prompts show high complexity (score: 0.81)
- You use advanced technical vocabulary (score: 0.84)
- Your engagement pattern shows strong consistency (score: 0.81)

You are classified as Advanced rather than Expert because your work primarily applies existing methods rather than developing novel analytical frameworks.

Recent trends suggest progression toward Expert level as you've begun exploring meta-analytical questions."
```

### 11.4 Audit Trail Storage

**Requirements:**
- Every analysis execution generates an audit record
- Immutable append-only log
- Queryable by user, timestamp, version, or decision type

**Audit Record Schema:**

```json
{
  "audit_id": "audit_20241125_143022_user_abc",
  "analysis_version": "2.5.20241125_143022",
  "user_id": "user_abc",
  "execution_timestamp": 1732549222,
  "execution_type": "full|incremental",
  "input_snapshot": {
    "behaviour_count": 47,
    "behaviour_ids": [...],
    "input_hash": "sha256..."
  },
  "decisions_made": [
    {
      "decision_type": "core_behaviour_promotion",
      "decision_id": "dec_001",
      "candidate": "prefers visual learning",
      "outcome": "promoted",
      "confidence": 0.82,
      "reasoning": "Cluster size: 3, avg credibility: 0.79, stability: 0.78, coherence: 0.81",
      "alternatives_considered": [],
      "thresholds_applied": {...}
    },
    {
      "decision_type": "expertise_classification",
      "decision_id": "dec_002",
      "domain": "data_analysis",
      "outcome": "Advanced",
      "confidence": 0.79,
      "reasoning": "Signal strength 0.79 within range [0.6, 0.85], high temporal consistency",
      "alternatives_considered": ["Expert (rejected: insufficient novelty signals)"],
      "signal_breakdown": {...}
    }
  ],
  "outputs_generated": {
    "core_behaviours": [...],
    "expertise_profiles": [...],
    "evidence_chains": [...]
  },
  "performance_metrics": {
    "execution_time_ms": 42300,
    "behaviours_processed": 47,
    "prompts_analyzed": 23,
    "clusters_formed": 12,
    "core_behaviours_promoted": 5
  }
}
```

---

## 12. Risk Mitigation & Edge Cases

### 12.1 Identified Risks

**A. Overgeneralization Risk**
- **Scenario:** Clustering unrelated behaviours into false core behaviour
- **Mitigation:** 
  - Strict semantic coherence threshold (0.7+)
  - Manual review for Low confidence core behaviours
  - Evidence chain transparency enables detection

**B. Expertise Inflation**
- **Scenario:** User uses advanced terminology copied from sources, inflating expertise
- **Mitigation:**
  - Weight temporal consistency heavily
  - Require sustained pattern, not one-off spikes
  - Downgrade confidence for inconsistent signals

**C. Privacy Leakage via Evidence Chains**
- **Scenario:** Evidence chains expose sensitive prompt content
- **Mitigation:**
  - Store only prompt IDs in evidence, not full text by default
  - Fetch full prompt only on explicit user request
  - Apply content filtering to prompt excerpts in explanations

**D. Concept Drift in Embeddings**
- **Scenario:** Embedding model's semantic space shifts over time/updates
- **Mitigation:**
  - Version embedding model with analysis results
  - Re-embed all behaviours on model change
  - Maintain backward compatibility window

**E. Catastrophic Forgetting**
- **Scenario:** Removing behaviours causes loss of valid historical insights
- **Mitigation:**
  - Historical core behaviour preservation
  - Tombstone records for retired patterns
  - Reemergence detection mechanism

### 12.2 Edge Case Handling

**Case 1: User with Contradictory Behaviours**
```
IF user has strong conflicting patterns:
  - Create BOTH core behaviours
  - Flag as "contextual preferences"
  - Note: "User shows different patterns in different contexts"
  - Do NOT force resolution
```

**Case 2: Insufficient Data**
```
IF user has <10 behaviours:
  - Skip core behaviour derivation
  - Return: "Insufficient data for pattern analysis"
  - Provide timeline: "Analysis available after ~20 behaviours observed"
```

**Case 3: Rapidly Changing User**
```
IF stability scores consistently <0.4:
  - Mark user profile as "Dynamic/Exploratory"
  - Reduce confidence in all core behaviours
  - Shorten re-analysis cycle to 3 days
  - Focus on short-term patterns
```

**Case 4: Domain Ambiguity**
```
IF behaviour maps to multiple domains equally:
  - Tag with all applicable domains
  - Note multi-domain pattern in expertise assessment
  - Consider "cross-domain synthesis" as signal of Advanced+ expertise
```

---

## 13. Success Metrics & KPIs

### 13.1 System Performance Metrics

- **Processing Efficiency:**
  - Average incremental analysis time: <5s
  - Average full analysis time: <60s
  - Queue wait time: <1 hour for high priority

- **Accuracy Metrics:**
  - Core behaviour stability rate: >75% remain stable after 30 days
  - Expertise prediction consistency: >80% remain same level after re-analysis
  - Confidence calibration: High confidence items have <10% degradation rate

- **Coverage Metrics:**
  - % of users with at least 1 core behaviour: >60%
  - % of users with expertise profile: >40%
  - Average behaviours per core behaviour: 3-7

### 13.2 Quality Indicators

- **Semantic Coherence:**
  - Average cluster coherence score: >0.75
  - Core behaviour uniqueness: <5% overlap between core behaviours

- **Evidence Quality:**
  - Average source behaviour credibility for core behaviours: >0.70
  - Evidence chain completeness: 100% of core behaviours have full chains

- **User Value Metrics (if feedback available):**
  - Explanation understandability rating
  - Accuracy of core behaviour descriptions (user-validated)
  - Actionability of expertise assessments

---

## Conclusion: System Readiness Checklist

This design provides a comprehensive, future-proof architecture for the Core Behaviour Analysis Component. Before implementation:

**✓ Architecture validated for:**
- Separation from upstream systems
- Scalability to millions of users
- Explainability and auditability
- Privacy and consent compliance

**✓ Execution strategy defined:**
- Adaptive hybrid processing model
- Resource budgeting and scaling plan
- Change management and versioning

**✓ Core capabilities specified:**
- Semantic clustering methodology
- Core behaviour derivation logic
- Expertise level classification framework
- Evidence chain construction

**✓ Edge cases and risks addressed:**
- Contradictory signals resolution
- Data insufficiency handling
- Privacy protection mechanisms
- Model drift mitigation

**✓ Evolution strategy established:**
- Feedback loops for self-improvement
- Quarterly review cycles
- Domain taxonomy evolution
- Long-term scalability roadmap

The system is designed to be **deterministic, repeatable, explainable, and continuously improving** — ready for implementation without further architectural decisions required.