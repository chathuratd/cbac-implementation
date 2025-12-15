# Docker Commands for CBAC System

## 🚀 Quick Start (Recommended)

### Start all containers with data persistence:
```bash
docker-compose up -d
```

### Check status:
```bash
docker-compose ps
```

### Stop containers:
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes all data):
```bash
docker-compose down -v
```

---

## 📦 Individual Docker Commands (Alternative)

### Qdrant (Vector Database)

**Start with persistent storage:**
```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v qdrant_storage:/qdrant/storage qdrant/qdrant:latest
```

**Check if running:**
```bash
curl http://localhost:6333
```

**Stop:**
```bash
docker stop qdrant
```

**Remove (⚠️ keeps volume):**
```bash
docker rm qdrant
```

**Remove with data (⚠️ deletes volume):**
```bash
docker rm qdrant
docker volume rm qdrant_storage
```

---

### MongoDB (Document Database)

**Start with persistent storage:**
```bash
docker run -d --name mongodb -p 27017:27017 -v mongodb_data:/data/db -v mongodb_config:/data/configdb -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=admin123 mongo:latest
```

**Check if running:**
```bash
docker exec -it mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --eval "db.version()"
```

**Stop:**
```bash
docker stop mongodb
```

**Remove (⚠️ keeps volume):**
```bash
docker rm mongodb
```

**Remove with data (⚠️ deletes volumes):**
```bash
docker rm mongodb
docker volume rm mongodb_data mongodb_config
```

---

## 🔄 Common Operations

### View logs:
```bash
# Docker Compose
docker-compose logs -f

# Individual
docker logs -f qdrant
docker logs -f mongodb
```

### Restart containers:
```bash
# Docker Compose
docker-compose restart

# Individual
docker restart qdrant
docker restart mongodb
```

### Check volumes:
```bash
docker volume ls
```

### Backup volumes:
```bash
# Qdrant backup
docker run --rm -v qdrant_storage:/data -v ${PWD}:/backup ubuntu tar czf /backup/qdrant_backup.tar.gz /data

# MongoDB backup
docker exec mongodb mongodump --username admin --password admin123 --authenticationDatabase admin --out /tmp/backup
docker cp mongodb:/tmp/backup ./mongodb_backup
```

---

## 📊 Data Persistence

**Volumes created:**
- `qdrant_storage` - Qdrant vector database
- `mongodb_data` - MongoDB database files
- `mongodb_config` - MongoDB configuration

**Data persists across:**
- ✅ Container restart (`docker restart`)
- ✅ Container stop/start (`docker stop` → `docker start`)
- ✅ Container removal (`docker rm` - volume stays)
- ❌ Volume removal (`docker volume rm` - data deleted)

---

## 🧪 Test Connections

### Qdrant:
```bash
curl http://localhost:6333/collections
```

### MongoDB:
```bash
docker exec -it mongodb mongosh -u admin -p admin123 --authenticationDatabase admin
```

---

## 📝 Notes

- **Credentials:** 
  - MongoDB: `admin` / `admin123`
  - Qdrant: No authentication by default

- **Ports:**
  - Qdrant: 6333 (HTTP), 6334 (gRPC)
  - MongoDB: 27017

- **Data Location:**
  - Docker volumes are stored in Docker's data directory
  - Use `docker volume inspect <volume_name>` to see exact path
