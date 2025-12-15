"""
Diagnostic script to check why LLM generation might not be working.
Checks:
1. MongoDB connection and behavior text availability
2. LLM service initialization
3. Full generation flow with actual data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.document_store import DocumentStoreService
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from app.services.cache_service import CacheService
from app.config.settings import settings


def test_mongodb_behavior_texts():
    """Test if we can fetch behavior texts from MongoDB"""
    print("\n" + "="*80)
    print("TEST: MongoDB Behavior Text Retrieval")
    print("="*80 + "\n")
    
    doc_service = DocumentStoreService()
    vector_service = VectorStoreService()
    
    # Get behaviors from Qdrant first
    user_id = "user_4_1765826173"
    print(f"Fetching behaviors for {user_id} from Qdrant...")
    
    try:
        behaviors = vector_service.get_behaviors_by_user(user_id)
        print(f"✅ Found {len(behaviors)} behaviors in Qdrant")
        
        if behaviors:
            # Try to fetch full behavior data from MongoDB
            behavior_ids = [b.behavior_id for b in behaviors[:5]]  # Test with first 5
            print(f"\nTrying to fetch behavior texts from MongoDB for {len(behavior_ids)} behaviors...")
            
            full_behaviors = doc_service.get_behaviors_by_ids(behavior_ids)
            
            if full_behaviors:
                print(f"✅ Retrieved {len(full_behaviors)} full behaviors from MongoDB")
                
                # Check if they have behavior_text (dictionaries from MongoDB)
                has_text = [fb for fb in full_behaviors if fb.get('behavior_text')]
                print(f"✅ {len(has_text)} behaviors have behavior_text field")
                
                if has_text:
                    print(f"\nSample behavior texts:")
                    for i, fb in enumerate(has_text[:3], 1):
                        print(f"{i}. [{fb['behavior_id']}] {fb['behavior_text'][:80]}...")
                    return True
                else:
                    print("❌ No behaviors have behavior_text field!")
                    return False
            else:
                print("❌ Could not retrieve behaviors from MongoDB")
                return False
        else:
            print("❌ No behaviors found in Qdrant")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_generation_flow():
    """Test the complete LLM generation flow"""
    print("\n" + "="*80)
    print("TEST: Full LLM Generation Flow")
    print("="*80 + "\n")
    
    doc_service = DocumentStoreService()
    llm_service = LLMService()
    cache_service = CacheService()
    
    # Sample behavior IDs from user_4
    behavior_ids = [
        "beh_0a110f56",
        "beh_b06f43a7", 
        "beh_54f3996b",
        "beh_63ada8fe",
        "beh_d497bb7d"
    ]
    
    print(f"Testing with {len(behavior_ids)} behavior IDs...")
    
    try:
        # Step 1: Fetch texts from MongoDB
        print("\n1. Fetching behavior texts from MongoDB...")
        full_behaviors = doc_service.get_behaviors_by_ids(behavior_ids)
        
        if not full_behaviors:
            print("   ❌ No behaviors retrieved from MongoDB")
            return False
        
        print(f"   ✅ Retrieved {len(full_behaviors)} behaviors")
        
        # Extract texts (MongoDB returns dictionaries)
        behavior_texts = [fb.get('behavior_text', '') for fb in full_behaviors if fb.get('behavior_text')]
        
        if not behavior_texts:
            print("   ❌ No behavior_text fields found")
            return False
        
        print(f"   ✅ Found {len(behavior_texts)} behavior texts")
        print(f"\n   Sample texts:")
        for i, text in enumerate(behavior_texts[:3], 1):
            print(f"   {i}. {text[:70]}...")
        
        # Step 2: Create cache key
        print("\n2. Creating cache key...")
        cache_key = cache_service.create_cache_key(behavior_texts)
        print(f"   ✅ Cache key: {cache_key}")
        
        # Step 3: Generate with LLM
        print("\n3. Generating statement with LLM...")
        statement = llm_service.generate_statement(
            behavior_texts=behavior_texts,
            domain="cooking",
            max_tokens=100,
            temperature=0.3
        )
        
        if statement:
            print(f"   ✅ Generated statement:")
            print(f"   \"{statement}\"")
            
            # Step 4: Cache it
            print("\n4. Caching statement...")
            cache_service.set(cache_key, statement, ttl=settings.CACHE_TTL_SECONDS)
            print(f"   ✅ Cached successfully")
            
            # Verify cache
            cached = cache_service.get(cache_key)
            if cached == statement:
                print(f"   ✅ Cache verification passed")
            else:
                print(f"   ⚠️  Cache verification failed")
            
            return True
        else:
            print("   ❌ LLM generation returned None")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all diagnostics"""
    print("\n" + "="*80)
    print("LLM GENERATION DIAGNOSTIC")
    print("="*80)
    print(f"\nSettings:")
    print(f"  ENABLE_LLM_GENERATION: {settings.ENABLE_LLM_GENERATION}")
    print(f"  OPENAI_DEPLOYMENT_NAME: {settings.OPENAI_DEPLOYMENT_NAME}")
    print(f"  MONGODB_URL: {settings.MONGODB_URL[:50]}...")
    print(f"  MONGODB_DATABASE: {settings.MONGODB_DATABASE}")
    
    results = {
        "MongoDB Behavior Texts": False,
        "Full Generation Flow": False
    }
    
    try:
        results["MongoDB Behavior Texts"] = test_mongodb_behavior_texts()
    except Exception as e:
        print(f"❌ MongoDB test crashed: {e}")
    
    if results["MongoDB Behavior Texts"]:
        try:
            results["Full Generation Flow"] = test_full_generation_flow()
        except Exception as e:
            print(f"❌ Generation flow test crashed: {e}")
    else:
        print("\n⚠️  Skipping generation flow test (MongoDB test failed)")
    
    # Summary
    print("\n" + "="*80)
    print("DIAGNOSTIC RESULTS")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All diagnostics PASSED!")
        print("LLM generation should be working in the analysis endpoint.")
    else:
        print("\n⚠️  Some diagnostics FAILED!")
        print("This explains why LLM generation is not working in analysis.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
