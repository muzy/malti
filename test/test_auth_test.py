"""
Test suite for the auth test endpoint
"""
import requests
import time
from test_config import (
    BASE_URL,
    VALID_USER_API_KEYS,
    INVALID_API_KEYS,
    VALID_SERVICE_API_KEYS
)

class TestAuthTestEndpoint:
    """Test cases for the /api/v1/auth/test endpoint"""
    
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.auth_test_endpoint = f"{BASE_URL}/api/v1/auth/test"
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_valid_user_auth_test(self):
        """Test auth test endpoint with valid user API keys"""
        print("\n🔍 Testing valid user auth test...")
        
        for username, api_key in VALID_USER_API_KEYS.items():
            headers = {"X-API-Key": api_key}
            
            try:
                response = self.session.get(self.auth_test_endpoint, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    expected_keys = ["authenticated", "user", "thresholds", "timestamp", "rate_limit_info"]
                    if all(key in data for key in expected_keys):
                        if (data["authenticated"] == True and 
                            data["user"]["name"] == username and
                            data["user"]["type"] == "user" and
                            "metrics" in data["user"]["permissions"]):
                            self.log_test(
                                f"Valid {username} auth test", 
                                True, 
                                f"Authentication successful, user: {username}"
                            )
                        else:
                            self.log_test(
                                f"Valid {username} auth test", 
                                False, 
                                f"Invalid response structure: {data}"
                            )
                    else:
                        self.log_test(
                            f"Valid {username} auth test", 
                            False, 
                            f"Missing expected keys in response: {data}"
                        )
                else:
                    self.log_test(
                        f"Valid {username} auth test", 
                        False, 
                        f"Status {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Valid {username} auth test", False, f"Exception: {str(e)}")
    
    def test_invalid_api_key_auth_test(self):
        """Test auth test endpoint with invalid API keys"""
        print("\n🔍 Testing invalid API key auth test...")
        
        for invalid_key in INVALID_API_KEYS:
            headers = {}
            if invalid_key is not None:
                headers["X-API-Key"] = invalid_key
            
            try:
                response = self.session.get(self.auth_test_endpoint, headers=headers)
                
                if response.status_code == 401:
                    self.log_test(f"Invalid API key auth test", True, "Correctly rejected")
                else:
                    self.log_test(
                        f"Invalid API key auth test", 
                        False, 
                        f"Expected 401, got {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Invalid API key auth test", False, f"Exception: {str(e)}")
    
    def test_service_api_key_auth_test(self):
        """Test that service API keys are rejected for auth test endpoint"""
        print("\n🔍 Testing service API key rejection for auth test...")
        
        for service_name, api_key in VALID_SERVICE_API_KEYS.items():
            headers = {"X-API-Key": api_key}
            
            try:
                response = self.session.get(self.auth_test_endpoint, headers=headers)
                
                if response.status_code == 403:
                    self.log_test(f"Service API key '{service_name}' rejected for auth test", True, "Correctly rejected")
                else:
                    self.log_test(
                        f"Service API key '{service_name}' rejected for auth test", 
                        False, 
                        f"Expected 403, got {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Service API key '{service_name}' rejected for auth test", False, f"Exception: {str(e)}")
    
    def test_missing_api_key_auth_test(self):
        """Test auth test endpoint without API key"""
        print("\n🔍 Testing missing API key auth test...")
        
        try:
            response = self.session.get(self.auth_test_endpoint)
            
            if response.status_code == 401:
                self.log_test("Missing API key auth test", True, "Correctly rejected")
            else:
                self.log_test(
                    "Missing API key auth test", 
                    False, 
                    f"Expected 401, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Missing API key auth test", False, f"Exception: {str(e)}")
    
    def test_rate_limiting(self):
        """Test rate limiting on auth test endpoint"""
        print("\n🔍 Testing rate limiting on auth test endpoint...")
        
        # Use the first valid user API key
        api_key = list(VALID_USER_API_KEYS.values())[0]
        headers = {"X-API-Key": api_key}
        
        # Make 11 requests quickly (limit is 10/minute)
        rate_limited = False
        for i in range(11):
            try:
                response = self.session.get(self.auth_test_endpoint, headers=headers)
                
                if response.status_code == 429:
                    rate_limited = True
                    self.log_test(
                        f"Rate limiting test request {i+1}", 
                        True, 
                        f"Rate limited after {i+1} requests (status 429)"
                    )
                    break
                elif response.status_code == 200:
                    if i < 10:
                        self.log_test(
                            f"Rate limiting test request {i+1}", 
                            True, 
                            f"Request {i+1} allowed (status 200)"
                        )
                    else:
                        self.log_test(
                            f"Rate limiting test request {i+1}", 
                            False, 
                            f"Request {i+1} should have been rate limited but got status 200"
                        )
                else:
                    self.log_test(
                        f"Rate limiting test request {i+1}", 
                        False, 
                        f"Unexpected status {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Rate limiting test request {i+1}", False, f"Exception: {str(e)}")
        
        if not rate_limited:
            self.log_test("Rate limiting test", False, "Rate limiting not triggered after 11 requests")
    
    def test_response_structure(self):
        """Test the response structure of auth test endpoint"""
        print("\n🔍 Testing auth test response structure...")
        
        # Use the first valid user API key
        api_key = list(VALID_USER_API_KEYS.values())[0]
        headers = {"X-API-Key": api_key}
        
        try:
            response = self.session.get(self.auth_test_endpoint, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = {
                    "authenticated": bool,
                    "user": dict,
                    "thresholds": dict,
                    "timestamp": str,
                    "rate_limit_info": dict
                }
                
                user_required_fields = {
                    "name": str,
                    "type": str,
                    "permissions": list
                }
                
                rate_limit_required_fields = {
                    "endpoint": str,
                    "limit": str,
                    "description": str
                }

                thresholds_required_fields = {
                    "error_success_threshold": (int, float),
                    "error_warning_threshold": (int, float),
                    "latency_success_threshold": (int, float),
                    "latency_warning_threshold": (int, float)
                }
                
                all_valid = True
                error_messages = []
                
                # Check top-level fields
                for field, expected_type in required_fields.items():
                    if field not in data:
                        all_valid = False
                        error_messages.append(f"Missing field: {field}")
                    elif not isinstance(data[field], expected_type):
                        all_valid = False
                        error_messages.append(f"Field '{field}' should be {expected_type.__name__}, got {type(data[field]).__name__}")
                
                # Check user fields
                if "user" in data:
                    for field, expected_type in user_required_fields.items():
                        if field not in data["user"]:
                            all_valid = False
                            error_messages.append(f"Missing user field: {field}")
                        elif not isinstance(data["user"][field], expected_type):
                            all_valid = False
                            error_messages.append(f"User field '{field}' should be {expected_type.__name__}, got {type(data['user'][field]).__name__}")
                
                # Check rate_limit_info fields
                if "rate_limit_info" in data:
                    for field, expected_type in rate_limit_required_fields.items():
                        if field not in data["rate_limit_info"]:
                            all_valid = False
                            error_messages.append(f"Missing rate_limit_info field: {field}")
                        elif not isinstance(data["rate_limit_info"][field], expected_type):
                            all_valid = False
                            error_messages.append(f"Rate limit info field '{field}' should be {expected_type.__name__}, got {type(data['rate_limit_info'][field]).__name__}")

                # Check thresholds fields
                if "thresholds" in data:
                    for field, expected_types in thresholds_required_fields.items():
                        if field not in data["thresholds"]:
                            all_valid = False
                            error_messages.append(f"Missing thresholds field: {field}")
                        elif not isinstance(data["thresholds"][field], expected_types):
                            all_valid = False
                            type_names = [t.__name__ for t in expected_types]
                            error_messages.append(f"Thresholds field '{field}' should be one of {type_names}, got {type(data['thresholds'][field]).__name__}")

                if all_valid:
                    self.log_test("Auth test response structure", True, "All required fields present with correct types")
                else:
                    self.log_test("Auth test response structure", False, f"Structure issues: {'; '.join(error_messages)}")
            else:
                self.log_test("Auth test response structure", False, f"Failed to get response: {response.status_code}")
                
        except Exception as e:
            self.log_test("Auth test response structure", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all auth test endpoint tests"""
        print("🚀 Starting Auth Test Endpoint Tests")
        print("=" * 50)
        
        self.test_valid_user_auth_test()
        self.test_invalid_api_key_auth_test()
        self.test_service_api_key_auth_test()
        self.test_missing_api_key_auth_test()
        self.test_response_structure()
        self.test_rate_limiting()
        
        # Summary
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"📊 Auth Test Tests Summary: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All auth test tests passed!")
        else:
            print("⚠️  Some auth test tests failed!")
            
        return passed == total

if __name__ == "__main__":
    tester = TestAuthTestEndpoint()
    tester.run_all_tests()