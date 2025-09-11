#!/usr/bin/env python3
"""
Main test runner for the Malti API test suite
"""
import sys
import time
from datetime import datetime

# Import test modules
from test_health import TestHealthEndpoints
from test_ingest import TestIngestEndpoint
from test_metrics import TestMetricsEndpoints

def main():
    """Run the complete test suite"""
    print("🧪 Malti API Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Show loaded configuration
    from test_config import print_loaded_config
    print_loaded_config()
    print("=" * 60)
    
    # Track overall results
    all_results = []
    start_time = time.time()
    
    # Run health tests first
    print("\n1️⃣  HEALTH ENDPOINTS")
    health_tester = TestHealthEndpoints()
    health_success = health_tester.run_all_tests()
    all_results.extend(health_tester.test_results)
    
    if not health_success:
        print("\n❌ Health tests failed! Server may not be running.")
        print("Please ensure the Malti server is started before running tests.")
        print("Run: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        sys.exit(1)
    
    # Run ingest tests
    print("\n2️⃣  INGEST ENDPOINT")
    ingest_tester = TestIngestEndpoint()
    ingest_success = ingest_tester.run_all_tests()
    all_results.extend(ingest_tester.test_results)
    
    # Run metrics tests
    print("\n3️⃣  METRICS ENDPOINTS")
    metrics_tester = TestMetricsEndpoints()
    metrics_success = metrics_tester.run_all_tests()
    all_results.extend(metrics_tester.test_results)
    
    # Calculate overall results
    end_time = time.time()
    duration = end_time - start_time
    
    passed = sum(1 for result in all_results if result["success"])
    total = len(all_results)
    
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print(f"Duration: {duration:.2f} seconds")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! 🎉")
        print("The Malti API is working correctly!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nFailed tests:")
        for result in all_results:
            if not result["success"]:
                print(f"  - {result['test']}: {result['message']}")
        sys.exit(1)

if __name__ == "__main__":
    main()