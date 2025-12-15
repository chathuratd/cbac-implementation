# CBAC API Startup Guide

## ✅ Prerequisites Check

Before starting, verify:

1. **Qdrant is running:**
   ```bash
   curl http://localhost:6333
   # Should return JSON response
   ```

2. **MongoDB is running:**
   ```bash
   docker ps | grep mongodb
   # Should show running container
   ```

3. **Data is loaded:**
   - Run `vector_db_save.py` to load behaviors into Qdrant
   - Run `mongo_db_save.py` to load prompts into MongoDB

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd cbac_api
pip install -r requirements.txt
```

### 2. Start the API

```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Starting CBAC API...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Test the API

Open another terminal:

```bash
# Quick test script
python test_api.py
```

Or manually test:

```bash
# Health check
curl http://localhost:8000/health

# Get user summary
curl http://localhost:8000/analysis/user_stable_users_01/summary

# Run analysis
curl -X POST http://localhost:8000/analysis \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_stable_users_01", "min_cluster_size": 3}'
```

### 4. Explore API Docs

Open in browser:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📝 Example Requests

### Analyze User Behaviors

```bash
curl -X POST http://localhost:8000/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_stable_users_01",
    "min_cluster_size": 3,
    "include_prompts": false
  }'
```

### Get Summary Only

```bash
curl http://localhost:8000/analysis/user_stable_users_01/summary
```

### Check System Health

```bash
curl http://localhost:8000/health
```

### Get Database Metrics

```bash
curl http://localhost:8000/health/metrics
```

## 🎯 Test Users

All users from `test_scenarios.json`:

- `user_stable_users_01` - Gardening, Cooking, Photography
- `user_stable_users_02` - Gardening, Cooking, Photography
- `user_stable_users_03` - Gardening, Cooking, Photography
- `user_expert_users_01` - Programming, Music, Fitness
- `user_expert_users_02` - Programming, Music, Fitness
- `user_evolution_users_01` - Novice → Advanced progression
- `user_evolution_users_02` - Expertise evolution
- `user_noisy_users_01` - Contradictory signals
- `user_noisy_users_02` - Mixed credibility
- `user_sparse_cluster_users_01` - Many small clusters

## 🐛 Troubleshooting

### "No behaviors found for user"
```bash
# Check if Qdrant has data
curl http://localhost:6333/collections/user_behaviors

# Re-run data loading
python vector_db_save.py
```

### "MongoDB connection failed"
```bash
# Check MongoDB is running
docker ps | grep mongo

# Test connection
mongosh "mongodb://admin:admin123@localhost:27017/"
```

### Port 8000 already in use
```bash
# Change port in .env
API_PORT=8001

# Or kill existing process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

## 📊 Expected Output

When you run analysis for `user_stable_users_01`, you should see:

```json
{
  "user_id": "user_stable_users_01",
  "core_behaviors": [
    {
      "generalized_statement": "User demonstrates deep and iterative engagement in gardening at intermediate level",
      "confidence_score": 0.85,
      "domain_detected": "gardening",
      "evidence_chain": ["beh_001", "beh_002", ...]
    },
    {
      "generalized_statement": "User shows consistent follow-up behavior in cooking at intermediate level",
      "confidence_score": 0.82,
      "domain_detected": "cooking",
      "evidence_chain": ["beh_012", "beh_013", ...]
    },
    {
      "generalized_statement": "User displays regular interest in photography at intermediate level",
      "confidence_score": 0.78,
      "domain_detected": "photography",
      "evidence_chain": ["beh_023", "beh_024", ...]
    }
  ],
  "total_behaviors_analyzed": 33,
  "num_clusters": 3,
  "metadata": {
    "processing_time_ms": 1250.45,
    "quality_metrics": {
      "silhouette_score": 0.65,
      "noise_ratio": 0.0,
      "num_clusters": 3
    }
  }
}
```

## 🎉 You're Ready!

The API is now fully functional. Next steps:

1. Test with different users
2. Adjust clustering parameters
3. Explore API documentation
4. Integrate with your application
