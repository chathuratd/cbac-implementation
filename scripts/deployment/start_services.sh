#!/bin/bash

# CBAC System - Start All Services
echo "🚀 Starting CBAC System..."
echo ""

# Start Docker containers
echo "📦 Starting Docker containers..."
docker-compose up -d

# Wait for containers to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check Qdrant
echo ""
echo "🔍 Checking Qdrant..."
if curl -s http://localhost:6333 > /dev/null; then
    echo "✅ Qdrant is running on http://localhost:6333"
else
    echo "❌ Qdrant is not responding"
fi

# Check MongoDB
echo ""
echo "🔍 Checking MongoDB..."
if docker exec mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --eval "db.version()" --quiet > /dev/null 2>&1; then
    echo "✅ MongoDB is running on localhost:27017"
else
    echo "❌ MongoDB is not responding"
fi

echo ""
echo "✨ All services started!"
echo ""
echo "Next steps:"
echo "1. Load data: python vector_db_save.py && python mongo_db_save.py"
echo "2. Run preflight: cd cbac_api && python preflight_check.py"
echo "3. Start API: python main.py"
