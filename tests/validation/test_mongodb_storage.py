"""
Quick Test: MongoDB Analysis Storage
Tests the new MongoDB-based analysis storage system
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from cbac_api.app.services.analysis_store import AnalysisStore
from datetime import datetime
import json


def test_mongodb_storage():
    """Test MongoDB analysis storage functionality"""
    
    print("="*60)
    print("MongoDB Analysis Storage - Quick Test")
    print("="*60)
    
    # Initialize store
    print("\n1. Initializing AnalysisStore...")
    try:
        store = AnalysisStore()
        print("✅ AnalysisStore initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Test connection
    print("\n2. Testing MongoDB connection...")
    try:
        connected = store.check_connection()
        if connected:
            print("✅ MongoDB connected")
        else:
            print("❌ MongoDB not connected")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    # Test save
    print("\n3. Testing save_analysis()...")
    test_user_id = "test_user_mongodb"
    test_analysis = {
        "core_behaviors": [
            {
                "core_behavior_id": "test_cb_001",
                "generalized_statement": "Test behavior",
                "confidence_score": 0.85
            }
        ],
        "total_behaviors_analyzed": 10,
        "num_clusters": 2,
        "metadata": {"test": True}
    }
    
    try:
        analysis_id = store.save_analysis(test_user_id, test_analysis)
        print(f"✅ Analysis saved with ID: {analysis_id}")
    except Exception as e:
        print(f"❌ Save failed: {e}")
        return False
    
    # Test get by ID
    print("\n4. Testing get_analysis_by_id()...")
    try:
        retrieved = store.get_analysis_by_id(analysis_id)
        if retrieved and retrieved["analysis_id"] == analysis_id:
            print(f"✅ Analysis retrieved successfully")
        else:
            print(f"❌ Failed to retrieve analysis")
            return False
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        return False
    
    # Test get latest
    print("\n5. Testing load_previous_analysis()...")
    try:
        latest = store.load_previous_analysis(test_user_id)
        if latest and latest["analysis_id"] == analysis_id:
            print(f"✅ Latest analysis retrieved")
        else:
            print(f"❌ Failed to get latest analysis")
            return False
    except Exception as e:
        print(f"❌ Load failed: {e}")
        return False
    
    # Test list analyses
    print("\n6. Testing list_user_analyses()...")
    try:
        analyses = store.list_user_analyses(test_user_id, limit=10)
        if len(analyses) > 0:
            print(f"✅ Found {len(analyses)} analyses")
            print(f"   First: {analyses[0]['analysis_id']}")
        else:
            print(f"❌ No analyses found")
            return False
    except Exception as e:
        print(f"❌ List failed: {e}")
        return False
    
    # Test stats
    print("\n7. Testing get_analysis_stats()...")
    try:
        stats = store.get_analysis_stats(test_user_id)
        print(f"✅ Stats retrieved:")
        print(f"   Total analyses: {stats['total_analyses']}")
        print(f"   Avg core behaviors: {stats['avg_core_behaviors']}")
    except Exception as e:
        print(f"❌ Stats failed: {e}")
        return False
    
    # Test delete
    print("\n8. Testing delete_analysis()...")
    try:
        deleted = store.delete_analysis(analysis_id)
        if deleted:
            print(f"✅ Analysis deleted")
        else:
            print(f"❌ Failed to delete analysis")
            return False
    except Exception as e:
        print(f"❌ Delete failed: {e}")
        return False
    
    # Verify deletion
    print("\n9. Verifying deletion...")
    try:
        retrieved = store.get_analysis_by_id(analysis_id)
        if retrieved is None:
            print(f"✅ Analysis confirmed deleted")
        else:
            print(f"❌ Analysis still exists!")
            return False
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    return True


if __name__ == "__main__":
    try:
        success = test_mongodb_storage()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
