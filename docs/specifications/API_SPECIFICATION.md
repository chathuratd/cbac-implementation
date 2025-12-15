# CBAC API Specification - Complete Feature Set

**Document Version:** 1.0  
**Last Updated:** November 25, 2025  
**Target Framework:** FastAPI (Python 3.10+)  
**Architecture:** RESTful API with async support

---

## System Overview

The Core Behaviour Analysis Component (CBAC) API provides endpoints for analyzing user behaviors, deriving core behavioral patterns, and assessing domain expertise. The system uses incremental clustering, semantic caching, and secure evidence chains to provide scalable, privacy-conscious behavioral insights.

---

## Core Capabilities

### 1. Core Behaviour Analysis
- Semantic clustering of raw behaviors
- Incremental vs. full clustering modes
- Core behaviour derivation with LLM-powered generalization
- Confidence scoring and stability tracking
- Evidence chain construction

### 2. Expertise Assessment (Future - Phase 2)
- Domain-specific expertise level classification
- Temporal progression tracking
- Multi-domain expertise profiles
- Signal extraction from behavior + prompt patterns
- Expertise evolution detection

### 3. System Management
- Cluster state management (centroid persistence)
- Semantic cache operations
- Analysis history and versioning
- Performance monitoring
- Configuration management

---

## API Endpoints Structure

```
/api/v1
├── /analysis                    # Core Behaviour Analysis
│   ├── POST /analyze            # Primary analysis endpoint
│   ├── POST /analyze/incremental   # Incremental update
│   ├── GET  /results/{user_id}     # Get latest results
│   ├── GET  /history/{user_id}     # Analysis history
│   └── DELETE /reset/{user_id}     # Reset user analysis
│
├── /clustering                  # Clustering Operations
│   ├── POST /cluster/full       # Force full re-clustering
│   ├── GET  /centroids/{user_id}   # Get user centroids
│   ├── GET  /clusters/{user_id}    # Get cluster details
│   └── POST /validate           # Validate cluster quality
│
├── /core-behaviors              # Core Behaviour Management
│   ├── GET  /list/{user_id}     # List core behaviors
│   ├── GET  /{core_behavior_id} # Get specific core behavior
│   ├── GET  /evidence/{core_behavior_id}  # Get evidence chain
│   └── POST /compare            # Compare versions
│
├── /expertise                   # Expertise Assessment (Phase 2)
│   ├── POST /assess             # Assess expertise levels
│   ├── GET  /profile/{user_id}  # Get expertise profile
│   ├── GET  /domains/{user_id}  # List detected domains
│   ├── GET  /progression/{user_id}/{domain}  # Track progression
│   └── POST /signals/extract    # Extract expertise signals
│
├── /cache                       # Semantic Cache Management
│   ├── GET  /stats              # Cache statistics
│   ├── POST /search             # Search cache for similar patterns
│   ├── POST /invalidate         # Invalidate cache entries
│   └── GET  /efficiency         # Cache hit/miss metrics
│
├── /health                      # System Health & Monitoring
│   ├── GET  /                   # Health check
│   ├── GET  /metrics            # System metrics
│   └── GET  /status             # Component status
│
└── /admin                       # Administrative Operations
    ├── POST /config             # Update configuration
    ├── GET  /config             # Get current config
    ├── POST /maintenance        # Trigger maintenance tasks
    └── GET  /logs               # Query system logs
```

---

## 1. Core Behaviour Analysis Endpoints

### 1.1 Primary Analysis Endpoint

**Endpoint:** `POST /api/v1/analysis/analyze`

**Description:** Analyzes user behaviors and derives core behavioral patterns. Automatically determines whether to use incremental or full clustering based on system state.

**Request Body:**
```json
{
  "user_id": "user_stable_users_01",
  "behaviors": [
    {
      "behavior_id": "beh_001",
      "behavior_text": "prefers visual learning methods",
      "credibility": 0.85,
      "reinforcement_count": 5,
      "decay_rate": 0.01,
      "created_at": 1732180002,
      "last_seen": 1732300112,
      "prompt_history_ids": ["prompt_001", "prompt_045"],
      "clarity_score": 0.87,
      "extraction_confidence": 0.92,
      "session_id": "session_001"
    }
    // ... more behaviors
  ],
  "options": {
    "force_full_clustering": false,
    "include_evidence_details": true,
    "min_cluster_size": 3,
    "confidence_threshold": 0.70
  }
}
```

**Response:** `200 OK`
```json
{
  "analysis_id": "analysis_8f2a9d",
  "user_id": "user_stable_users_01",
  "timestamp": 1732500000,
  "processing_mode": "incremental",
  "execution_time_ms": 523,
  "results": {
    "core_behaviors": [
      {
        "core_behavior_id": "cb_001",
        "generalized_text": "prefers visual learning approaches",
        "confidence": 0.85,
        "stability_score": 0.78,
        "source_behavior_count": 5,
        "cluster_id": "cluster_01",
        "created_at": 1732500000,
        "last_updated": 1732500000,
        "version": 1,
        "evidence_chain": {
          "source_behavior_ids": ["beh_001", "beh_023", "beh_045"],
          "prompt_ids": ["prompt_001", "prompt_045", "prompt_089"],
          "cluster_metrics": {
            "semantic_coherence": 0.82,
            "credibility_aggregate": 0.84,
            "temporal_spread_days": 45
          },
          "derivation_method": "llm_generalization",
          "cache_hit": true
        }
      }
      // ... more core behaviors
    ],
    "clusters": {
      "total_clusters": 4,
      "behaviors_clustered": 32,
      "orphan_behaviors": 3,
      "new_clusters_created": 1,
      "centroids_updated": 3
    },
    "quality_metrics": {
      "overall_confidence": 0.81,
      "clustering_silhouette_score": 0.67,
      "cache_hit_rate": 0.45
    }
  },
  "metadata": {
    "behaviors_analyzed": 35,
    "previous_analysis_id": "analysis_7a1b2c",
    "changes_from_previous": {
      "new_core_behaviors": 1,
      "updated_core_behaviors": 2,
      "retired_core_behaviors": 0
    }
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `404 Not Found` - User not found
- `500 Internal Server Error` - Processing failure

---

### 1.2 Incremental Analysis Endpoint

**Endpoint:** `POST /api/v1/analysis/analyze/incremental`

**Description:** Explicitly triggers incremental clustering for new behaviors. Requires previous analysis state to exist.

**Request Body:**
```json
{
  "user_id": "user_stable_users_01",
  "new_behaviors": [
    {
      "behavior_id": "beh_036",
      "behavior_text": "enjoys collaborative problem-solving",
      "credibility": 0.82,
      "reinforcement_count": 3,
      // ... other fields
    }
  ],
  "options": {
    "assignment_threshold": 0.80,
    "create_new_clusters": true,
    "min_orphan_pool_size": 3
  }
}
```

**Response:** `200 OK`
```json
{
  "analysis_id": "analysis_9c3d4e",
  "user_id": "user_stable_users_01",
  "processing_mode": "incremental",
  "execution_time_ms": 287,
  "results": {
    "assignments": [
      {
        "behavior_id": "beh_036",
        "assigned_to_cluster": "cluster_02",
        "distance": 0.73,
        "confidence": 0.85
      }
    ],
    "new_clusters": [],
    "orphaned_behaviors": [],
    "centroid_updates": [
      {
        "cluster_id": "cluster_02",
        "previous_members": 5,
        "new_members": 6,
        "centroid_shift": 0.04
      }
    ]
  },
  "should_trigger_full_clustering": false,
  "reassignment_rate": 0.03
}
```

---

### 1.3 Get Analysis Results

**Endpoint:** `GET /api/v1/analysis/results/{user_id}`

**Description:** Retrieves the most recent analysis results for a user.

**Query Parameters:**
- `include_evidence` (boolean, default: false) - Include detailed evidence chains
- `version` (integer, optional) - Specific version to retrieve

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "latest_analysis_id": "analysis_8f2a9d",
  "analysis_timestamp": 1732500000,
  "core_behaviors": [/* array of core behaviors */],
  "summary": {
    "total_core_behaviors": 4,
    "avg_confidence": 0.83,
    "oldest_behavior_age_days": 67,
    "last_updated": 1732500000
  }
}
```

---

### 1.4 Get Analysis History

**Endpoint:** `GET /api/v1/analysis/history/{user_id}`

**Description:** Retrieves historical analysis results for tracking changes over time.

**Query Parameters:**
- `limit` (integer, default: 10) - Number of historical records
- `start_date` (timestamp, optional) - Filter from date
- `end_date` (timestamp, optional) - Filter to date

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "total_analyses": 15,
  "history": [
    {
      "analysis_id": "analysis_8f2a9d",
      "timestamp": 1732500000,
      "core_behavior_count": 4,
      "processing_mode": "incremental",
      "execution_time_ms": 523,
      "changes": {
        "added": 1,
        "updated": 2,
        "removed": 0
      }
    }
    // ... more historical entries
  ]
}
```

---

### 1.5 Reset User Analysis

**Endpoint:** `DELETE /api/v1/analysis/reset/{user_id}`

**Description:** Resets all analysis state for a user (centroids, cache entries, core behaviors). Next analysis will be full clustering.

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "reset_timestamp": 1732500000,
  "cleared_items": {
    "core_behaviors": 4,
    "cluster_centroids": 5,
    "cache_entries": 12,
    "analysis_history": 15
  },
  "message": "User analysis state completely reset. Next analysis will perform full clustering."
}
```

---

## 2. Clustering Operations Endpoints

### 2.1 Force Full Re-clustering

**Endpoint:** `POST /api/v1/clustering/cluster/full`

**Description:** Forces a complete re-clustering from scratch, ignoring existing centroids.

**Request Body:**
```json
{
  "user_id": "user_stable_users_01",
  "behaviors": [/* all behaviors */],
  "options": {
    "min_cluster_size": 3,
    "min_samples": 2,
    "clustering_algorithm": "hdbscan"
  }
}
```

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "clustering_id": "cluster_full_9d2e3f",
  "timestamp": 1732500000,
  "execution_time_ms": 3420,
  "results": {
    "total_clusters": 5,
    "behaviors_clustered": 48,
    "orphan_behaviors": 2,
    "centroids_created": 5,
    "silhouette_score": 0.71,
    "cluster_sizes": [12, 10, 9, 8, 9]
  },
  "centroids": [
    {
      "cluster_id": "cluster_01",
      "centroid_vector": [0.234, -0.456, /* ... */],
      "member_count": 12,
      "coherence_score": 0.84
    }
    // ... more centroids
  ]
}
```

---

### 2.2 Get User Centroids

**Endpoint:** `GET /api/v1/clustering/centroids/{user_id}`

**Description:** Retrieves stored cluster centroids for a user.

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "total_centroids": 5,
  "last_updated": 1732500000,
  "embedding_model": "all-MiniLM-L6-v2",
  "centroids": [
    {
      "cluster_id": "cluster_01",
      "centroid_hash": "a3f8c2d1...",
      "member_behavior_ids": ["beh_001", "beh_023", "beh_045"],
      "member_count": 12,
      "coherence_score": 0.84,
      "created_at": 1732400000,
      "last_updated": 1732500000
    }
    // ... more centroids
  ]
}
```

---

### 2.3 Get Cluster Details

**Endpoint:** `GET /api/v1/clustering/clusters/{user_id}`

**Description:** Get detailed information about all clusters for a user.

**Query Parameters:**
- `cluster_id` (string, optional) - Specific cluster to retrieve
- `include_members` (boolean, default: false) - Include full behavior details

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "total_clusters": 5,
  "clusters": [
    {
      "cluster_id": "cluster_01",
      "size": 12,
      "coherence_score": 0.84,
      "avg_credibility": 0.82,
      "temporal_span_days": 54,
      "core_behavior_id": "cb_001",
      "member_behavior_ids": ["beh_001", "beh_023", /* ... */],
      "representative_behaviors": [
        "prefers visual learning methods",
        "likes diagram-based explanations",
        "requests infographics frequently"
      ]
    }
    // ... more clusters
  ]
}
```

---

### 2.4 Validate Cluster Quality

**Endpoint:** `POST /api/v1/clustering/validate`

**Description:** Validates clustering quality using various metrics.

**Request Body:**
```json
{
  "user_id": "user_stable_users_01",
  "metrics": ["silhouette", "coherence", "stability"]
}
```

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "validation_timestamp": 1732500000,
  "overall_quality": "good",
  "metrics": {
    "silhouette_score": 0.67,
    "avg_coherence": 0.81,
    "temporal_stability": 0.74,
    "cluster_balance": 0.68
  },
  "recommendations": [
    "Cluster 3 has low coherence (0.62) - consider splitting",
    "2 orphan behaviors could potentially form a new cluster"
  ]
}
```

---

## 3. Core Behaviour Management Endpoints

### 3.1 List Core Behaviors

**Endpoint:** `GET /api/v1/core-behaviors/list/{user_id}`

**Description:** Lists all core behaviors for a user.

**Query Parameters:**
- `min_confidence` (float, default: 0.0) - Filter by minimum confidence
- `sort_by` (string, default: "confidence") - Sort order: confidence, created_at, stability
- `limit` (integer, optional) - Maximum results to return

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "total_core_behaviors": 4,
  "filters_applied": {
    "min_confidence": 0.70
  },
  "core_behaviors": [
    {
      "core_behavior_id": "cb_001",
      "generalized_text": "prefers visual learning approaches",
      "confidence": 0.85,
      "stability_score": 0.78,
      "source_behavior_count": 5,
      "created_at": 1732400000,
      "last_updated": 1732500000,
      "version": 2,
      "status": "active"
    }
    // ... more core behaviors
  ]
}
```

---

### 3.2 Get Specific Core Behavior

**Endpoint:** `GET /api/v1/core-behaviors/{core_behavior_id}`

**Description:** Get detailed information about a specific core behavior.

**Query Parameters:**
- `include_evidence` (boolean, default: true) - Include evidence chain
- `include_source_behaviors` (boolean, default: false) - Include full source behavior details

**Response:** `200 OK`
```json
{
  "core_behavior_id": "cb_001",
  "user_id": "user_stable_users_01",
  "generalized_text": "prefers visual learning approaches",
  "confidence": 0.85,
  "stability_score": 0.78,
  "source_behavior_count": 5,
  "cluster_id": "cluster_01",
  "created_at": 1732400000,
  "last_updated": 1732500000,
  "version": 2,
  "status": "active",
  "evidence_chain": {
    "source_behavior_ids": ["beh_001", "beh_023", "beh_045"],
    "prompt_ids": ["prompt_001", "prompt_045", "prompt_089"],
    "cluster_metrics": {
      "semantic_coherence": 0.82,
      "credibility_aggregate": 0.84,
      "temporal_spread_days": 45
    },
    "derivation_method": "llm_generalization",
    "cache_hit": true,
    "llm_model": "claude-sonnet-4",
    "generated_at": 1732500000
  },
  "source_behaviors": [
    {
      "behavior_id": "beh_001",
      "behavior_text": "prefers visual learning methods",
      "credibility": 0.85,
      "reinforcement_count": 5
    }
    // ... more if include_source_behaviors=true
  ]
}
```

---

### 3.3 Get Evidence Chain

**Endpoint:** `GET /api/v1/core-behaviors/evidence/{core_behavior_id}`

**Description:** Retrieves detailed evidence chain for a core behavior.

**Query Parameters:**
- `include_prompts` (boolean, default: false) - Include prompt IDs (metadata only)
- `include_metrics` (boolean, default: true) - Include clustering metrics

**Response:** `200 OK`
```json
{
  "core_behavior_id": "cb_001",
  "evidence_chain": {
    "derivation_timestamp": 1732500000,
    "source_behaviors": [
      {
        "behavior_id": "beh_001",
        "contribution_weight": 0.35,
        "credibility": 0.85,
        "reinforcement_count": 5
      }
      // ... more sources
    ],
    "prompt_references": [
      {
        "prompt_id": "prompt_001",
        "timestamp": 1732180002,
        "behavior_ids_triggered": ["beh_001", "beh_023"]
      }
      // ... more prompts
    ],
    "clustering_evidence": {
      "cluster_id": "cluster_01",
      "cluster_size": 12,
      "semantic_coherence": 0.82,
      "credibility_aggregate": 0.84,
      "silhouette_score": 0.71
    },
    "derivation_logic": {
      "method": "llm_generalization",
      "cache_hit": true,
      "cache_similarity": 0.96,
      "llm_model": "claude-sonnet-4",
      "prompt_template_version": "v2.1"
    },
    "confidence_calculation": {
      "credibility_component": 0.336,
      "stability_component": 0.234,
      "coherence_component": 0.246,
      "cache_adjustment": -0.05,
      "final_confidence": 0.85
    }
  }
}
```

---

### 3.4 Compare Core Behavior Versions

**Endpoint:** `POST /api/v1/core-behaviors/compare`

**Description:** Compares different versions of core behaviors or compares current vs. historical state.

**Request Body:**
```json
{
  "user_id": "user_stable_users_01",
  "comparison_type": "temporal",
  "from_timestamp": 1732400000,
  "to_timestamp": 1732500000
}
```

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "comparison_period": {
    "from": 1732400000,
    "to": 1732500000,
    "days_elapsed": 1
  },
  "changes": {
    "new_core_behaviors": [
      {
        "core_behavior_id": "cb_005",
        "generalized_text": "interested in collaborative coding practices",
        "confidence": 0.78
      }
    ],
    "updated_core_behaviors": [
      {
        "core_behavior_id": "cb_001",
        "changes": {
          "confidence": {"from": 0.82, "to": 0.85},
          "stability_score": {"from": 0.74, "to": 0.78},
          "source_behavior_count": {"from": 4, "to": 5}
        }
      }
    ],
    "retired_core_behaviors": [],
    "unchanged_core_behaviors": ["cb_002", "cb_003", "cb_004"]
  },
  "summary": {
    "total_changes": 2,
    "stability_trend": "improving",
    "avg_confidence_change": 0.03
  }
}
```

---

## 4. Expertise Assessment Endpoints (Phase 2 - Future)

### 4.1 Assess Expertise

**Endpoint:** `POST /api/v1/expertise/assess`

**Description:** Assesses user expertise levels across detected domains.

**Request Body:**
```json
{
  "user_id": "user_stable_users_01",
  "behaviors": [/* array of behaviors */],
  "options": {
    "include_signal_breakdown": true,
    "temporal_weighting": true,
    "domains": null  // null = auto-detect, or specify ["programming", "design"]
  }
}
```

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "assessment_id": "expertise_7b3c9a",
  "timestamp": 1732500000,
  "expertise_profiles": [
    {
      "domain": "programming",
      "expertise_level": "intermediate",
      "signal_strength": 0.58,
      "confidence": 0.76,
      "stability": 0.72,
      "behavior_count": 18,
      "signal_breakdown": {
        "terminology_sophistication": 0.65,
        "question_complexity": 0.54,
        "reinforcement_depth": 0.62,
        "problem_solving_patterns": 0.58,
        "error_recovery": 0.52
      },
      "evidence_map": {
        "behavior_ids": ["beh_003", "beh_012", /* ... */],
        "prompt_ids": ["prompt_005", "prompt_023", /* ... */],
        "key_indicators": [
          "Uses domain-specific terminology (15 occurrences)",
          "Demonstrates structured problem-solving (8 instances)",
          "Shows understanding of core concepts (12 behaviors)"
        ]
      },
      "progression": {
        "trend": "improving",
        "previous_level": "novice",
        "level_changed_at": 1732300000,
        "days_at_current_level": 2
      }
    }
    // ... more domains
  ],
  "summary": {
    "total_domains": 3,
    "avg_expertise_level": "intermediate",
    "most_confident_domain": "programming",
    "emerging_domains": ["design"]
  }
}
```

---

### 4.2 Get Expertise Profile

**Endpoint:** `GET /api/v1/expertise/profile/{user_id}`

**Description:** Retrieves the current expertise profile for a user.

**Query Parameters:**
- `domain` (string, optional) - Filter by specific domain
- `include_history` (boolean, default: false) - Include historical assessments

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "profile_timestamp": 1732500000,
  "domains": [
    {
      "domain": "programming",
      "expertise_level": "intermediate",
      "confidence": 0.76,
      "stability": 0.72,
      "first_detected": 1732100000,
      "last_assessed": 1732500000,
      "behavior_count": 18
    }
    // ... more domains
  ],
  "overall_summary": {
    "total_domains": 3,
    "primary_domain": "programming",
    "expertise_distribution": {
      "novice": 0,
      "intermediate": 2,
      "advanced": 1,
      "expert": 0
    }
  }
}
```

---

### 4.3 List Detected Domains

**Endpoint:** `GET /api/v1/expertise/domains/{user_id}`

**Description:** Lists all domains detected from user behaviors.

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "total_domains": 3,
  "domains": [
    {
      "domain": "programming",
      "behavior_count": 18,
      "first_detected": 1732100000,
      "confidence": 0.82,
      "keywords": ["code", "python", "function", "algorithm"]
    },
    {
      "domain": "design",
      "behavior_count": 12,
      "first_detected": 1732200000,
      "confidence": 0.75,
      "keywords": ["layout", "color", "typography", "ui"]
    },
    {
      "domain": "photography",
      "behavior_count": 8,
      "first_detected": 1732300000,
      "confidence": 0.68,
      "keywords": ["exposure", "composition", "lighting"]
    }
  ]
}
```

---

### 4.4 Track Expertise Progression

**Endpoint:** `GET /api/v1/expertise/progression/{user_id}/{domain}`

**Description:** Tracks how expertise has evolved in a specific domain over time.

**Query Parameters:**
- `start_date` (timestamp, optional) - Start of tracking period
- `end_date` (timestamp, optional) - End of tracking period
- `granularity` (string, default: "week") - Data point frequency: day, week, month

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "domain": "programming",
  "tracking_period": {
    "start": 1732100000,
    "end": 1732500000,
    "days": 5
  },
  "progression_timeline": [
    {
      "timestamp": 1732100000,
      "expertise_level": "novice",
      "signal_strength": 0.28,
      "confidence": 0.65,
      "behavior_count": 5
    },
    {
      "timestamp": 1732300000,
      "expertise_level": "intermediate",
      "signal_strength": 0.58,
      "confidence": 0.76,
      "behavior_count": 18
    }
  ],
  "trend_analysis": {
    "direction": "improving",
    "rate_of_change": 0.30,
    "predicted_next_level": "advanced",
    "estimated_days_to_next_level": 15
  },
  "milestones": [
    {
      "timestamp": 1732300000,
      "event": "level_up",
      "from_level": "novice",
      "to_level": "intermediate",
      "trigger": "signal_strength_threshold"
    }
  ]
}
```

---

### 4.5 Extract Expertise Signals

**Endpoint:** `POST /api/v1/expertise/signals/extract`

**Description:** Extracts raw expertise signals from behaviors and prompts without classification.

**Request Body:**
```json
{
  "user_id": "user_stable_users_01",
  "domain": "programming",
  "behaviors": [/* array of behaviors */],
  "analyze_prompts": true
}
```

**Response:** `200 OK`
```json
{
  "user_id": "user_stable_users_01",
  "domain": "programming",
  "extraction_timestamp": 1732500000,
  "signals": {
    "terminology_analysis": {
      "domain_specific_terms": 45,
      "advanced_concepts": 12,
      "sophistication_score": 0.65
    },
    "behavioral_patterns": {
      "question_types": {
        "basic": 3,
        "intermediate": 8,
        "advanced": 7
      },
      "problem_solving_indicators": 15,
      "self_correction_instances": 4
    },
    "temporal_patterns": {
      "consistency_score": 0.72,
      "engagement_frequency": "high",
      "progression_detected": true
    },
    "reinforcement_metrics": {
      "avg_reinforcement_count": 4.2,
      "avg_credibility": 0.79,
      "stable_behavior_count": 12
    }
  },
  "raw_indicators": [
    {
      "type": "terminology",
      "indicator": "Uses advanced OOP concepts",
      "evidence_count": 5,
      "confidence": 0.82
    },
    {
      "type": "problem_solving",
      "indicator": "Demonstrates algorithm optimization",
      "evidence_count": 3,
      "confidence": 0.76
    }
    // ... more indicators
  ]
}
```

---

## 5. Semantic Cache Management Endpoints

### 5.1 Get Cache Statistics

**Endpoint:** `GET /api/v1/cache/stats`

**Description:** Retrieves semantic cache performance statistics.

**Response:** `200 OK`
```json
{
  "cache_summary": {
    "total_entries": 1247,
    "total_size_mb": 45.3,
    "oldest_entry_age_days": 87,
    "newest_entry_age_days": 0
  },
  "performance_metrics": {
    "cache_hit_rate": 0.58,
    "avg_similarity_on_hit": 0.96,
    "total_llm_calls_saved": 523,
    "estimated_cost_savings_usd": 12.45
  },
  "usage_stats": {
    "lookups_last_24h": 142,
    "hits_last_24h": 81,
    "misses_last_24h": 61,
    "new_entries_last_24h": 34
  },
  "top_reused_entries": [
    {
      "cache_id": "cache_8f2a9d",
      "generalized_statement": "prefers visual learning methods",
      "reuse_count": 47,
      "last_reused": 1732500000
    }
    // ... more entries
  ]
}
```

---

### 5.2 Search Cache

**Endpoint:** `POST /api/v1/cache/search`

**Description:** Search for similar cached generalizations.

**Request Body:**
```json
{
  "query_behaviors": [
    "likes diagrams and charts",
    "prefers visual explanations",
    "requests infographics"
  ],
  "similarity_threshold": 0.90,
  "max_results": 5
}
```

**Response:** `200 OK`
```json
{
  "query_timestamp": 1732500000,
  "results": [
    {
      "cache_id": "cache_8f2a9d",
      "generalized_statement": "prefers visual learning methods",
      "similarity_score": 0.96,
      "source_cluster_size": 5,
      "reuse_count": 47,
      "confidence": 0.85,
      "created_at": 1732300000
    }
    // ... more results
  ],
  "search_stats": {
    "total_searched": 1247,
    "matches_found": 3,
    "avg_similarity": 0.93,
    "search_time_ms": 45
  }
}
```

---

### 5.3 Invalidate Cache Entries

**Endpoint:** `POST /api/v1/cache/invalidate`

**Description:** Manually invalidate cache entries.

**Request Body:**
```json
{
  "invalidation_criteria": {
    "older_than_days": 90,
    "reuse_count_less_than": 2,
    "specific_cache_ids": ["cache_abc123"]
  }
}
```

**Response:** `200 OK`
```json
{
  "invalidation_timestamp": 1732500000,
  "entries_invalidated": 45,
  "space_freed_mb": 2.3,
  "criteria_applied": {
    "older_than_days": 90,
    "reuse_count_less_than": 2
  }
}
```

---

### 5.4 Get Cache Efficiency Metrics

**Endpoint:** `GET /api/v1/cache/efficiency`

**Description:** Detailed cache efficiency and cost analysis.

**Query Parameters:**
- `time_period` (string, default: "7d") - Analysis period: 1d, 7d, 30d, all

**Response:** `200 OK`
```json
{
  "analysis_period": "7d",
  "efficiency_metrics": {
    "hit_rate": 0.58,
    "miss_rate": 0.42,
    "avg_lookup_time_ms": 23,
    "avg_similarity_on_hit": 0.96
  },
  "cost_analysis": {
    "llm_calls_saved": 523,
    "llm_calls_made": 378,
    "total_llm_calls_without_cache": 901,
    "cost_savings_percentage": 58.0,
    "estimated_savings_usd": 12.45
  },
  "recommendations": [
    "Cache hit rate is optimal (>50%)",
    "Consider increasing similarity threshold to 0.97 for higher quality",
    "23 entries have 0 reuse - consider removing"
  ]
}
```

---

## 6. System Health & Monitoring Endpoints

### 6.1 Health Check

**Endpoint:** `GET /api/v1/health/`

**Description:** Basic health check endpoint.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": 1732500000,
  "version": "1.0.0",
  "uptime_seconds": 345678
}
```

---

### 6.2 System Metrics

**Endpoint:** `GET /api/v1/health/metrics`

**Description:** Detailed system performance metrics.

**Response:** `200 OK`
```json
{
  "timestamp": 1732500000,
  "api_metrics": {
    "total_requests_24h": 1523,
    "avg_response_time_ms": 234,
    "error_rate": 0.02,
    "active_connections": 12
  },
  "processing_metrics": {
    "analyses_completed_24h": 87,
    "avg_analysis_time_ms": 523,
    "incremental_analysis_percentage": 0.89,
    "full_clustering_executions_24h": 3
  },
  "resource_usage": {
    "cpu_usage_percent": 23.5,
    "memory_usage_mb": 1245.6,
    "disk_usage_mb": 4521.3
  },
  "cache_metrics": {
    "hit_rate_24h": 0.58,
    "size_mb": 45.3,
    "entries": 1247
  }
}
```

---

### 6.3 Component Status

**Endpoint:** `GET /api/v1/health/status`

**Description:** Status of all system components.

**Response:** `200 OK`
```json
{
  "timestamp": 1732500000,
  "overall_status": "healthy",
  "components": {
    "api_server": {
      "status": "healthy",
      "uptime_seconds": 345678
    },
    "clustering_engine": {
      "status": "healthy",
      "last_execution": 1732499500,
      "active_jobs": 2
    },
    "llm_service": {
      "status": "healthy",
      "provider": "anthropic",
      "model": "claude-sonnet-4",
      "rate_limit_remaining": 890
    },
    "semantic_cache": {
      "status": "healthy",
      "entries": 1247,
      "hit_rate": 0.58
    },
    "embedding_service": {
      "status": "healthy",
      "model": "all-MiniLM-L6-v2",
      "last_used": 1732499800
    }
  }
}
```

---

## 7. Administrative Endpoints

### 7.1 Update Configuration

**Endpoint:** `POST /api/v1/admin/config`

**Description:** Update system configuration parameters.

**Request Body:**
```json
{
  "clustering": {
    "min_cluster_size": 3,
    "assignment_threshold": 0.80,
    "full_clustering_interval_days": 30
  },
  "core_behaviors": {
    "min_confidence": 0.70,
    "stability_threshold": 0.50
  },
  "cache": {
    "similarity_threshold": 0.95,
    "ttl_days": 90,
    "max_size_mb": 100
  }
}
```

**Response:** `200 OK`
```json
{
  "updated_at": 1732500000,
  "parameters_updated": 8,
  "requires_restart": false,
  "message": "Configuration updated successfully"
}
```

---

### 7.2 Get Current Configuration

**Endpoint:** `GET /api/v1/admin/config`

**Description:** Retrieve current system configuration.

**Response:** `200 OK`
```json
{
  "current_config": {
    "clustering": {
      "min_cluster_size": 3,
      "assignment_threshold": 0.80,
      "full_clustering_interval_days": 30,
      "embedding_model": "all-MiniLM-L6-v2"
    },
    "core_behaviors": {
      "min_confidence": 0.70,
      "stability_threshold": 0.50,
      "max_core_behaviors_per_user": 50
    },
    "cache": {
      "similarity_threshold": 0.95,
      "ttl_days": 90,
      "max_size_mb": 100
    },
    "llm": {
      "provider": "anthropic",
      "model": "claude-sonnet-4",
      "max_tokens": 50,
      "temperature": 0.3
    }
  },
  "last_updated": 1732400000
}
```

---

### 7.3 Trigger Maintenance Tasks

**Endpoint:** `POST /api/v1/admin/maintenance`

**Description:** Manually trigger maintenance operations.

**Request Body:**
```json
{
  "tasks": ["cache_cleanup", "full_reclustering", "log_rotation"],
  "user_ids": null,  // null = all users, or specify ["user_001", "user_002"]
  "force": false
}
```

**Response:** `202 Accepted`
```json
{
  "task_id": "maintenance_7c4d8e",
  "scheduled_at": 1732500000,
  "tasks_queued": ["cache_cleanup", "full_reclustering", "log_rotation"],
  "affected_users": "all",
  "estimated_duration_minutes": 45,
  "message": "Maintenance tasks scheduled successfully"
}
```

---

### 7.4 Query System Logs

**Endpoint:** `GET /api/v1/admin/logs`

**Description:** Query system logs for debugging and monitoring.

**Query Parameters:**
- `level` (string, optional) - Filter by log level: debug, info, warning, error
- `start_time` (timestamp, optional) - Start of time range
- `end_time` (timestamp, optional) - End of time range
- `limit` (integer, default: 100) - Maximum results
- `search` (string, optional) - Search term

**Response:** `200 OK`
```json
{
  "total_logs": 523,
  "returned_logs": 100,
  "filters_applied": {
    "level": "error",
    "time_range": "last_24h"
  },
  "logs": [
    {
      "timestamp": 1732499990,
      "level": "error",
      "component": "clustering_engine",
      "message": "Failed to assign behavior beh_xyz to cluster",
      "user_id": "user_stable_users_01",
      "error_code": "CLUSTER_ASSIGNMENT_FAILED",
      "details": {
        "behavior_id": "beh_xyz",
        "min_distance": 0.92,
        "threshold": 0.80
      }
    }
    // ... more logs
  ]
}
```

---

## Common Response Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 202 | Accepted - Request accepted for processing |
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict (e.g., duplicate analysis) |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server-side error |
| 503 | Service Unavailable - Service temporarily down |

---

## Common Request Headers

```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token}  // If authentication enabled
X-Request-ID: {uuid}  // For request tracking
```

---

## Common Response Headers

```
Content-Type: application/json
X-Request-ID: {uuid}  // Echo of request ID
X-Response-Time-Ms: {duration}  // Processing time
X-Rate-Limit-Remaining: {count}  // Remaining requests
X-Rate-Limit-Reset: {timestamp}  // Rate limit reset time
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "User ID is required",
    "details": {
      "field": "user_id",
      "constraint": "non_empty_string"
    },
    "timestamp": 1732500000,
    "request_id": "req_7f3a9d"
  }
}
```

---

## Pagination Format

Endpoints returning large datasets support pagination:

```json
{
  "data": [/* array of items */],
  "pagination": {
    "total_items": 523,
    "page": 1,
    "page_size": 50,
    "total_pages": 11,
    "has_next": true,
    "has_prev": false,
    "next_url": "/api/v1/analysis/history?page=2",
    "prev_url": null
  }
}
```

---

## Webhook Support (Future)

Future versions will support webhooks for asynchronous notifications:

```json
{
  "webhook_url": "https://your-app.com/webhooks/cbac",
  "events": [
    "analysis.completed",
    "core_behavior.created",
    "expertise.level_changed",
    "maintenance.completed"
  ]
}
```

---

## Rate Limiting

Default rate limits (configurable):
- **Anonymous:** 100 requests/hour
- **Authenticated:** 1000 requests/hour
- **Analysis endpoints:** 50 analyses/hour per user
- **Admin endpoints:** 20 requests/hour

---

## Authentication & Authorization (Future)

Phase 1 implementation may not include authentication. Future versions will support:
- API Key authentication
- JWT-based authentication
- Role-based access control (RBAC)
- User-level isolation (users can only access their own data)

---

## Implementation Phases

### Phase 1 (Current - Core Behaviour Focus)
✅ Implement:
- All `/analysis` endpoints
- All `/clustering` endpoints
- All `/core-behaviors` endpoints
- Basic `/cache` endpoints
- All `/health` endpoints
- Basic `/admin` endpoints

⏸️ Defer to Phase 2:
- All `/expertise` endpoints (5.1 - 5.5)
- Advanced cache features
- Webhook support
- Authentication/Authorization

### Phase 2 (Future - Expertise Assessment)
- Implement all `/expertise` endpoints
- Enhanced signal extraction
- Temporal progression tracking
- Multi-domain expertise profiles

---

## Notes for Implementation

1. **Start with Phase 1 endpoints** - Focus on core behaviour analysis
2. **Design with Phase 2 in mind** - Use extensible data models
3. **All endpoints should be async** - Use FastAPI async capabilities
4. **Database agnostic** - Use abstraction layer for future DB migration
5. **Extensive logging** - Log all operations for debugging
6. **Input validation** - Use Pydantic models for all requests
7. **Error handling** - Comprehensive error handling with meaningful messages
8. **Testing friendly** - Design endpoints to be easily testable with our generated datasets

---

**Document Status:** Ready for Implementation  
**Next Step:** Begin FastAPI project structure and Phase 1 endpoint implementation
