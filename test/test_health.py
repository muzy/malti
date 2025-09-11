"""
Test suite for health and basic endpoints
"""
import requests
from test_config import HEALTH_ENDPOINT, ROOT_ENDPOINT

class TestHealthEndpoints:
    """Test cases for health and basic endpoints"""
    
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_health_endpoint(self):
        """Test the /health endpoint"""
        print("\n🔍 Testing health endpoint...")
        
        try:
            response = self.session.get(HEALTH_ENDPOINT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health endpoint", True, "Server is healthy")
                else:
                    self.log_test("Health endpoint", False, f"Unexpected status: {data}")
            else:
                self.log_test("Health endpoint", False, f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Health endpoint", False, f"Exception: {str(e)}")
    
    def test_root_endpoint(self):
        """Test the root / endpoint"""
        print("\n🔍 Testing root endpoint...")
        
        try:
            response = self.session.get(ROOT_ENDPOINT)
            
            if response.status_code == 200:
                data = response.text # text is a property, not a method
                if "html" in data:
                    self.log_test("Root endpoint", True, f"Got frontend html")
                else:
                    self.log_test("Root endpoint", False, f"Unexpected response: {data}")
            else:
                self.log_test("Root endpoint", False, f"Status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Root endpoint", False, f"Exception: {str(e)}")
    
    
    def run_all_tests(self):
        """Run all health endpoint tests"""
        print("🚀 Starting Health Endpoints Tests")
        print("=" * 50)
        
        self.test_health_endpoint()
        self.test_root_endpoint()
        
        # Summary
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"📊 Health Tests Summary: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All health tests passed!")
        else:
            print("⚠️  Some health tests failed!")
            
        return passed == total