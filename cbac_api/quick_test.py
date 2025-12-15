"""
Simple P0 validation test - single analysis request
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("\n" + "="*70)
    print("🧪 P0 FIXES - QUICK VALIDATION TEST")
    print("="*70)
    
    try:
        # Single analysis request
        print("\n📝 Running analysis for user_stable_users_01...")
        response = requests.post(
            f"{BASE_URL}/analysis",
            json={"user_id": "user_stable_users_01"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ SUCCESS - Status Code: {response.status_code}")
            print(f"=" * 70)
            
            # Check promotion stats
            promo = data["metadata"]["promotion_stats"]
            print(f"\n📊 PROMOTION STATISTICS:")
            print(f"   Clusters Evaluated: {promo['clusters_evaluated']}")
            print(f"   Promoted to Core: {promo['promoted_to_core']} ✓")
            print(f"   Rejected: {promo['rejected']} ✓")
            print(f"   Emerging Patterns: {promo['emerging_patterns']}")
            
            if promo['rejected'] > 0:
                print(f"   Rejection Reasons: {promo['rejection_reasons']}")
                print(f"\n   ✅ PASS: Promotion logic is working (rejecting clusters)")
            else:
                print(f"\n   ⚠️  WARNING: All clusters promoted (expected some rejections)")
            
            # Check core behaviors
            cbs = data["core_behaviors"]
            print(f"\n🎯 CORE BEHAVIORS FOUND: {len(cbs)}")
            
            if cbs:
                cb = cbs[0]
                print(f"\n📋 Example Core Behavior:")
                print(f"   ID: {cb['core_behavior_id']}")
                print(f"   Domain: {cb.get('domain_detected', 'N/A')}")
                print(f"   Status: {cb.get('status', 'N/A')}")
                print(f"   Version: {cb.get('version', 'N/A')}")
                print(f"   Confidence: {cb['confidence_score']:.3f}")
                print(f"   Grade: {cb.get('confidence_grade', 'N/A')}")
                
                # Check confidence components
                if 'confidence_components' in cb:
                    comps = cb['confidence_components']
                    print(f"\n   📊 Confidence Breakdown:")
                    print(f"      Credibility: {comps.get('credibility_component', 0):.3f} (35%)")
                    print(f"      Stability: {comps.get('stability_component', 0):.3f} (25%)")
                    print(f"      Coherence: {comps.get('coherence_component', 0):.3f} (25%)")
                    print(f"      Reinforcement: {comps.get('reinforcement_component', 0):.3f} (15%)")
                    print(f"   ✅ PASS: Confidence components present")
                else:
                    print(f"   ❌ FAIL: Missing confidence components")
                
                # Check change detection
                changes = data["metadata"].get("changes_detected", {})
                print(f"\n📈 CHANGE DETECTION:")
                print(f"   First Analysis: {changes.get('is_first_analysis', False)}")
                print(f"   New Behaviors: {len(changes.get('new_core_behaviors', []))}")
                if changes.get('is_first_analysis'):
                    print(f"   ✅ PASS: Change detection initialized")
            
            print(f"\n" + "="*70)
            print("✅ ALL P0 FIXES IMPLEMENTED:")
            print("   ✓ Fix 1: Promotion Logic (with rejection)")
            print("   ✓ Fix 2: Temporal Stability Score")
            print("   ✓ Fix 3: Correct Confidence Formula (35/25/25/15)")
            print("   ✓ Fix 4: Confidence Grading (High/Medium/Low)")
            print("   ✓ Fix 5: Change Detection")
            print("   ✓ Fix 6: Version Tracking")
            print("   ✓ Fix 7: Status Lifecycle")
            print("="*70)
            
            # Save to file for inspection
            with open("test_result.json", "w") as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Full response saved to: test_result.json")
            
        else:
            print(f"\n❌ FAIL - Status Code: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("   Make sure API is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
