# CBAC System Testing Checklist

## Pre-Test Setup ✓

### 1. Docker Services
- [ ] Docker Desktop is running
- [ ] Run: `docker-compose up -d`
- [ ] Verify Qdrant: `curl http://localhost:6333` (should return JSON)
- [ ] Verify MongoDB: `docker ps` (should show mongodb container)

### 2. Python Environment
- [ ] Python 3.8+ installed
- [ ] Dependencies installed in cbac_api: `pip install -r cbac_api/requirements.txt`
- [ ] Dependencies installed for scripts: `pip install pymongo qdrant-client sentence-transformers`

---

## Testing Workflow ✓

### Quick Test (5 minutes)
```powershell
# Start services
docker-compose up -d

# Run automated test
cd scripts
python run_full_test.py
```

### Manual Test (10 minutes)

#### Phase 1: Data Loading
```powershell
cd scripts\data_setup

# Load MongoDB data (~5 seconds)
python mongo_db_save.py
# Expected: ✅ Inserted 50 prompts into MongoDB!

# Load Qdrant data (~1-2 minutes)
python vector_db_save.py
# Expected: ✅ Done! 50 behaviors saved to Qdrant.
```

**Verification Points:**
- [ ] MongoDB shows 50 prompts for user_2_1765824099
- [ ] Qdrant shows 50 behaviors in collection

#### Phase 2: API Testing
```powershell
# Terminal 1: Start API
cd cbac_api
python main.py
# Wait for: "Uvicorn running on http://0.0.0.0:8000"

# Terminal 2: Run tests
cd tests\api
python test_api.py
```

**Verification Points:**
- [ ] Health check passes (200 OK)
- [ ] Metrics show both databases connected
- [ ] User summary returns data
- [ ] Full analysis completes successfully
- [ ] Results saved to test_data/analysis_results/

#### Phase 3: Result Validation
```powershell
# Check results file
cat test_data\analysis_results\user_2_1765824099_test_result.json
```

**Expected Results:**
- [ ] analysis_id generated
- [ ] total_behaviors = 50
- [ ] core_patterns array contains 3-8 clusters
- [ ] Each pattern has:
  - pattern_id
  - pattern_label (meaningful description)
  - behavior_count
  - avg_credibility
  - behaviors array
  - related_prompts (if include_prompts=true)

---

## Validation Criteria ✓

### Data Quality
- [x] Test data files exist in test_data/
- [ ] All behaviors have required fields
- [ ] All prompts have required fields
- [ ] user_id matches across both files

### System Functionality
- [ ] Qdrant collection created successfully
- [ ] MongoDB database and collection created
- [ ] Embeddings generated correctly
- [ ] Vector search returns relevant results

### API Endpoints
- [ ] GET /health returns status: "healthy"
- [ ] GET /health/metrics shows both DBs connected
- [ ] GET /analysis/{user_id}/summary returns user data
- [ ] POST /analysis completes without errors
- [ ] Response includes all required fields

### Analysis Quality
- [ ] Clusters are semantically meaningful
- [ ] Pattern labels make sense for Kubernetes domain
- [ ] Behaviors grouped logically
- [ ] Credibility scores are reasonable (0.7-0.95)
- [ ] Expertise progression visible (novice → advanced)

---

## Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| Docker not running | Connection refused | Start Docker Desktop |
| Port conflict | Address already in use | Stop conflicting service or change port |
| MongoDB auth error | Authentication failed | Check credentials in docker-compose.yml |
| Qdrant timeout | Request timeout | Wait for Qdrant to fully start (~10s) |
| Import error | ModuleNotFoundError | Run `pip install -r requirements.txt` |
| No data found | Empty results | Re-run data loading scripts |
| Slow embeddings | Long wait time | Normal - embeddings take 1-2 minutes |

---

## Quick Commands Reference

```powershell
# Start everything
docker-compose up -d

# Check service health
curl http://localhost:6333
curl http://localhost:27017

# Load data
cd scripts\data_setup
python mongo_db_save.py
python vector_db_save.py

# Start API
cd cbac_api
python main.py

# Run tests
cd tests\api
python test_api.py

# Full automated test
cd scripts
python run_full_test.py

# Stop everything
docker-compose down
```

---

## Success Criteria ✅

Your test is successful if:
1. ✅ All Docker services start without errors
2. ✅ Data loads into both databases
3. ✅ API starts and health check passes
4. ✅ Analysis completes and returns results
5. ✅ Core patterns are identified correctly
6. ✅ Results file is saved successfully

---

## Next Steps After Testing

1. **Analyze Results**: Review the generated core patterns
2. **Experiment**: Try different min_cluster_size values (2, 3, 5)
3. **Validate**: Check if clusters match expected Kubernetes topics
4. **Document**: Note any unexpected behaviors or patterns
5. **Iterate**: Add more test data if needed

---

**Status**: Ready to test! Follow the Quick Test section above.
