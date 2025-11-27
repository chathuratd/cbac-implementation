# CBAC API - Core Behaviour Analysis Component

REST API for analyzing user behaviors, performing semantic clustering, and deriving core behavioral patterns.

## 🎯 Features

- **Behavior Analysis**: Analyze user interaction patterns from behavior data
- **Semantic Clustering**: HDBSCAN-based clustering of similar behaviors
- **Core Behavior Derivation**: Extract generalized patterns with confidence scores
- **Evidence Traceability**: Full chain from core behaviors back to source data
- **Database Integration**: Qdrant (vector embeddings) + MongoDB (document storage)

## 🏗️ Architecture

```
behaviors_db.json → Qdrant (with embeddings)
                        ↓
                  [CBAC API]
                        ↓
              Clustering → Core Behaviors

prompts_db.json → MongoDB (metadata)
```

## 📁 Project Structure

```
cbac_api/
├── app/
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── models/
│   │   └── schemas.py            # Pydantic data models
│   ├── services/
│   │   ├── vector_store.py       # Qdrant integration
│   │   ├── document_store.py     # MongoDB integration
│   │   ├── clustering.py         # HDBSCAN clustering
│   │   └── core_analyzer.py      # Core behavior derivation
│   └── routers/
│       ├── analysis.py           # Analysis endpoints
│       └── health.py             # Health check endpoints
├── main.py                       # FastAPI application
├── requirements.txt              # Python dependencies
└── .env                          # Environment configuration
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker (for Qdrant and MongoDB)
- Qdrant running on `localhost:6333`
- MongoDB running on `localhost:27017`

### Installation

1. **Install dependencies:**
```bash
cd cbac_api
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
# .env file is already created with default values
# Modify if your database URLs are different
```

3. **Ensure data is loaded:**
```bash
# Make sure you've run these scripts first:
# - vector_db_save.py (loads behaviors into Qdrant)
# - mongo_db_save.py (loads prompts into MongoDB)
```

### Running the API

```bash
# Development mode (auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Analysis

#### `POST /analysis`
Analyze user behaviors and derive core behavioral patterns.

**Request:**
```json
{
  "user_id": "user_stable_users_01",
  "min_cluster_size": 3,
  "include_prompts": false
}
```

**Response:**
```json
{
  "user_id": "user_stable_users_01",
  "core_behaviors": [
    {
      "core_behavior_id": "core_user_stable_users_01_0_abc123",
      "user_id": "user_stable_users_01",
      "generalized_statement": "User demonstrates deep engagement in gardening at intermediate level",
      "confidence_score": 0.87,
      "evidence_chain": ["beh_001", "beh_002", "beh_003"],
      "cluster_id": 0,
      "domain_detected": "gardening",
      "metadata": {}
    }
  ],
  "total_behaviors_analyzed": 33,
  "num_clusters": 3,
  "analysis_timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "processing_time_ms": 1250,
    "quality_metrics": {}
  }
}
```

#### `GET /analysis/{user_id}/summary`
Get quick summary of user's behavior data.

### Health

#### `GET /health`
System health check.

#### `GET /health/metrics`
Database statistics and metrics.

#### `GET /health/status/{component}`
Detailed status for specific component (qdrant/mongodb).

## 🧪 Testing

### Test with dev_baseline scenario

```bash
# Analyze user_stable_users_01
curl -X POST http://localhost:8000/analysis \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_stable_users_01", "min_cluster_size": 3}'
```

### Get summary first

```bash
curl http://localhost:8000/analysis/user_stable_users_01/summary
```

## 🔧 Configuration

All settings in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |
| `MONGODB_URL` | `mongodb://admin:admin123@localhost:27017/` | MongoDB connection string |
| `MONGODB_DATABASE` | `cbac_system` | Database name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `MIN_CLUSTER_SIZE` | `3` | HDBSCAN min cluster size |
| `MIN_SAMPLES` | `2` | HDBSCAN min samples |
| `API_PORT` | `8000` | API server port |
| `DEBUG` | `True` | Enable debug logging |

## 📊 Data Flow

1. **Request arrives** → POST /analysis with user_id
2. **Fetch behaviors** → Query Qdrant filtered by user_id
3. **Cluster** → HDBSCAN on pre-computed embeddings
4. **Derive** → Generate core behaviors from clusters
5. **Score** → Calculate confidence based on coherence + evidence
6. **Respond** → Return core behaviors with metadata

## 🎓 Test Users Available

- `user_stable_users_01` - Gardening/Cooking/Photography (33 behaviors)
- `user_stable_users_02` - Gardening/Cooking/Photography (33 behaviors)
- `user_stable_users_03` - Gardening/Cooking/Photography (33 behaviors)
- `user_expert_users_01` - Programming/Music/Fitness (33 behaviors)
- `user_expert_users_02` - Programming/Music/Fitness (33 behaviors)
- Plus 5 more users with different patterns

## 📝 Next Steps

- [ ] Add caching layer for repeated analysis
- [ ] Implement incremental clustering
- [ ] Add LLM-based generalization (Phase 2)
- [ ] Add expertise assessment endpoints (Phase 2)
- [ ] Add batch analysis support
- [ ] Add visualization endpoints

## 🐛 Troubleshooting

**"No behaviors found for user"**
- Ensure `vector_db_save.py` has been run
- Check Qdrant is running: `curl http://localhost:6333`

**"MongoDB connection failed"**
- Ensure MongoDB is running: `docker ps | grep mongodb`
- Check credentials in `.env`

**Clustering produces too many/few clusters**
- Adjust `MIN_CLUSTER_SIZE` in `.env`
- Try different values (2-5 recommended)

## 📄 License

MIT
