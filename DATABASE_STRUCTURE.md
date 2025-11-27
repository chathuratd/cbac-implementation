# CBAC Database-Style Dataset Structure

## Overview

The datasets are organized like a real database system with **separate collections** that are linked by IDs. This mimics how behaviors would be stored in a vector database and prompts in a document database.

---

## File Structure

```
implemantation/
├── behaviors_db.json              # All behaviors (like Vector DB)
├── prompts_db.json                # All prompts (like Document DB)
├── users_metadata.json            # User info + ground truth
├── test_scenarios.json            # 5 test scenarios with user lists
└── test_scenario_incremental.json # Incremental update test
```

---

## 1. behaviors_db.json

**Purpose:** Main behavior collection (simulates vector database)

**Structure:** Array of behavior objects

**Sample Entry:**
```json
{
  "behavior_id": "beh_c439c009",
  "behavior_text": "understands seasonal planting cycles",
  "credibility": 0.81,
  "reinforcement_count": 5,
  "decay_rate": 0.01,
  "created_at": 1756310373,
  "last_seen": 1756330778,
  "prompt_history_ids": ["prompt_0022", "prompt_0050", "prompt_0018"],
  "clarity_score": 0.8,
  "extraction_confidence": 0.77,
  "session_id": "session_005",
  "user_id": "user_stable_users_01",
  "domain": "gardening",              // GROUND TRUTH - remove in production
  "expertise_level": "intermediate"   // GROUND TRUTH - remove in production
}
```

**Key Fields:**
- `behavior_id`: Unique identifier
- `user_id`: Links to specific user (used to filter behaviors)
- `prompt_history_ids`: Links to prompts that triggered this behavior
- `domain` & `expertise_level`: Ground truth labels (for testing only)

**Total Entries:** 333 behaviors across 10 users

**Usage:**
```python
# Get behaviors for a specific user
user_behaviors = [b for b in behaviors_db if b["user_id"] == "user_stable_users_01"]

# Get behaviors by IDs
behavior_ids = ["beh_001", "beh_002"]
behaviors = [b for b in behaviors_db if b["behavior_id"] in behavior_ids]
```

---

## 2. prompts_db.json

**Purpose:** Prompt history collection (simulates document database)

**Structure:** Array of prompt objects

**Sample Entry:**
```json
{
  "prompt_id": "prompt_0079",
  "prompt_text": "Can you help me with {gardening_problem}?",
  "timestamp": 1756310986,
  "session_id": "session_004",
  "tokens": 78,
  "user_id": "user_stable_users_01",
  "domain": "gardening"  // GROUND TRUTH - remove in production
}
```

**Key Fields:**
- `prompt_id`: Unique identifier (referenced by behaviors)
- `user_id`: User who made the prompt
- `timestamp`: When the prompt was made
- `prompt_text`: Original prompt content
- `domain`: Ground truth (for testing only)

**Total Entries:** 999 prompts (~3 prompts per behavior)

**Usage:**
```python
# Get prompts by IDs (from behavior's prompt_history_ids)
prompt_ids = ["prompt_0022", "prompt_0050"]
prompts = [p for p in prompts_db if p["prompt_id"] in prompt_ids]

# Get all prompts for a user
user_prompts = [p for p in prompts_db if p["user_id"] == "user_stable_users_01"]
```

---

## 3. users_metadata.json

**Purpose:** User information and ground truth for validation

**Structure:** Array of user metadata objects

**Sample Entry:**
```json
{
  "user_id": "user_stable_users_01",
  "scenario_type": "stable_user",
  "behavior_count": 35,
  "prompt_count": 105,
  "ground_truth": {
    "expected_clusters": {
      "gardening_intermediate": 15,
      "cooking_intermediate": 12,
      "photography_novice": 8
    },
    "expected_domains": ["gardening", "photography", "cooking"],
    "expected_core_behaviors": 3,
    "expertise_levels": {
      "gardening": "intermediate",
      "cooking": "intermediate",
      "photography": "novice"
    }
  },
  "metadata": {
    "generated_at": 1764086373,
    "total_prompts": 105,
    "total_behaviors": 35,
    "time_span_days": 60
  }
}
```

**Usage:**
```python
# Get ground truth for validation
user_meta = next(u for u in users_metadata if u["user_id"] == "user_stable_users_01")
expected_clusters = user_meta["ground_truth"]["expected_clusters"]
expected_expertise = user_meta["ground_truth"]["expertise_levels"]

# Compare system output vs expected
assert len(detected_clusters) == user_meta["ground_truth"]["expected_core_behaviors"]
```

---

## 4. test_scenarios.json

**Purpose:** Defines test scenarios with specific user sets

**Structure:** Array of scenario objects

**Available Scenarios:**

### Scenario 1: Development Baseline
```json
{
  "scenario_id": "dev_baseline",
  "user_ids": ["user_stable_users_01", "user_stable_users_02"],
  "expected_outcomes": {
    "core_behaviors_per_user": 3,
    "domains_per_user": 3,
    "min_cluster_size": 3
  }
}
```
**Use for:** Initial development, unit testing

### Scenario 2: Full Integration
```json
{
  "scenario_id": "integration_full",
  "user_ids": [/* all 10 users */],
  "expected_outcomes": {
    "total_users": 10,
    "varied_cluster_counts": true
  }
}
```
**Use for:** End-to-end testing, performance benchmarking

### Scenario 3: Stable Users Only
```json
{
  "scenario_id": "stable_only",
  "user_ids": [/* 3 stable users */],
  "expected_outcomes": {
    "high_confidence": true,
    "clear_clusters": true
  }
}
```
**Use for:** Baseline clustering validation

### Scenario 4: Edge Cases
```json
{
  "scenario_id": "edge_cases",
  "user_ids": [/* noisy + sparse users */],
  "expected_outcomes": {
    "some_low_confidence": true,
    "orphan_behaviors_expected": true
  }
}
```
**Use for:** Robustness testing, error handling

### Scenario 5: Expertise Progression
```json
{
  "scenario_id": "expertise_progression",
  "user_ids": [/* evolution users */],
  "expected_outcomes": {
    "temporal_patterns": true,
    "final_expertise": "advanced"
  }
}
```
**Use for:** Temporal analysis, expertise evolution detection

**Usage:**
```python
# Load a test scenario
scenario = next(s for s in test_scenarios if s["scenario_id"] == "dev_baseline")

# Get behaviors for all users in scenario
for user_id in scenario["user_ids"]:
    user_behaviors = [b for b in behaviors_db if b["user_id"] == user_id]
    # Process user...
```

---

## 5. test_scenario_incremental.json

**Purpose:** Test incremental clustering (adding new behaviors to existing user)

**Structure:**
```json
{
  "scenario_id": "incremental_update",
  "base_user_id": "user_stable_users_01",
  "base_state": {
    "behavior_count": 35,
    "established_domains": ["gardening", "cooking", "photography"]
  },
  "incremental_behaviors": [/* 9 new behaviors */],
  "incremental_prompts": [/* 9 new prompts */],
  "expected_outcomes": {
    "new_behavior_count": 9,
    "gardening_cluster_should_grow": true,
    "programming_cluster_should_form": true,
    "no_full_reclustering": true
  }
}
```

**Incremental Behaviors Breakdown:**
- **5 gardening behaviors** (intermediate) → Should join existing gardening cluster
- **4 programming behaviors** (novice) → Should form NEW cluster

**Usage:**
```python
# Step 1: Process base user (already in behaviors_db)
base_behaviors = [b for b in behaviors_db if b["user_id"] == incremental["base_user_id"]]
# Run clustering, derive core behaviors

# Step 2: Add incremental behaviors
new_behaviors = incremental["incremental_behaviors"]
# Test incremental clustering (should NOT re-cluster everything)

# Step 3: Validate
assert gardening_cluster_grew  # Existing cluster expanded
assert programming_cluster_formed  # New cluster created
assert no_full_reclustering_occurred  # Performance check
```

---

## User Distribution

| Scenario Type | User Count | User IDs | Characteristics |
|---------------|------------|----------|-----------------|
| Stable Users | 3 | user_stable_users_01-03 | Clear 3-domain patterns |
| Multi-Domain Experts | 2 | user_multi_domain_experts_01-02 | Advanced in 2-3 domains |
| Expertise Evolution | 2 | user_expertise_evolution_01-02 | Novice → Advanced progression |
| Noisy Data | 2 | user_noisy_data_01-02 | Contradictory signals |
| Sparse Clusters | 1 | user_sparse_clusters_01 | Many small clusters |

**Total:** 10 users, 333 behaviors, 999 prompts

---

## Data Access Patterns

### Pattern 1: Get all data for one user
```python
user_id = "user_stable_users_01"

# Get behaviors
behaviors = [b for b in behaviors_db if b["user_id"] == user_id]

# Get prompts (via behavior references)
prompt_ids = set()
for b in behaviors:
    prompt_ids.update(b["prompt_history_ids"])
prompts = [p for p in prompts_db if p["prompt_id"] in prompt_ids]

# Get ground truth
metadata = next(u for u in users_metadata if u["user_id"] == user_id)
```

### Pattern 2: Process a test scenario
```python
scenario = next(s for s in test_scenarios if s["scenario_id"] == "dev_baseline")

for user_id in scenario["user_ids"]:
    # Get user behaviors
    behaviors = [b for b in behaviors_db if b["user_id"] == user_id]
    
    # Process through CBAC
    core_behaviors = cbac_system.process(behaviors)
    
    # Validate against ground truth
    expected = next(u["ground_truth"] for u in users_metadata if u["user_id"] == user_id)
    validate(core_behaviors, expected)
```

### Pattern 3: Incremental update simulation
```python
incremental = load_json("test_scenario_incremental.json")

# Step 1: Get baseline state
base_user_id = incremental["base_user_id"]
base_behaviors = [b for b in behaviors_db if b["user_id"] == base_user_id]
baseline_results = cbac_system.process(base_behaviors)

# Step 2: Add new behaviors
new_behaviors = incremental["incremental_behaviors"]
all_behaviors = base_behaviors + new_behaviors

# Step 3: Process incrementally (should reuse centroids)
updated_results = cbac_system.process_incremental(
    baseline_results, 
    new_behaviors
)

# Step 4: Validate
assert updated_results.no_full_reclustering
assert updated_results.gardening_cluster_size_increased
```

---

## Ground Truth Labels

**Important:** The following fields are for testing/validation ONLY:

- `behavior.domain` - Domain label (gardening, cooking, etc.)
- `behavior.expertise_level` - Expertise level (novice, intermediate, advanced)
- `prompt.domain` - Domain label

**These should NOT be used by the CBAC system during processing.** They exist only for:
1. Validating clustering quality (do similar domains cluster together?)
2. Validating expertise classification (does detected level match ground truth?)
3. Understanding test data structure

**Before production:** Remove these fields from the JSON or ignore them in the loader.

---

## Regenerating Datasets

To regenerate with new random variations:

```bash
python data_gen.py
```

This will:
1. Delete old dataset files
2. Generate new users with same patterns but different random values
3. Create all 5 JSON files with fresh data

**Warning:** This will overwrite existing datasets!

---

## Next Steps for Implementation

1. **Create Data Loader:**
   ```python
   def load_user_behaviors(user_id, behaviors_db):
       return [b for b in behaviors_db if b["user_id"] == user_id]
   
   def load_prompts_by_ids(prompt_ids, prompts_db):
       return [p for p in prompts_db if p["prompt_id"] in prompt_ids]
   ```

2. **Process Test Scenario:**
   ```python
   scenario = test_scenarios[0]  # dev_baseline
   for user_id in scenario["user_ids"]:
       behaviors = load_user_behaviors(user_id, behaviors_db)
       core_behaviors = cbac.process(behaviors)
       validate_against_ground_truth(core_behaviors, user_id)
   ```

3. **Validate Results:**
   ```python
   user_meta = users_metadata[user_id]
   expected = user_meta["ground_truth"]
   
   assert len(core_behaviors) == expected["expected_core_behaviors"]
   assert detected_domains == set(expected["expected_domains"])
   assert expertise_levels == expected["expertise_levels"]
   ```

---

**Status:** ✓ Database-style datasets ready for CBAC implementation
