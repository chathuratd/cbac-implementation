"""
End-to-End Testing Script for CBAC System
==========================================
This script runs the complete workflow:
1. Check prerequisites (Docker services)
2. Load test data into databases
3. Start API server
4. Run analysis tests
5. Verify results

Usage:
    python run_full_test.py
"""

import os
import sys
import time
import subprocess
import requests
import json
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_num, message):
    """Print formatted step header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"STEP {step_num}: {message}")
    print(f"{'='*70}{Colors.ENDC}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")

def check_prerequisites():
    """Check if Docker services are running"""
    print_step(1, "Checking Prerequisites")
    
    # Check Qdrant
    print_info("Checking Qdrant...")
    try:
        response = requests.get("http://localhost:6333", timeout=5)
        if response.status_code == 200:
            print_success("Qdrant is running")
        else:
            print_error(f"Qdrant responded with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Qdrant is not accessible: {e}")
        print_info("Start Qdrant with: docker-compose up -d qdrant")
        return False
    
    # Check MongoDB
    print_info("Checking MongoDB...")
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://admin:admin123@localhost:27017/?authSource=admin", serverSelectionTimeoutMS=5000)
        client.server_info()
        print_success("MongoDB is running")
        return True
    except Exception as e:
        print_error(f"MongoDB is not accessible: {e}")
        print_info("Start MongoDB with: docker-compose up -d mongodb")
        return False

def load_test_data():
    """Load test data into databases"""
    print_step(2, "Loading Test Data into Databases")
    
    script_dir = Path(__file__).parent
    data_setup_dir = script_dir / "data_setup"
    
    # Load MongoDB data
    print_info("Loading prompts into MongoDB...")
    mongo_script = data_setup_dir / "mongo_db_save.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(mongo_script)],
            cwd=str(data_setup_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print_success("MongoDB data loaded successfully")
        else:
            print_error(f"MongoDB load failed: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Failed to run MongoDB script: {e}")
        return False
    
    # Load Qdrant data
    print_info("Loading behaviors into Qdrant...")
    qdrant_script = data_setup_dir / "vector_db_save.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(qdrant_script)],
            cwd=str(data_setup_dir),
            capture_output=True,
            text=True,
            timeout=120  # Embedding can take time
        )
        
        if result.returncode == 0:
            print(result.stdout)
            print_success("Qdrant data loaded successfully")
        else:
            print_error(f"Qdrant load failed: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Failed to run Qdrant script: {e}")
        return False
    
    return True

def check_api_running():
    """Check if API is already running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Inform user to start API server"""
    print_step(3, "API Server Setup")
    
    if check_api_running():
        print_success("API server is already running")
        return True
    
    print_info("API server is not running")
    print(f"\n{Colors.WARNING}Please start the API server in a separate terminal:{Colors.ENDC}")
    print(f"{Colors.BOLD}cd cbac_api{Colors.ENDC}")
    print(f"{Colors.BOLD}python main.py{Colors.ENDC}\n")
    
    # Wait for user confirmation
    while True:
        response = input("Press Enter once the API server is running (or 'q' to quit): ").strip().lower()
        if response == 'q':
            return False
        
        if check_api_running():
            print_success("API server is running!")
            return True
        else:
            print_error("Cannot connect to API. Please ensure it's running on http://localhost:8000")

def run_api_tests():
    """Run comprehensive API tests"""
    print_step(4, "Running API Tests")
    
    BASE_URL = "http://localhost:8000"
    USER_ID = "user_2_1765824099"
    
    # Test 1: Health Check
    print_info("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data['status']}")
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False
    
    # Test 2: Metrics
    print_info("Test 2: System Metrics")
    try:
        response = requests.get(f"{BASE_URL}/health/metrics")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Metrics retrieved:")
            print(f"  - Qdrant: {data['qdrant']['status']}")
            print(f"  - MongoDB: {data['mongodb']['status']}")
        else:
            print_error(f"Metrics check failed: {response.status_code}")
    except Exception as e:
        print_error(f"Metrics check error: {e}")
    
    # Test 3: User Summary
    print_info(f"Test 3: User Summary for {USER_ID}")
    try:
        response = requests.get(f"{BASE_URL}/analysis/{USER_ID}/summary")
        if response.status_code == 200:
            data = response.json()
            print_success("Summary retrieved:")
            print(f"  - Total behaviors: {data.get('total_behaviors', 'N/A')}")
            print(f"  - Domain: {data.get('domain', 'N/A')}")
            print(f"  - Expertise level: {data.get('expertise_level', 'N/A')}")
        else:
            print_error(f"Summary failed: {response.status_code}")
    except Exception as e:
        print_error(f"Summary error: {e}")
    
    # Test 4: Full Analysis
    print_info(f"Test 4: Running Full Behavior Analysis for {USER_ID}")
    try:
        payload = {
            "user_id": USER_ID,
            "min_cluster_size": 3,
            "include_prompts": True
        }
        
        response = requests.post(
            f"{BASE_URL}/analysis",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Analysis completed successfully!")
            print(f"  - Analysis ID: {data.get('analysis_id', 'N/A')}")
            print(f"  - User: {data.get('user_id', 'N/A')}")
            print(f"  - Total behaviors: {data.get('total_behaviors', 'N/A')}")
            print(f"  - Core patterns found: {len(data.get('core_patterns', []))}")
            
            # Save results
            output_dir = Path(__file__).parent.parent / "test_data" / "analysis_results"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{USER_ID}_test_result.json"
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print_success(f"Results saved to: {output_file}")
            
            # Display core patterns
            if data.get('core_patterns'):
                print(f"\n{Colors.BOLD}Core Patterns:{Colors.ENDC}")
                for i, pattern in enumerate(data['core_patterns'][:3], 1):
                    print(f"  {i}. {pattern.get('pattern_label', 'N/A')}")
                    print(f"     - Behaviors: {pattern.get('behavior_count', 0)}")
                    print(f"     - Credibility: {pattern.get('avg_credibility', 0):.2f}")
            
            return True
        else:
            print_error(f"Analysis failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print_error(f"Analysis error: {e}")
        return False

def main():
    """Main test execution"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print("CBAC SYSTEM - END-TO-END TEST")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    # Step 1: Prerequisites
    if not check_prerequisites():
        print_error("Prerequisites check failed. Please start required services.")
        print_info("Run: docker-compose up -d")
        return 1
    
    # Step 2: Load Data
    if not load_test_data():
        print_error("Data loading failed. Check error messages above.")
        return 1
    
    # Step 3: Start API
    if not start_api_server():
        print_error("API server setup failed.")
        return 1
    
    # Step 4: Run Tests
    if not run_api_tests():
        print_error("API tests failed.")
        return 1
    
    # Success
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
    print("=" * 70)
    print("✅ ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
