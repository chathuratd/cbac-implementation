"""
Quick Test Script for Phase 1 Enhanced Features
Tests all new endpoints and incremental analysis functionality
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
TEST_USER_ID = "user_4_1765826173"


def test_endpoint(name: str, method: str, url: str, data: Dict = None) -> Dict[str, Any]:
    """Test an endpoint and return result"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Method: {method} {url}")
    print(f"{'='*60}")
    
    try:
        start = time.time()
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        elapsed = (time.time() - start) * 1000
        
        print(f"Status: {response.status_code}")
        print(f"Time: {elapsed:.2f}ms")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Response preview:")
            print(json.dumps(result, indent=2)[:500] + "...")
            return {"success": True, "data": result, "time_ms": elapsed}
        else:
            print(f"Error: {response.text}")
            return {"success": False, "error": response.text, "time_ms": elapsed}
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    print("="*60)
    print("Phase 1 Enhanced - Endpoint Testing")
    print("="*60)
    
    results = {}
    
    # Test 1: POST /analysis (full analysis)
    results["full_analysis"] = test_endpoint(
        "Full Analysis",
        "POST",
        f"{BASE_URL}/analysis",
        {"user_id": TEST_USER_ID, "min_cluster_size": 3}
    )
    
    # Test 2: GET /analysis/{user_id}/latest
    results["latest_analysis"] = test_endpoint(
        "Get Latest Analysis (Cached)",
        "GET",
        f"{BASE_URL}/analysis/{TEST_USER_ID}/latest"
    )
    
    # Test 3: GET /analysis/{user_id}/history
    results["history"] = test_endpoint(
        "Analysis History",
        "GET",
        f"{BASE_URL}/analysis/{TEST_USER_ID}/history?limit=5"
    )
    
    # Test 4: GET /analysis/{user_id}/stats
    results["stats"] = test_endpoint(
        "Analysis Statistics",
        "GET",
        f"{BASE_URL}/analysis/{TEST_USER_ID}/stats"
    )
    
    # Test 5: GET /analysis/by-id/{analysis_id}
    if results["history"]["success"]:
        analyses = results["history"]["data"].get("analyses", [])
        if analyses:
            analysis_id = analyses[0]["analysis_id"]
            results["by_id"] = test_endpoint(
                "Get Analysis by ID",
                "GET",
                f"{BASE_URL}/analysis/by-id/{analysis_id}"
            )
    
    # Test 6: POST /analysis?force=false (incremental)
    results["incremental_analysis"] = test_endpoint(
        "Incremental Analysis (No Force)",
        "POST",
        f"{BASE_URL}/analysis?force=false",
        {"user_id": TEST_USER_ID, "min_cluster_size": 3}
    )
    
    # Test 7: POST /analysis?force=true (force re-analysis)
    results["forced_analysis"] = test_endpoint(
        "Forced Re-Analysis",
        "POST",
        f"{BASE_URL}/analysis?force=true",
        {"user_id": TEST_USER_ID, "min_cluster_size": 3}
    )
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results.values() if r.get("success"))
    total = len(results)
    
    print(f"\nTests Passed: {successful}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result.get("success") else "❌ FAIL"
        time_str = f"{result.get('time_ms', 0):.2f}ms" if result.get("time_ms") else "N/A"
        print(f"{status} - {test_name} ({time_str})")
    
    # Performance comparison
    if results["full_analysis"]["success"] and results["incremental_analysis"]["success"]:
        full_time = results["full_analysis"]["time_ms"]
        incremental_time = results["incremental_analysis"]["time_ms"]
        speedup = full_time / incremental_time if incremental_time > 0 else 0
        
        print("\n" + "="*60)
        print("PERFORMANCE ANALYSIS")
        print("="*60)
        print(f"Full Analysis Time: {full_time:.2f}ms")
        print(f"Incremental Analysis Time: {incremental_time:.2f}ms")
        print(f"Speedup: {speedup:.1f}x faster")
        print(f"Time Saved: {full_time - incremental_time:.2f}ms ({((full_time - incremental_time) / full_time * 100):.1f}%)")
    
    # Change detection analysis
    if results["forced_analysis"]["success"]:
        data = results["forced_analysis"]["data"]
        if "metadata" in data and "changes_detected" in data["metadata"]:
            changes = data["metadata"]["changes_detected"]
            if "summary" in changes:
                print("\n" + "="*60)
                print("CHANGE DETECTION SUMMARY")
                print("="*60)
                summary = changes["summary"]
                print(f"Total Changes: {summary.get('total_changes', 0)}")
                print(f"New Behaviors: {summary.get('new_count', 0)}")
                print(f"Strengthened: {summary.get('strengthened_count', 0)}")
                print(f"Weakened: {summary.get('weakened_count', 0)}")
                print(f"Minor Updates: {summary.get('minor_updates_count', 0)}")
                print(f"Stable: {summary.get('stable_count', 0)}")
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
