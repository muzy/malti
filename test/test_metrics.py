"""
Test suite for the metrics endpoints
"""
import requests
import json
from datetime import datetime, timedelta
from test_config import (
    METRICS_AGGREGATE_ENDPOINT,
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
    
    def validate_dashboard_response(self, data: dict) -> tuple[bool, str]:
        """Validate that the response has the expected DashboardMetricsResponse structure"""
        required_keys = ['time_series', 'metrics_summary', 'endpoints', 'status_distribution', 'consumers', 'system_overview']
        
        for key in required_keys:
            if key not in data:
                return False, f"Missing required key: {key}"
        
        # Validate time_series structure
        if not isinstance(data['time_series'], list):
            return False, "time_series should be a list"
        
        if len(data['time_series']) > 0:
            ts_item = data['time_series'][0]
            ts_required = ['bucket', 'total_requests']
            for field in ts_required:
                if field not in ts_item:
                    return False, f"time_series item missing field: {field}"
        
        # Validate metrics_summary structure
        if not isinstance(data['metrics_summary'], dict):
            return False, "metrics_summary should be a dict"
        
        if 'total_requests' not in data['metrics_summary']:
            return False, "metrics_summary missing total_requests"
        
        # Validate endpoints structure
        if not isinstance(data['endpoints'], list):
            return False, "endpoints should be a list"
        
        if len(data['endpoints']) > 0:
            endpoint_item = data['endpoints'][0]
            endpoint_required = ['endpoint', 'method', 'total_requests', 'error_count', 'error_rate']
            for field in endpoint_required:
                if field not in endpoint_item:
                    return False, f"endpoints item missing field: {field}"
        
        # Validate status_distribution structure
        if not isinstance(data['status_distribution'], list):
            return False, "status_distribution should be a list"
        
        # Validate consumers structure
        if not isinstance(data['consumers'], list):
            return False, "consumers should be a list"
        
        # Validate system_overview structure
        if not isinstance(data['system_overview'], dict):
            return False, "system_overview should be a dict"
        
        overview_required = ['total_requests', 'total_errors', 'error_rate']
        for field in overview_required:
            if field not in data['system_overview']:
                return False, f"system_overview missing field: {field}"
        
        return True, "Valid DashboardMetricsResponse structure"
    
    def test_valid_user_aggregate_metrics(self):
        """Test aggregate metrics with valid user API keys"""
        print("\n🔍 Testing valid user aggregate metrics...")
        
        for username, api_key in VALID_USER_API_KEYS.items():
            headers = {"X-API-Key": api_key}
            params = {
                "interval": "5min"
            }
            
            try:
                response = self.session.get(METRICS_AGGREGATE_ENDPOINT, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid, msg = self.validate_dashboard_response(data)
                    
                    if is_valid:
                        total_requests = data['system_overview']['total_requests']
                        time_series_count = len(data['time_series'])
                        self.log_test(
                            f"Valid {username} aggregate metrics", 
                            True, 
                            f"Retrieved dashboard data: {total_requests} requests, {time_series_count} time buckets"
                        )
                    else:
                        self.log_test(
                            f"Valid {username} aggregate metrics", 
                            False, 
                            f"Invalid response structure: {msg}"
                        )
                else:
                    self.log_test(
                        f"Valid {username} aggregate metrics", 
                        False, 
                        f"Status {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Valid {username} aggregate metrics", False, f"Exception: {str(e)}")
    
    def test_invalid_api_key_metrics(self):
        """Test metrics endpoints with invalid API keys"""
        print("\n🔍 Testing invalid API key metrics...")

        for invalid_key in INVALID_API_KEYS:
            headers = {}
            if invalid_key is not None:
                headers["X-API-Key"] = invalid_key

            try:
                response = self.session.get(METRICS_AGGREGATE_ENDPOINT, headers=headers)

                if response.status_code == 401:
                    self.log_test("Invalid API key aggregate metrics", True, "Correctly rejected")
                else:
                    self.log_test(
                        "Invalid API key aggregate metrics",
                        False,
                        f"Expected 401, got {response.status_code}: {response.text}"
                    )

            except Exception as e:
                self.log_test("Invalid API key aggregate metrics", False, f"Exception: {str(e)}")
    
    def test_service_api_key_metrics(self):
        """Test that service API keys are rejected for metrics endpoints"""
        print("\n🔍 Testing service API key rejection for metrics...")

        for service_name, api_key in VALID_SERVICE_API_KEYS.items():
            headers = {"X-API-Key": api_key}

            try:
                response = self.session.get(METRICS_AGGREGATE_ENDPOINT, headers=headers)

                if response.status_code == 403:
                    self.log_test(f"Service API key '{service_name}' rejected for aggregate", True, "Correctly rejected")
                else:
                    self.log_test(
                        f"Service API key '{service_name}' rejected for aggregate",
                        False,
                        f"Expected 403, got {response.status_code}: {response.text}"
                    )

            except Exception as e:
                self.log_test(f"Service API key '{service_name}' rejected for aggregate", False, f"Exception: {str(e)}")
    
    def test_missing_api_key_metrics(self):
        """Test metrics endpoints without API key"""
        print("\n🔍 Testing missing API key metrics...")

        try:
            response = self.session.get(METRICS_AGGREGATE_ENDPOINT)

            if response.status_code == 401:
                self.log_test("Missing API key aggregate metrics", True, "Correctly rejected")
            else:
                self.log_test(
                    "Missing API key aggregate metrics",
                    False,
                    f"Expected 401, got {response.status_code}: {response.text}"
                )

        except Exception as e:
            self.log_test("Missing API key aggregate metrics", False, f"Exception: {str(e)}")
    
    def test_metrics_filters(self):
        """Test metrics endpoints with various filters"""
        print("\n🔍 Testing metrics filters...")
        
        # Use the first valid user API key
        api_key = list(VALID_USER_API_KEYS.values())[0]
        headers = {"X-API-Key": api_key}
        
        # Test different filter combinations
        filter_tests = [
            {"service": "auth-service"},
            {"method": "GET"},
            {"endpoint": "/api/v1/login"},
            {"consumer": "web-app"},
            {"interval": "1hour"},
            {"service": "auth-service", "method": "POST"},
        ]

        for i, filters in enumerate(filter_tests):
            try:
                response = self.session.get(METRICS_AGGREGATE_ENDPOINT, headers=headers, params=filters)

                if response.status_code == 200:
                    data = response.json()
                    is_valid, msg = self.validate_dashboard_response(data)
                    
                    if is_valid:
                        total_requests = data['system_overview']['total_requests']
                        self.log_test(
                            f"Metrics filters aggregate {i+1}",
                            True,
                            f"Retrieved dashboard with filters: {total_requests} requests"
                        )
                    else:
                        self.log_test(
                            f"Metrics filters aggregate {i+1}",
                            False,
                            f"Invalid response structure: {msg}"
                        )
                else:
                    self.log_test(
                        f"Metrics filters aggregate {i+1}",
                        False,
                        f"Status {response.status_code}: {response.text}"
                    )

            except Exception as e:
                self.log_test(f"Metrics filters aggregate {i+1}", False, f"Exception: {str(e)}")
    
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
            {"start_time": one_hour_ago.isoformat()},
            {"end_time": now.isoformat()},
            {"start_time": one_day_ago.isoformat(), "end_time": now.isoformat()},
        ]

        for i, time_filters in enumerate(time_tests):
            try:
                response = self.session.get(METRICS_AGGREGATE_ENDPOINT, headers=headers, params=time_filters)

                if response.status_code == 200:
                    data = response.json()
                    is_valid, msg = self.validate_dashboard_response(data)
                    
                    if is_valid:
                        time_buckets = len(data['time_series'])
                        self.log_test(
                            f"Time range aggregate {i+1}",
                            True,
                            f"Retrieved {time_buckets} time buckets with time filters"
                        )
                    else:
                        self.log_test(
                            f"Time range aggregate {i+1}",
                            False,
                            f"Invalid response structure: {msg}"
                        )
                else:
                    self.log_test(
                        f"Time range aggregate {i+1}",
                        False,
                        f"Status {response.status_code}: {response.text}"
                    )

            except Exception as e:
                self.log_test(f"Time range aggregate {i+1}", False, f"Exception: {str(e)}")
    
    def test_invalid_parameters(self):
        """Test metrics endpoints with invalid parameters"""
        print("\n🔍 Testing invalid parameters...")
        
        # Use the first valid user API key
        api_key = list(VALID_USER_API_KEYS.values())[0]
        headers = {"X-API-Key": api_key}
        
        # Test invalid parameters
        invalid_params = [
            {"interval": "invalid"},  # Invalid interval
        ]

        for i, params in enumerate(invalid_params):
            try:
                response = self.session.get(METRICS_AGGREGATE_ENDPOINT, headers=headers, params=params)

                # Invalid interval should return 422
                if response.status_code == 422:
                    self.log_test(
                        f"Invalid params aggregate {i+1}",
                        True,
                        f"Correctly rejected invalid parameters with 422 status"
                    )
                else:
                    self.log_test(
                        f"Invalid params aggregate {i+1}",
                        False,
                        f"Expected 422, got {response.status_code}: {response.text}"
                    )

            except Exception as e:
                self.log_test(f"Invalid params aggregate {i+1}", False, f"Exception: {str(e)}")

    def test_realtime_endpoint(self):
        """Test the realtime metrics endpoint"""
        print("\n🔍 Testing realtime metrics endpoint...")
        
        # Use the first valid user API key
        api_key = list(VALID_USER_API_KEYS.values())[0]
        headers = {"X-API-Key": api_key}
        
        # Test basic realtime request
        try:
            response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                is_valid, msg = self.validate_dashboard_response(data)
                
                if is_valid:
                    time_buckets = len(data['time_series'])
                    total_requests = data['system_overview']['total_requests']
                    self.log_test(
                        "Realtime endpoint basic", 
                        True, 
                        f"Retrieved realtime dashboard: {total_requests} requests, {time_buckets} 1-min buckets"
                    )
                else:
                    self.log_test(
                        "Realtime endpoint basic", 
                        False, 
                        f"Invalid response structure: {msg}"
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
            "end_time": now.isoformat()
        }
        
        try:
            response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                is_valid, msg = self.validate_dashboard_response(data)
                
                if is_valid:
                    time_buckets = len(data['time_series'])
                    self.log_test(
                        "Realtime endpoint with time range", 
                        True, 
                        f"Retrieved {time_buckets} buckets for 30-minute window"
                    )
                else:
                    self.log_test(
                        "Realtime endpoint with time range", 
                        False, 
                        f"Invalid response structure: {msg}"
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
            "service": "auth-service"
        }
        
        try:
            response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers, params=filter_params)
            
            if response.status_code == 200:
                data = response.json()
                is_valid, msg = self.validate_dashboard_response(data)
                
                if is_valid:
                    total_requests = data['system_overview']['total_requests']
                    self.log_test(
                        "Realtime endpoint with service filter", 
                        True, 
                        f"Retrieved filtered realtime: {total_requests} requests"
                    )
                else:
                    self.log_test(
                        "Realtime endpoint with service filter", 
                        False, 
                        f"Invalid response structure: {msg}"
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
            "end_time": now.isoformat()
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
            "end_time": now.isoformat()
        }
        
        try:
            response = self.session.get(METRICS_REALTIME_ENDPOINT, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                is_valid, msg = self.validate_dashboard_response(data)
                
                if is_valid:
                    time_buckets = len(data['time_series'])
                    self.log_test(
                        "Realtime endpoint valid 60min range", 
                        True, 
                        f"Accepted 60-minute range, retrieved {time_buckets} buckets"
                    )
                else:
                    self.log_test(
                        "Realtime endpoint valid 60min range", 
                        False, 
                        f"Invalid response structure: {msg}"
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
