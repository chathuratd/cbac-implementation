"""
Quick test script to verify CBAC API functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_metrics():
    """Test metrics endpoint"""
    print("\n📊 Testing Metrics...")
    response = requests.get(f"{BASE_URL}/health/metrics")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_summary(user_id="user_stable_users_01"):
    """Test summary endpoint"""
    print(f"\n📋 Testing Summary for {user_id}...")
    response = requests.get(f"{BASE_URL}/analysis/{user_id}/summary")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_analysis(user_id="user_stable_users_01", min_cluster_size=3):
    """Test main analysis endpoint"""
    print(f"\n🧠 Testing Analysis for {user_id}...")
    
    payload = {
        "user_id": user_id,
        "min_cluster_size": min_cluster_size,
        "include_prompts": False
    }
    
    response = requests.post(
        f"{BASE_URL}/analysis",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Analysis Success!")
        print(f"   Total Behaviors: {data['total_behaviors_analyzed']}")
        print(f"   Clusters Found: {data['num_clusters']}")
        print(f"   Core Behaviors: {len(data['core_behaviors'])}")
        print(f"   Processing Time: {data['metadata']['processing_time_ms']:.2f}ms")
        
        print("\n📌 Core Behaviors:")
        for i, cb in enumerate(data['core_behaviors'], 1):
            print(f"\n   {i}. {cb['generalized_statement']}")
            print(f"      Confidence: {cb['confidence_score']:.2%}")
            print(f"      Domain: {cb['domain_detected']}")
            print(f"      Evidence: {len(cb['evidence_chain'])} behaviors")
    else:
        print(f"❌ Error: {response.text}")
    
    return response.status_code == 200

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 CBAC API - Quick Test Suite")
    print("=" * 60)
    
    results = {
        "health": test_health(),
        "metrics": test_metrics(),
        "summary": test_summary(),
        "analysis": test_analysis()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    print("\n" + ("🎉 All tests passed!" if all_passed else "⚠️  Some tests failed"))
    
    return all_passed

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("   Make sure the API is running: python main.py")
