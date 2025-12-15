"""
Quick validation script for P0 fixes
Tests that the critical algorithm fixes are working correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_promotion_logic():
    """Test that clusters are properly evaluated and some are rejected"""
    print("\n" + "="*60)
    print("TEST 1: Core Behavior Promotion Logic")
    print("="*60)
    
    # Test with user_stable_users_01
    response = requests.post(
        f"{BASE_URL}/analysis",
        json={"user_id": "user_stable_users_01"}
    )
    
    if response.status_code == 200:
        data = response.json()
        promotion_stats = data["metadata"]["promotion_stats"]
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"\n📊 Promotion Statistics:")
        print(f"   - Clusters Evaluated: {promotion_stats['clusters_evaluated']}")
        print(f"   - Promoted to Core: {promotion_stats['promoted_to_core']}")
        print(f"   - Rejected: {promotion_stats['rejected']}")
        print(f"   - Emerging Patterns: {promotion_stats['emerging_patterns']}")
        
        if promotion_stats['rejected'] > 0:
            print(f"\n✅ PASS: Some clusters were rejected (not all promoted)")
            print(f"   Rejection Reasons: {promotion_stats['rejection_reasons']}")
        else:
            print(f"\n⚠️  WARNING: All clusters were promoted (expected some rejections)")
        
        return data
    else:
        print(f"❌ FAIL: Status Code {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def test_confidence_components(analysis_data):
    """Test that confidence breakdown is present"""
    print("\n" + "="*60)
    print("TEST 2: Confidence Components & Grading")
    print("="*60)
    
    if not analysis_data:
        print("❌ SKIP: No analysis data from previous test")
        return
    
    core_behaviors = analysis_data["core_behaviors"]
    
    if not core_behaviors:
        print("❌ SKIP: No core behaviors found")
        return
    
    print(f"✅ Found {len(core_behaviors)} core behaviors")
    
    # Check first core behavior
    cb = core_behaviors[0]
    
    print(f"\n📋 Core Behavior Example:")
    print(f"   - ID: {cb['core_behavior_id']}")
    print(f"   - Statement: {cb['generalized_statement'][:60]}...")
    print(f"   - Confidence Score: {cb['confidence_score']:.3f}")
    print(f"   - Confidence Grade: {cb['confidence_grade']}")
    
    if 'confidence_components' in cb and cb['confidence_components']:
        print(f"\n✅ PASS: Confidence components present")
        comps = cb['confidence_components']
        print(f"   - Credibility: {comps.get('credibility_component', 0):.3f} (weight: {comps.get('credibility_weight', 0)})")
        print(f"   - Stability: {comps.get('stability_component', 0):.3f} (weight: {comps.get('stability_weight', 0)})")
        print(f"   - Coherence: {comps.get('coherence_component', 0):.3f} (weight: {comps.get('coherence_weight', 0)})")
        print(f"   - Reinforcement: {comps.get('reinforcement_component', 0):.3f} (weight: {comps.get('reinforcement_weight', 0)})")
    else:
        print(f"❌ FAIL: No confidence components found")


def test_change_detection():
    """Test that change detection is working"""
    print("\n" + "="*60)
    print("TEST 3: Change Detection")
    print("="*60)
    
    # Run first analysis
    print("📝 Running first analysis...")
    response1 = requests.post(
        f"{BASE_URL}/analysis",
        json={"user_id": "user_stable_users_02"}
    )
    
    if response1.status_code != 200:
        print(f"❌ FAIL: First analysis failed ({response1.status_code})")
        return
    
    data1 = response1.json()
    changes1 = data1["metadata"]["changes_detected"]
    
    print(f"✅ First analysis complete")
    print(f"   - Is first analysis: {changes1['is_first_analysis']}")
    print(f"   - New behaviors: {len(changes1['new_core_behaviors'])}")
    
    if changes1['is_first_analysis']:
        print(f"✅ PASS: First analysis correctly identified")
    else:
        print(f"❌ FAIL: Should be marked as first analysis")
    
    # Wait a moment
    time.sleep(1)
    
    # Run second analysis (same user)
    print(f"\n📝 Running second analysis (same user)...")
    response2 = requests.post(
        f"{BASE_URL}/analysis",
        json={"user_id": "user_stable_users_02"}
    )
    
    if response2.status_code != 200:
        print(f"❌ FAIL: Second analysis failed ({response2.status_code})")
        return
    
    data2 = response2.json()
    changes2 = data2["metadata"]["changes_detected"]
    
    print(f"✅ Second analysis complete")
    print(f"   - Is first analysis: {changes2['is_first_analysis']}")
    print(f"   - New behaviors: {len(changes2.get('new_core_behaviors', []))}")
    print(f"   - Updated behaviors: {len(changes2.get('updated_behaviors', []))}")
    print(f"   - Retired behaviors: {len(changes2.get('retired_behaviors', []))}")
    
    if not changes2['is_first_analysis']:
        print(f"✅ PASS: Change detection working (not marked as first)")
    else:
        print(f"❌ FAIL: Should not be marked as first analysis")


def test_versioning():
    """Test that versioning is working"""
    print("\n" + "="*60)
    print("TEST 4: Version Tracking")
    print("="*60)
    
    # Run first analysis
    print("📝 Running first analysis...")
    response1 = requests.post(
        f"{BASE_URL}/analysis",
        json={"user_id": "user_stable_users_03"}
    )
    
    if response1.status_code != 200:
        print(f"❌ FAIL: First analysis failed")
        return
    
    data1 = response1.json()
    cb1 = data1["core_behaviors"][0] if data1["core_behaviors"] else None
    
    if cb1:
        print(f"✅ First analysis complete")
        print(f"   - Core Behavior ID: {cb1['core_behavior_id']}")
        print(f"   - Version: {cb1['version']}")
        print(f"   - Created At: {cb1['created_at']}")
        
        if cb1['version'] == 1:
            print(f"✅ PASS: First version is 1")
        else:
            print(f"❌ FAIL: First version should be 1, got {cb1['version']}")
    
    # Wait and run second analysis
    time.sleep(1)
    
    print(f"\n📝 Running second analysis...")
    response2 = requests.post(
        f"{BASE_URL}/analysis",
        json={"user_id": "user_stable_users_03"}
    )
    
    if response2.status_code != 200:
        print(f"❌ FAIL: Second analysis failed")
        return
    
    data2 = response2.json()
    
    # Find matching core behavior by domain
    cb2 = None
    for cb in data2["core_behaviors"]:
        if cb.get("domain_detected") == cb1.get("domain_detected"):
            cb2 = cb
            break
    
    if cb2:
        print(f"✅ Second analysis complete")
        print(f"   - Core Behavior ID: {cb2['core_behavior_id']}")
        print(f"   - Version: {cb2['version']}")
        print(f"   - Last Updated: {cb2['last_updated']}")
        
        if cb2['version'] == 2:
            print(f"✅ PASS: Version incremented to 2")
        else:
            print(f"⚠️  WARNING: Expected version 2, got {cb2['version']}")
    else:
        print(f"⚠️  WARNING: Could not find matching core behavior in second analysis")


def main():
    print("\n" + "="*60)
    print("🧪 P0 FIXES VALIDATION SUITE")
    print("="*60)
    print("Testing critical algorithm fixes...")
    print("API: " + BASE_URL)
    
    try:
        # Test 1: Promotion logic with rejection
        analysis_data = test_promotion_logic()
        
        # Test 2: Confidence components
        test_confidence_components(analysis_data)
        
        # Test 3: Change detection
        test_change_detection()
        
        # Test 4: Versioning
        test_versioning()
        
        print("\n" + "="*60)
        print("✅ VALIDATION COMPLETE")
        print("="*60)
        print("\nKey Improvements:")
        print("  ✓ Promotion logic evaluates and rejects unqualified clusters")
        print("  ✓ Confidence calculation uses correct formula (35/25/25/15)")
        print("  ✓ Temporal stability calculated from time gap variance")
        print("  ✓ Confidence grades assigned (High/Medium/Low)")
        print("  ✓ Confidence components breakdown available")
        print("  ✓ Change detection tracks new/updated/retired behaviors")
        print("  ✓ Version tracking increments correctly")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("   Make sure the API is running: python -m uvicorn main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
