"""
Load behaviors from JSON test data files into MongoDB.
This enables LLM generation to access behavior_text from MongoDB.
"""

import sys
import os
import json
import glob

# Add cbac_api to path
cbac_api_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cbac_api")
sys.path.insert(0, cbac_api_path)

from pymongo import MongoClient
from app.config.settings import settings


def load_behaviors_to_mongodb():
    """Load all behavior JSON files into MongoDB"""
    print("\n" + "="*80)
    print("LOADING BEHAVIORS TO MONGODB")
    print("="*80 + "\n")
    
    # Connect to MongoDB
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    behaviors_coll = db[settings.MONGODB_COLLECTION_BEHAVIORS]
    
    # Find all behavior JSON files in test_data directory
    test_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "test_data")
    behavior_files = glob.glob(os.path.join(test_data_dir, "behaviors_*.json"))
    
    print(f"Found {len(behavior_files)} behavior files:\n")
    for f in behavior_files:
        print(f"  - {os.path.basename(f)}")
    
    total_loaded = 0
    
    for file_path in behavior_files:
        filename = os.path.basename(file_path)
        print(f"\nProcessing {filename}...")
        
        try:
            with open(file_path, 'r') as f:
                behaviors = json.load(f)
            
            print(f"  Found {len(behaviors)} behaviors")
            
            if behaviors:
                # Insert or update behaviors
                for behavior in behaviors:
                    behavior_id = behavior.get('behavior_id')
                    if behavior_id:
                        # Upsert: update if exists, insert if not
                        behaviors_coll.update_one(
                            {"behavior_id": behavior_id},
                            {"$set": behavior},
                            upsert=True
                        )
                
                total_loaded += len(behaviors)
                print(f"  ✅ Loaded {len(behaviors)} behaviors")
            else:
                print(f"  ⚠️  No behaviors in file")
                
        except Exception as e:
            print(f"  ❌ Error loading {filename}: {e}")
    
    # Final stats
    print(f"\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")
    
    total_in_db = behaviors_coll.count_documents({})
    print(f"Total behaviors loaded: {total_loaded}")
    print(f"Total behaviors in MongoDB: {total_in_db}")
    
    # Show sample
    sample = behaviors_coll.find_one()
    if sample:
        sample.pop("_id", None)
        print(f"\nSample behavior:")
        print(f"  ID: {sample.get('behavior_id')}")
        print(f"  Text: {sample.get('behavior_text', 'N/A')}")
        print(f"  User: {sample.get('user_id')}")
        print(f"  Domain: {sample.get('domain')}")
    
    # Check for behavior_text field
    has_text = behaviors_coll.count_documents({"behavior_text": {"$exists": True}})
    print(f"\nBehaviors with 'behavior_text': {has_text}/{total_in_db}")
    
    if has_text == total_in_db and total_in_db > 0:
        print("\n🎉 SUCCESS! All behaviors have behavior_text field.")
        print("LLM generation should now work correctly.")
    else:
        print(f"\n⚠️  WARNING: Only {has_text} out of {total_in_db} have behavior_text")
    
    client.close()


if __name__ == "__main__":
    load_behaviors_to_mongodb()
