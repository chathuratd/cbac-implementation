# CBAC System Testing Guide

## Test Data Overview

You have test data for a user with Kubernetes expertise progression:
- **User ID**: `user_2_1765824099`
- **Domain**: Kubernetes
- **Expertise Levels**: Novice → Intermediate → Advanced
- **Total Behaviors**: ~50 behaviors
- **Total Prompts**: ~50 prompts

Files:
- `test_data/behaviors_user_2_1765824099.json` - User behavior patterns
- `test_data/prompts_user_2_1765824099.json` - User prompt history

---

## Quick Start: Complete End-to-End Test

### Option 1: Automated Full Test (Recommended)

```powershell
cd scripts
python run_full_test.py
```

This script will:
1. ✅ Check Docker services (Qdrant, MongoDB)
2. 📦 Load test data into databases
3. 🚀 Guide you to start the API
4. 🧪 Run comprehensive tests
5. 💾 Save analysis results

---

### Option 2: Manual Step-by-Step

#### Step 1: Start Docker Services

```powershell
# From project root
docker-compose up -d
```

Verify services:
```powershell
# Check Qdrant
curl http://localhost:6333

# Check MongoDB
docker ps | Select-String mongodb
```

#### Step 2: Load Test Data

```powershell
cd scripts\data_setup

# Load prompts into MongoDB
python mongo_db_save.py

# Load behaviors into Qdrant (takes 1-2 minutes for embeddings)
python vector_db_save.py
```

Expected output:
- MongoDB: `✅ Inserted 50 prompts into MongoDB!`
- Qdrant: `✅ Done! 50 behaviors saved to Qdrant.`

#### Step 3: Start API Server

Open a **new terminal**:

```powershell
cd cbac_api
python main.py
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Step 4: Run Tests

In another terminal:

```powershell
cd tests\api
python test_api.py
```

Or test individual endpoints:

```powershell
# Health check
curl http://localhost:8000/health

# User summary
curl http://localhost:8000/analysis/user_2_1765824099/summary

# Full analysis
curl -X POST http://localhost:8000/analysis `
  -H "Content-Type: application/json" `
  -d '{\"user_id\": \"user_2_1765824099\", \"min_cluster_size\": 3, \"include_prompts\": true}'
```

---

## What to Expect

### 1. User Summary Response
```json
{
  "user_id": "user_2_1765824099",
  "total_behaviors": 50,
  "domain": "kubernetes",
  "expertise_level": "advanced",
  "avg_credibility": 0.82
}
```

### 2. Full Analysis Response
```json
{
  "analysis_id": "analysis_...",
  "user_id": "user_2_1765824099",
  "total_behaviors": 50,
  "core_patterns": [
    {
      "pattern_id": "pattern_1",
      "pattern_label": "Kubernetes Troubleshooting Expert",
      "behavior_count": 12,
      "avg_credibility": 0.89,
      "behaviors": [...]
    }
  ]
}
```

Results are saved to: `test_data/analysis_results/user_2_1765824099_test_result.json`

---

## Expected Test Results

### Behavior Clustering
The system should identify distinct behavior patterns:
1. **Troubleshooting patterns** - Pod debugging, log analysis
2. **Resource management** - Cluster optimization, autoscaling
3. **Security patterns** - Network policies, secrets management
4. **Infrastructure automation** - CI/CD integration, cluster upgrades

### Expertise Progression
The analysis should show progression from:
- **Novice**: Basic troubleshooting, simple configurations
- **Intermediate**: Advanced networking, multi-tenant setups
- **Advanced**: Performance optimization, custom architectures

---

## Troubleshooting

### Issue: MongoDB connection error
```
pymongo.errors.ServerSelectionTimeoutError
```
**Fix**: Ensure MongoDB is running
```powershell
docker-compose up -d mongodb
```

### Issue: Qdrant connection error
```
requests.exceptions.ConnectionError
```
**Fix**: Ensure Qdrant is running
```powershell
docker-compose up -d qdrant
```

### Issue: No behaviors found
**Fix**: Re-run data loading scripts
```powershell
cd scripts\data_setup
python vector_db_save.py
```

### Issue: API not starting
**Check**:
1. Port 8000 is not in use
2. Dependencies installed: `pip install -r requirements.txt`
3. Python environment is activated

---

## Viewing Results

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Database Inspection

**MongoDB** (via MongoDB Compass or CLI):
```javascript
// Connect to: mongodb://admin:admin123@localhost:27017
use cbac_system
db.prompts.countDocuments({"user_id": "user_2_1765824099"})
```

**Qdrant** (via UI or API):
- UI: http://localhost:6333/dashboard
- API: http://localhost:6333/collections/user_behaviors

---

## Clean Up

### Clear test data
```powershell
# MongoDB
mongosh "mongodb://admin:admin123@localhost:27017/cbac_system" --eval 'db.prompts.deleteMany({"user_id": "user_2_1765824099"})'

# Qdrant - will be cleared automatically on next data load
```

### Stop services
```powershell
docker-compose down
```

---

## Next Steps

After successful testing:
1. ✅ Review analysis results in `test_data/analysis_results/`
2. 📊 Check clustering quality and core patterns
3. 🔍 Validate behavior-prompt relationships
4. 📈 Test with different `min_cluster_size` parameters
5. 🎯 Experiment with additional test data

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python run_full_test.py` | Run complete end-to-end test |
| `python mongo_db_save.py` | Load prompts only |
| `python vector_db_save.py` | Load behaviors only |
| `python test_api.py` | Test API endpoints |
| `docker-compose up -d` | Start all services |
| `docker-compose down` | Stop all services |

---

**Need Help?** Check the main documentation:
- `docs/QUICKSTART.md` - General setup guide
- `docs/API_SPECIFICATION.md` - API reference
- `docs/IMPLEMENTATION_SUMMARY.md` - System overview
