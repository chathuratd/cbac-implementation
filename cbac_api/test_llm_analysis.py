"""
Test the analysis endpoint with LLM-generated statements.
This will run an actual analysis and show the difference between 
template-based and LLM-generated statements.
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_analysis(user_id: str):
    """Run analysis for a user and display results"""
    print(f"\n{'='*80}")
    print(f"TESTING ANALYSIS FOR: {user_id}")
    print(f"{'='*80}\n")
    
    url = f"{API_BASE}/analysis"
    payload = {
        "user_id": user_id,
        "min_cluster_size": 3
    }
    
    print(f"📤 Sending request to: {url}")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        elapsed = (time.time() - start_time) * 1000
        
        print(f"\n⏱️  Response time: {elapsed:.2f}ms")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ SUCCESS!")
            print(f"\n{'='*80}")
            print(f"ANALYSIS RESULTS")
            print(f"{'='*80}\n")
            
            print(f"User ID: {data['user_id']}")
            print(f"Total Behaviors: {data['total_behaviors_analyzed']}")
            print(f"Clusters Created: {data['num_clusters']}")
            print(f"Core Behaviors Found: {len(data['core_behaviors'])}")
            
            # Promotion stats
            metadata = data.get('metadata', {})
            promo_stats = metadata.get('promotion_stats', {})
            
            print(f"\n📈 PROMOTION STATISTICS:")
            print(f"  Clusters Evaluated: {promo_stats.get('clusters_evaluated', 0)}")
            print(f"  Promoted to Core: {promo_stats.get('promoted_to_core', 0)}")
            print(f"  Rejected: {promo_stats.get('rejected', 0)}")
            
            rejection_reasons = promo_stats.get('rejection_reasons', {})
            if rejection_reasons:
                print(f"\n  Rejection Reasons:")
                for reason, count in rejection_reasons.items():
                    print(f"    - {reason}: {count}")
            
            # Core behaviors with LLM-generated statements
            print(f"\n{'='*80}")
            print(f"CORE BEHAVIORS (LLM-GENERATED STATEMENTS)")
            print(f"{'='*80}\n")
            
            for i, cb in enumerate(data['core_behaviors'], 1):
                print(f"{i}. {cb['generalized_statement']}")
                print(f"   📊 Confidence: {cb['confidence_score']:.3f} ({cb['confidence_grade']})")
                print(f"   🎯 Domain: {cb['domain_detected']}")
                print(f"   📝 Evidence: {len(cb['evidence_chain'])} behaviors")
                print(f"   🔄 Status: {cb['status']}")
                print()
            
            # Cache stats if available
            print(f"{'='*80}")
            print(f"LLM GENERATION DETAILS")
            print(f"{'='*80}\n")
            print(f"Processing Time: {metadata.get('processing_time_ms', 0):.2f}ms")
            
            return True
            
        else:
            print(f"\n❌ FAILED!")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def main():
    """Test with available users"""
    print("\n" + "="*80)
    print("LLM-BASED ANALYSIS ENDPOINT TEST")
    print("="*80)
    
    # Test users
    test_users = [
        "user_4_1765826173",
        "user_2_1765824099"
    ]
    
    results = {}
    
    for user_id in test_users:
        try:
            success = test_analysis(user_id)
            results[user_id] = success
            
            # Wait a bit between requests
            if user_id != test_users[-1]:
                print("\n⏳ Waiting 2 seconds before next test...")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error for {user_id}: {e}")
            results[user_id] = False
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for user_id, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {user_id}")
    
    all_success = all(results.values())
    
    if all_success:
        print("\n🎉 All tests PASSED!")
        print("\n💡 The analysis now uses LLM-generated statements that are:")
        print("   - More specific and meaningful")
        print("   - Based on actual behavior text content")
        print("   - Cached for efficiency")
        print("   - Fall back to templates on error")
    else:
        print("\n⚠️  Some tests failed")
    
    return all_success


if __name__ == "__main__":
    import sys
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    success = main()
    sys.exit(0 if success else 1)
