"""
Test suite for the metrics endpoints
"""
import requests
import json
from datetime import datetime, timedelta
from test_config import (
    METRICS_AGGREGATE_ENDPOINT,
    METRICS_RAW_ENDPOINT,
    METRICS_REALTIME_ENDPOINT,
    VALID_USER_API_KEYS,
    INVALID_API_KEYS,
    VALID_SERVICE_API_KEYS
)

class TestMetricsEndpoints:
    """Test cases for the /api/v1/metrics/* endpoints"""
    
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
    
    def test_valid_user_aggregate_metrics(self):
        """Test aggregate metrics with valid user API keys"""
        print("\n🔍 Testing valid user aggregate metrics...")
        
        for username, api_key in VALID_USER_API_KEYS.items():
            headers = {"X-API-Key": api_key}
            params = {
                "limit": 10,
                "interval": "5min"
            }
            
            try:
                response = self.session.get(METRICS_AGGREGATE_ENDPOINT, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"Valid {username} aggregate metrics", 
                        True, 
                        f"Retrieved {len(data)} records"
                    )
                else:
                    self.log_test(
                        f"Valid {username} aggregate metrics", 
                        False, 
                        f"Status {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Valid {username} aggregate metrics", False, f"Exception: {str(e)}")
    
    def test_valid_user_raw_metrics(self):
        """Test raw metrics with valid user API keys"""
        print("\n🔍 Testing valid user raw metrics...")
        
        for username, api_key in VALID_USER_API_KEYS.items():
            headers = {"X-API-Key": api_key}
            params = {"limit": 10}
            
            try:
                response = self.session.get(METRICS_RAW_ENDPOINT, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"Valid {username} raw metrics", 
                        True, 
                        f"Retrieved {len(data)} records"
                    )
                else:
                    self.log_test(
                        f"Valid {username} raw metrics", 
                        False, 
                        f"Status {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Valid {username} raw metrics", False, f"Exception: {str(e)}")
    
    def test_invalid_api_key_metrics(self):
        """Test metrics endpoints with invalid API keys"""
        print("\n🔍 Testing invalid API key metrics...")
        
        endpoints = [
            ("aggregate", METRICS_AGGREGATE_ENDPOINT),
            ("raw", METRICS_RAW_ENDPOINT)
        ]
        
        for endpoint_name, endpoint_url in endpoints:
            for invalid_key in INVALID_API_KEYS:
                headers = {}
                if invalid_key is not None:
                    headers["X-API-Key"] = invalid_key
                
                try:
                    response = self.session.get(endpoint_url, headers=headers)
                    
                    if response.status_code == 401:
                        self.log_test(f"Invalid API key {endpoint_name} metrics", True, "Correctly rejected")
                    else:
                        self.log_test(
                            f"Invalid API key {endpoint_name} metrics", 
                            False, 
                            f"Expected 401, got {response.status_code}: {response.text}"
                        )
                        
                except Exception as e:
                    self.log_test(f"Invalid API key {endpoint_name} metrics", False, f"Exception: {str(e)}")
    
    def test_service_api_key_metrics(self):
        """Test that service API keys are rejected for metrics endpoints"""
        print("\n🔍 Testing service API key rejection for metrics...")
        
        endpoints = [
            ("aggregate", METRICS_AGGREGATE_ENDPOINT),
            ("raw", METRICS_RAW_ENDPOINT)
        ]
        
        for endpoint_name, endpoint_url in endpoints:
            for service_name, api_key in VALID_SERVICE_API_KEYS.items():
                headers = {"X-API-Key": api_key}
                
                try:
                    response = self.session.get(endpoint_url, headers=headers)
                    
                    if response.status_code == 403:
                        self.log_test(f"Service API key '{service_name}' rejected for {endpoint_name}", True, "Correctly rejected")
                    else:
                        self.log_test(
                            f"Service API key '{service_name}' rejected for {endpoint_name}", 
                            False, 
                            f"Expected 403, got {response.status_code}: {response.text}"
                        )
                        
                except Exception as e:
                    self.log_test(f"Service API key '{service_name}' rejected for {endpoint_name}", False, f"Exception: {str(e)}")
    
    def test_missing_api_key_metrics(self):
        """Test metrics endpoints without API key"""
        print("\n🔍 Testing missing API key metrics...")
        
        endpoints = [
            ("aggregate", METRICS_AGGREGATE_ENDPOINT),
            ("raw", METRICS_RAW_ENDPOINT)
        ]
        
        for endpoint_name, endpoint_url in endpoints:
            try:
                response = self.session.get(endpoint_url)
                
                if response.status_code == 401:
                    self.log_test(f"Missing API key {endpoint_name} metrics", True, "Correctly rejected")
                else:
                    self.log_test(
                        f"Missing API key {endpoint_name} metrics", 
                        False, 
                        f"Expected 401, got {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Missing API key {endpoint_name} metrics", False, f"Exception: {str(e)}")
    
    def test_metrics_filters(self):
        """Test metrics endpoints with various filters"""
        print("\n🔍 Testing metrics filters...")
        
        # Use the first valid user API key
        api_key = list(VALID_USER_API_KEYS.values())[0]
        headers = {"X-API-Key": api_key}
        
        # Test different filter combinations
        filter_tests = [
            {"service": "auth-service", "limit": 5},
            {"method": "GET", "limit": 5},
            {"endpoint": "/api/v1/login", "limit": 5},
            {"consumer": "web-app", "limit": 5},
            {"interval": "1hour", "limit": 5},
            {"service": "auth-service", "method": "POST", "limit": 5},
        ]
        
        endpoints = [
            ("aggregate", METRICS_AGGREGATE_ENDPOINT),
            ("raw", METRICS_RAW_ENDPOINT)
        ]
        
        for endpoint_name, endpoint_url in endpoints:
            for i, filters in enumerate(filter_tests):
                try:
                    response = self.session.get(endpoint_url, headers=headers, params=filters)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.log_test(
                            f"Metrics filters {endpoint_name} {i+1}", 
                            True, 
                            f"Retrieved {len(data)} records with filters"
                        )
                    else:
                        self.log_test(
                            f"Metrics filters {endpoint_name} {i+1}", 
                            False, 
                            f"Status {response.status_code}: {response.text}"
                        )
                        
                except Exception as e:
                    self.log_test(f"Metrics filters {endpoint_name} {i+1}", False, f"Exception: {str(e)}")
    
    def test_time_range_filters(self):
        """Test metrics endpoints with time range filters"""
        print("\n🔍 Testing time range filters...")
        
        # Use the first valid user API key
        api_key = list(VALID_USER_API_KEYS.values())[0]
        headers = {"X-API-Key": api_key}
        
        # Create time ranges in UTC
        from datetime import timezone
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        time_tests = [
            {"start_time": one_hour_ago.isoformat(), "limit": 5},
            {"end_time": now.isoformat(), "limit": 5},
            {"start_time": one_day_ago.isoformat(), "end_time": now.isoformat(), "limit": 5},
        ]
        
        endpoints = [
            ("aggregate", METRICS_AGGREGATE_ENDPOINT),
            ("raw", METRICS_RAW_ENDPOINT)
        ]
        
        for endpoint_name, endpoint_url in endpoints:
            for i, time_filters in enumerate(time_tests):
                try:
                    response = self.session.get(endpoint_url, headers=headers, params=time_filters)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.log_test(
                            f"Time range {endpoint_name} {i+1}", 
                            True, 
                            f"Retrieved {len(data)} records with time filters"
                        )
                    else:
                        self.log_test(
                            f"Time range {endpoint_name} {i+1}", 
                            False, 
                            f"Status {response.status_code}: {response.text}"
                        )
                        
                except Exception as e:
                    self.log_test(f"Time range {endpoint_name} {i+1}", False, f"Exception: {str(e)}")
    
    def test_invalid_parameters(self):
        """Test metrics endpoints with invalid parameters"""
        print("\n🔍 Testing invalid parameters...")
        
        # Use the first valid user API key
        api_key = list(VALID_USER_API_KEYS.values())[0]
        headers = {"X-API-Key": api_key}
        
        # Test invalid parameters
        invalid_params = [
            {"limit": -1},  # Negative limit
            {"limit": 0},   # Zero limit
            {"interval": "invalid"},  # Invalid interval
            {"limit": "not_a_number"},  # Non-numeric limit
        ]
        
        endpoints = [
            ("aggregate", METRICS_AGGREGATE_ENDPOINT),
            ("raw", METRICS_RAW_ENDPOINT)
        ]
        
        for endpoint_name, endpoint_url in endpoints:
            for i, params in enumerate(invalid_params):
                try:
                    response = self.session.get(endpoint_url, headers=headers, params=params)
                    
                    # Some invalid parameters might be handled gracefully (e.g., default values)
                    # So we accept both 200 (with defaults) and 422 (validation error)
                    if response.status_code in [200, 422]:
                        self.log_test(
                            f"Invalid params {endpoint_name} {i+1}", 
                            True, 
                            f"Handled gracefully (status {response.status_code})"
                        )
                    else:
                        self.log_test(
                            f"Invalid params {endpoint_name} {i+1}", 
                            False, 
                            f"Unexpected status {response.status_code}: {response.text}"
                        )
                        
                except Exception as e:
                    self.log_test(f"Invalid params {endpoint_name} {i+1}", False, f"Exception: {str(e)}")

    def test_realtime_endpoint(self):
        """Test the realtime metrics endpoint"""
        print("\n🔍 Testing realtime metrics endpoint...")
        
        # Use the first valid user API key
        api_key = list(VALID_USER_API_KEYS.values())[0]
        headers = {"X-API-Key": api_key}
        
        # Test basic realtime request
        try:
            response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers, params={"limit": 10})
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Realtime endpoint basic", 
                    True, 
                    f"Retrieved {len(data)} realtime records"
                )
            else:
                self.log_test(
                    "Realtime endpoint basic", 
                    False, 
                    f"Status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Realtime endpoint basic", False, f"Exception: {str(e)}")
        
        # Test realtime endpoint with time ranges
        from datetime import timezone
        now = datetime.now(timezone.utc)
        thirty_minutes_ago = now - timedelta(minutes=30)
        
        params = {
            "start_time": thirty_minutes_ago.isoformat(),
            "end_time": now.isoformat(),
            "limit": 20
        }
        
        try:
            response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Realtime endpoint with time range", 
                    True, 
                    f"Retrieved {len(data)} records for 30-minute window"
                )
            else:
                self.log_test(
                    "Realtime endpoint with time range", 
                    False, 
                    f"Status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Realtime endpoint with time range", False, f"Exception: {str(e)}")
        
        # Test realtime endpoint with filters
        filter_params = {
            "service": "auth-service",
            "limit": 15
        }
        
        try:
            response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers, params=filter_params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Realtime endpoint with service filter", 
                    True, 
                    f"Retrieved {len(data)} filtered realtime records"
                )
            else:
                self.log_test(
                    "Realtime endpoint with service filter", 
                    False, 
                    f"Status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Realtime endpoint with service filter", False, f"Exception: {str(e)}")

    def test_realtime_endpoint_time_limits(self):
        """Test realtime endpoint time range limits (should be max 60 minutes)"""
        print("\n🔍 Testing realtime endpoint time limits...")
        
        # Use the first valid user API key
        api_key = list(VALID_USER_API_KEYS.values())[0]
        headers = {"X-API-Key": api_key}
        
        # Test with time range exceeding 60 minutes (should be rejected)
        from datetime import timezone
        now = datetime.now(timezone.utc)
        ninety_minutes_ago = now - timedelta(minutes=90)
        
        params = {
            "start_time": ninety_minutes_ago.isoformat(),
            "end_time": now.isoformat(),
            "limit": 10
        }
        
        try:
            response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers, params=params)
            
            if response.status_code == 422:
                self.log_test(
                    "Realtime endpoint time limit validation", 
                    True, 
                    "Correctly rejected 90-minute time range with 422 status"
                )
            else:
                self.log_test(
                    "Realtime endpoint time limit validation", 
                    False, 
                    f"Expected 422, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Realtime endpoint time limit validation", False, f"Exception: {str(e)}")
        
        # Test with valid 60-minute time range (should be accepted)
        sixty_minutes_ago = now - timedelta(minutes=60)
        
        params = {
            "start_time": sixty_minutes_ago.isoformat(),
            "end_time": now.isoformat(),
            "limit": 10
        }
        
        try:
            response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Realtime endpoint valid 60min range", 
                    True, 
                    f"Accepted 60-minute range, retrieved {len(data)} records"
                )
            else:
                self.log_test(
                    "Realtime endpoint valid 60min range", 
                    False, 
                    f"Status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Realtime endpoint valid 60min range", False, f"Exception: {str(e)}")

    def test_realtime_endpoint_authentication(self):
        """Test realtime endpoint authentication requirements"""
        print("\n🔍 Testing realtime endpoint authentication...")
        
        # Test with invalid API key
        for invalid_key in INVALID_API_KEYS[:2]:  # Test first 2 invalid keys
            headers = {}
            if invalid_key is not None:
                headers["X-API-Key"] = invalid_key
            
            try:
                response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers)
                
                if response.status_code == 401:
                    self.log_test(f"Realtime invalid API key '{invalid_key}'", True, "Correctly rejected")
                else:
                    self.log_test(
                        f"Realtime invalid API key '{invalid_key}'", 
                        False, 
                        f"Expected 401, got {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Realtime invalid API key '{invalid_key}'", False, f"Exception: {str(e)}")
        
        # Test that service API keys are rejected for realtime endpoint
        for service_name, api_key in VALID_SERVICE_API_KEYS.items():
            headers = {"X-API-Key": api_key}
            
            try:
                response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers)
                
                if response.status_code == 403:
                    self.log_test(f"Realtime service API key '{service_name}' rejected", True, "Correctly rejected")
                else:
                    self.log_test(
                        f"Realtime service API key '{service_name}' rejected", 
                        False, 
                        f"Expected 403, got {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Realtime service API key '{service_name}' rejected", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all metrics endpoint tests"""
        print("🚀 Starting Metrics Endpoints Tests")
        print("=" * 50)
        
        self.test_valid_user_aggregate_metrics()
        self.test_valid_user_raw_metrics()
        self.test_invalid_api_key_metrics()
        self.test_service_api_key_metrics()
        self.test_missing_api_key_metrics()
        self.test_metrics_filters()
        self.test_time_range_filters()
        self.test_invalid_parameters()
        self.test_realtime_endpoint()
        self.test_realtime_endpoint_time_limits()
        self.test_realtime_endpoint_authentication()
        
        # Summary
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"📊 Metrics Tests Summary: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All metrics tests passed!")
        else:
            print("⚠️  Some metrics tests failed!")
            
        return passed == total