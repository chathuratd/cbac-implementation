"""
Migration Script: File-based Analysis Storage to MongoDB
Migrates existing analysis JSON files to MongoDB database
"""

import json
import os
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
import sys

# Add parent directory to path to import settings
sys.path.append(str(Path(__file__).parent.parent))

from cbac_api.app.config.settings import settings


def migrate_file_to_mongodb():
    """Migrate analysis results from JSON files to MongoDB"""
    
    # Connect to MongoDB
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    collection = db["analysis_results"]
    
    # Create indexes
    print("Creating indexes...")
    collection.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
    collection.create_index("analysis_id", unique=True)
    collection.create_index("timestamp", DESCENDING)
    print("✅ Indexes created")
    
    # Path to analysis results directory
    results_dir = Path("./analysis_results")
    
    if not results_dir.exists():
        print(f"❌ Directory {results_dir} not found")
        return
    
    # Find all JSON files (excluding _latest files to avoid duplicates)
    json_files = [f for f in results_dir.glob("*.json") if not f.stem.endswith("_latest")]
    
    if not json_files:
        print("No analysis files found to migrate")
        return
    
    print(f"\nFound {len(json_files)} analysis files to migrate")
    print("="*60)
    
    migrated = 0
    skipped = 0
    errors = 0
    
    for json_file in json_files:
        try:
            # Read JSON file
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Extract analysis_id from filename or data
            analysis_id = data.get("analysis_id")
            if not analysis_id:
                # Generate from filename
                analysis_id = json_file.stem
                data["analysis_id"] = analysis_id
            
            # Check if already exists
            existing = collection.find_one({"analysis_id": analysis_id})
            if existing:
                print(f"⏭️  Skipping {analysis_id} (already exists)")
                skipped += 1
                continue
            
            # Parse timestamp
            if "timestamp" not in data or not isinstance(data["timestamp"], datetime):
                # Try to parse from saved_at or analysis_id
                if "saved_at" in data:
                    try:
                        data["timestamp"] = datetime.fromisoformat(data["saved_at"])
                    except:
                        pass
                
                if "timestamp" not in data and "_" in analysis_id:
                    try:
                        ts = int(analysis_id.split("_")[-1])
                        data["timestamp"] = datetime.fromtimestamp(ts)
                    except:
                        data["timestamp"] = datetime.utcnow()
            
            # Ensure required fields
            if "user_id" not in data:
                # Extract from analysis_id
                parts = analysis_id.split("_")
                if len(parts) >= 2:
                    data["user_id"] = "_".join(parts[:-1])
                else:
                    print(f"⚠️  Warning: Cannot extract user_id from {analysis_id}")
                    data["user_id"] = "unknown"
            
            if "version" not in data:
                data["version"] = "1.0"
            
            # Insert into MongoDB
            collection.insert_one(data)
            print(f"✅ Migrated {analysis_id}")
            migrated += 1
            
        except Exception as e:
            print(f"❌ Error migrating {json_file.name}: {e}")
            errors += 1
    
    print("\n" + "="*60)
    print("Migration Summary:")
    print(f"  ✅ Migrated: {migrated}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Errors: {errors}")
    print(f"  📊 Total: {len(json_files)}")
    print("="*60)
    
    # Verify migration
    total_in_db = collection.count_documents({})
    print(f"\n✅ Total documents in MongoDB: {total_in_db}")
    
    # List users
    user_ids = collection.distinct("user_id")
    print(f"✅ Unique users: {len(user_ids)}")
    for user_id in user_ids:
        count = collection.count_documents({"user_id": user_id})
        print(f"   - {user_id}: {count} analyses")


if __name__ == "__main__":
    print("="*60)
    print("Analysis Storage Migration: Files → MongoDB")
    print("="*60)
    
    try:
        migrate_file_to_mongodb()
        print("\n✅ Migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
