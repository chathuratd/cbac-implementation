"""
Check MongoDB collections and contents to understand data structure.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
from app.config.settings import settings
import json


def main():
    print("\n" + "="*80)
    print("MONGODB DATA INSPECTION")
    print("="*80 + "\n")
    
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    
    # List all collections
    print(f"Database: {settings.MONGODB_DATABASE}")
    print(f"\nCollections:")
    collections = db.list_collection_names()
    for coll in collections:
        count = db[coll].count_documents({})
        print(f"  - {coll}: {count} documents")
    
    # Check behaviors collection specifically
    print(f"\n" + "="*80)
    print("BEHAVIORS COLLECTION INSPECTION")
    print("="*80 + "\n")
    
    if "behaviors" in collections:
        behaviors_coll = db["behaviors"]
        count = behaviors_coll.count_documents({})
        print(f"Total behaviors: {count}")
        
        if count > 0:
            # Show sample document
            sample = behaviors_coll.find_one()
            print(f"\nSample behavior document:")
            sample.pop("_id", None)
            print(json.dumps(sample, indent=2, default=str)[:500] + "...")
            
            # Check for behavior_text field
            has_text = behaviors_coll.count_documents({"behavior_text": {"$exists": True}})
            print(f"\nBehaviors with 'behavior_text' field: {has_text}/{count}")
        else:
            print("❌ Behaviors collection is EMPTY!")
    else:
        print("❌ 'behaviors' collection does NOT EXIST!")
        print("\nThis is why LLM generation fails - no behavior texts available.")
        print("\nPossible solutions:")
        print("1. Check if data was loaded to a different collection")
        print("2. Run data setup scripts to populate behaviors collection")
        print("3. Check test_data/ directory for sample data")
    
    print(f"\n" + "="*80)
    print("PROMPTS COLLECTION INSPECTION")
    print("="*80 + "\n")
    
    if "prompts" in collections:
        prompts_coll = db["prompts"]
        count = prompts_coll.count_documents({})
        print(f"Total prompts: {count}")
        
        if count > 0:
            # Show sample document
            sample = prompts_coll.find_one()
            print(f"\nSample prompt document:")
            sample.pop("_id", None)
            print(json.dumps(sample, indent=2, default=str)[:500] + "...")
    else:
        print("❌ 'prompts' collection does NOT EXIST!")
    
    client.close()


if __name__ == "__main__":
    main()
