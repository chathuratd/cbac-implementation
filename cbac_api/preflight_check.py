"""
Pre-flight check script - Verify system is ready before starting CBAC API
"""
import sys
import requests
from pymongo import MongoClient
from qdrant_client import QdrantClient

def check_qdrant():
    """Check Qdrant connection and data"""
    print("\n🔍 Checking Qdrant...")
    try:
        client = QdrantClient(url="http://localhost:6333")
        collections = client.get_collections()
        
        # Check if user_behaviors collection exists
        collection_names = [c.name for c in collections.collections]
        if "user_behaviors" not in collection_names:
            print("   ❌ Collection 'user_behaviors' not found")
            print("   → Run: python vector_db_save.py")
            return False
        
        # Check collection has data
        info = client.get_collection("user_behaviors")
        if info.points_count == 0:
            print("   ❌ Collection 'user_behaviors' is empty")
            print("   → Run: python vector_db_save.py")
            return False
        
        print(f"   ✅ Qdrant OK - {info.points_count} behaviors loaded")
        return True
        
    except Exception as e:
        print(f"   ❌ Qdrant connection failed: {e}")
        print("   → Ensure Qdrant is running on localhost:6333")
        return False

def check_mongodb():
    """Check MongoDB connection and data"""
    print("\n🔍 Checking MongoDB...")
    try:
        client = MongoClient("mongodb://admin:admin123@localhost:27017/")
        client.server_info()  # Test connection
        
        db = client["cbac_system"]
        prompts_collection = db["prompts"]
        
        # Check collection exists and has data
        count = prompts_collection.count_documents({})
        if count == 0:
            print("   ❌ Prompts collection is empty")
            print("   → Run: python mongo_db_save.py")
            return False
        
        print(f"   ✅ MongoDB OK - {count} prompts loaded")
        return True
        
    except Exception as e:
        print(f"   ❌ MongoDB connection failed: {e}")
        print("   → Ensure MongoDB is running on localhost:27017")
        print("   → Check credentials: admin/admin123")
        return False

def check_python_packages():
    """Check required Python packages"""
    print("\n🔍 Checking Python packages...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "qdrant_client",
        "pymongo",
        "sentence_transformers",
        "sklearn",
        "numpy"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"   ❌ Missing packages: {', '.join(missing)}")
        print("   → Run: pip install -r requirements.txt")
        return False
    
    print("   ✅ All required packages installed")
    return True

def check_data_files():
    """Check if source data files exist"""
    print("\n🔍 Checking data files...")
    
    import os
    required_files = [
        "../behaviors_db.json",
        "../prompts_db.json",
        "../users_metadata.json"
    ]
    
    missing = []
    for filepath in required_files:
        if not os.path.exists(filepath):
            missing.append(filepath)
    
    if missing:
        print(f"   ❌ Missing files: {', '.join(missing)}")
        return False
    
    print("   ✅ All data files present")
    return True

def main():
    """Run all pre-flight checks"""
    print("=" * 60)
    print("🚀 CBAC API - Pre-Flight Check")
    print("=" * 60)
    
    checks = {
        "Python Packages": check_python_packages(),
        "Data Files": check_data_files(),
        "Qdrant": check_qdrant(),
        "MongoDB": check_mongodb()
    }
    
    print("\n" + "=" * 60)
    print("📊 Check Results")
    print("=" * 60)
    
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    all_passed = all(checks.values())
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to start the API.")
        print("\n🚀 Start the API with:")
        print("   python main.py")
        print("\n📚 Or read QUICKSTART.md for more details")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
