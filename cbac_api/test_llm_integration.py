"""
Test script to verify LLM integration for generalized statement generation.

This script:
1. Tests LLM service connection
2. Tests cache service functionality
3. Runs a sample analysis to verify LLM generates meaningful statements
"""

import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm_service import LLMService
from app.services.cache_service import CacheService
from app.config.settings import settings


def test_llm_connection():
    """Test LLM service connection"""
    print("\n" + "="*60)
    print("TEST 1: LLM Service Connection")
    print("="*60)
    
    llm_service = LLMService()
    
    if llm_service.client is None:
        print("❌ FAILED: LLM client not initialized")
        print(f"   API Key: {'✓ Set' if settings.OPENAI_API_KEY else '✗ Missing'}")
        print(f"   API Base: {settings.OPENAI_API_BASE}")
        return False
    
    print("✅ LLM client initialized successfully")
    print(f"   API Base: {settings.OPENAI_API_BASE}")
    print(f"   LLM Generation: {'Enabled' if settings.ENABLE_LLM_GENERATION else 'Disabled'}")
    
    # Test connection
    print("\nTesting connection...")
    is_connected = llm_service.test_connection()
    
    if is_connected:
        print("✅ LLM connection test PASSED")
    else:
        print("❌ LLM connection test FAILED")
    
    return is_connected


def test_cache_service():
    """Test cache service functionality"""
    print("\n" + "="*60)
    print("TEST 2: Cache Service")
    print("="*60)
    
    cache_service = CacheService()
    
    # Test basic operations
    test_key = "test_key_123"
    test_value = "User frequently requests scrambled eggs recipes"
    
    # Set
    cache_service.set(test_key, test_value, ttl=60)
    print(f"✅ Set cache: {test_key[:20]}...")
    
    # Get
    retrieved = cache_service.get(test_key)
    if retrieved == test_value:
        print(f"✅ Get cache: Value matches")
    else:
        print(f"❌ Get cache: Value mismatch")
        return False
    
    # Create cache key from texts
    texts = [
        "User requests a simple recipe for scrambled eggs.",
        "User requests a simple recipe for scrambled eggs.",
        "User asks about scrambled eggs"
    ]
    cache_key = cache_service.create_cache_key(texts)
    print(f"✅ Generated cache key: {cache_key}")
    
    # Stats
    stats = cache_service.get_stats()
    print(f"✅ Cache stats: {stats}")
    
    # Cleanup
    cache_service.delete(test_key)
    print(f"✅ Deleted test key")
    
    return True


def test_statement_generation():
    """Test LLM statement generation with sample behaviors"""
    print("\n" + "="*60)
    print("TEST 3: LLM Statement Generation")
    print("="*60)
    
    llm_service = LLMService()
    
    # Sample behavior texts (similar to real data)
    test_cases = [
        {
            "name": "Specific - Scrambled Eggs",
            "domain": "cooking",
            "texts": [
                "User requests a simple recipe for scrambled eggs.",
                "User requests a simple recipe for scrambled eggs.",
                "User asks about scrambled eggs preparation",
                "User wants to know how to make scrambled eggs",
                "User seeks scrambled eggs cooking instructions"
            ]
        },
        {
            "name": "Varied - Cooking",
            "domain": "cooking",
            "texts": [
                "User asks about pasta carbonara recipe",
                "User wants quick breakfast ideas",
                "User requests baking tips for beginners",
                "User inquires about meal prep strategies"
            ]
        },
        {
            "name": "Technical - Programming",
            "domain": "programming",
            "texts": [
                "User asks how to implement a REST API in Python",
                "User wants to understand FastAPI routing",
                "User seeks guidance on API endpoint design",
                "User requests help with async functions"
            ]
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📝 Test Case: {test_case['name']}")
        print(f"   Domain: {test_case['domain']}")
        print(f"   Behaviors: {len(test_case['texts'])}")
        
        # Generate statement
        statement = llm_service.generate_statement(
            behavior_texts=test_case['texts'],
            domain=test_case['domain'],
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE
        )
        
        if statement:
            print(f"   ✅ Generated: \"{statement}\"")
            results.append({
                "name": test_case['name'],
                "statement": statement,
                "success": True
            })
        else:
            print(f"   ❌ FAILED: No statement generated")
            results.append({
                "name": test_case['name'],
                "statement": None,
                "success": False
            })
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r['success'])
    print(f"Successful: {successful}/{len(results)}")
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['name']}")
        if result['statement']:
            print(f"   → {result['statement']}")
    
    return successful == len(results)


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LLM INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Settings:")
    print(f"  ENABLE_LLM_GENERATION: {settings.ENABLE_LLM_GENERATION}")
    print(f"  ENABLE_STATEMENT_CACHE: {settings.ENABLE_STATEMENT_CACHE}")
    print(f"  LLM_MAX_TOKENS: {settings.LLM_MAX_TOKENS}")
    print(f"  LLM_TEMPERATURE: {settings.LLM_TEMPERATURE}")
    
    results = {
        "connection": False,
        "cache": False,
        "generation": False
    }
    
    # Test 1: Connection
    try:
        results["connection"] = test_llm_connection()
    except Exception as e:
        print(f"❌ Connection test error: {e}")
    
    # Test 2: Cache
    try:
        results["cache"] = test_cache_service()
    except Exception as e:
        print(f"❌ Cache test error: {e}")
    
    # Test 3: Generation (only if connection works)
    if results["connection"]:
        try:
            results["generation"] = test_statement_generation()
        except Exception as e:
            print(f"❌ Generation test error: {e}")
    else:
        print("\n⚠️  Skipping generation test (connection failed)")
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.upper()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests PASSED! LLM integration is working correctly.")
    else:
        print("\n⚠️  Some tests FAILED. Please check the output above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
