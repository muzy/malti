"""
Test suite for the ingestion endpoint
"""
import requests
import json
import random
import time
from datetime import datetime, timezone, timedelta
from test_config import (
    INGEST_ENDPOINT, 
    VALID_SERVICE_API_KEYS, 
    VALID_USER_API_KEYS,
    INVALID_API_KEYS,
    SAMPLE_TELEMETRY_DATA
)

class TestIngestEndpoint:
    """Test cases for the /api/v1/ingest endpoint"""
    
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
    
    def test_valid_service_ingest(self):
        """Test ingestion with valid service API keys"""
        print("\n🔍 Testing valid service ingestion...")
        
        for service_name, api_key in VALID_SERVICE_API_KEYS.items():
            # Filter data for this service
            service_data = [req for req in SAMPLE_TELEMETRY_DATA if req["service"] == service_name]
            
            if not service_data:
                # Create sample data for this service (no context for basic test endpoint)
                service_data = [{
                    "service": service_name,
                    "node": "test-node",
                    "method": "GET",
                    "endpoint": "/api/v1/test",
                    "status": 200,
                    "response_time": 100,
                    "consumer": "test-consumer",
                    "created_at": datetime.utcnow().isoformat()
                }]
            
            payload = {"requests": service_data}
            headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
            
            try:
                response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_test(
                        f"Valid {service_name} ingest", 
                        True, 
                        f"Stored {result.get('count', 0)} records"
                    )
                else:
                    self.log_test(
                        f"Valid {service_name} ingest", 
                        False, 
                        f"Status {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Valid {service_name} ingest", False, f"Exception: {str(e)}")
    
    def test_invalid_api_key_ingest(self):
        """Test ingestion with invalid API keys"""
        print("\n🔍 Testing invalid API key ingestion...")
        
        # Use sample data for auth-service
        payload = {"requests": [SAMPLE_TELEMETRY_DATA[0]]}
        
        for invalid_key in INVALID_API_KEYS:
            headers = {"Content-Type": "application/json"}
            if invalid_key is not None:
                headers["X-API-Key"] = invalid_key
            
            try:
                response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
                
                if response.status_code == 401:
                    self.log_test(f"Invalid API key '{invalid_key}'", True, "Correctly rejected")
                else:
                    self.log_test(
                        f"Invalid API key '{invalid_key}'", 
                        False, 
                        f"Expected 401, got {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Invalid API key '{invalid_key}'", False, f"Exception: {str(e)}")
    
    def test_user_api_key_ingest(self):
        """Test that user API keys are rejected for ingest endpoint"""
        print("\n🔍 Testing user API key rejection for ingest...")
        
        payload = {"requests": [SAMPLE_TELEMETRY_DATA[0]]}
        
        for username, api_key in VALID_USER_API_KEYS.items():
            headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
            
            try:
                response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
                
                if response.status_code == 403:
                    self.log_test(f"User API key '{username}' rejected", True, "Correctly rejected")
                else:
                    self.log_test(
                        f"User API key '{username}' rejected", 
                        False, 
                        f"Expected 403, got {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"User API key '{username}' rejected", False, f"Exception: {str(e)}")
    
    def test_service_mismatch(self):
        """Test that services can only send data for themselves"""
        print("\n🔍 Testing service mismatch validation...")
        
        # Try to send payment-service data with auth-service API key
        auth_service_key = VALID_SERVICE_API_KEYS["auth-service"]
        payment_service_data = [req for req in SAMPLE_TELEMETRY_DATA if req["service"] == "payment-service"][0]
        
        payload = {"requests": [payment_service_data]}
        headers = {"X-API-Key": auth_service_key, "Content-Type": "application/json"}
        
        try:
            response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
            
            if response.status_code == 403:
                self.log_test("Service mismatch validation", True, "Correctly rejected cross-service data")
            else:
                self.log_test(
                    "Service mismatch validation", 
                    False, 
                    f"Expected 403, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Service mismatch validation", False, f"Exception: {str(e)}")
    
    def test_missing_api_key(self):
        """Test ingestion without API key"""
        print("\n🔍 Testing missing API key...")
        
        payload = {"requests": [SAMPLE_TELEMETRY_DATA[0]]}
        headers = {"Content-Type": "application/json"}
        
        try:
            response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
            
            if response.status_code == 401:
                self.log_test("Missing API key", True, "Correctly rejected")
            else:
                self.log_test(
                    "Missing API key", 
                    False, 
                    f"Expected 401, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Missing API key", False, f"Exception: {str(e)}")
    
    def test_invalid_payload(self):
        """Test ingestion with invalid payload"""
        print("\n🔍 Testing invalid payload...")
        
        auth_service_key = VALID_SERVICE_API_KEYS["auth-service"]
        headers = {"X-API-Key": auth_service_key, "Content-Type": "application/json"}
        
        # Test cases for invalid payloads
        invalid_payloads = [
            {},  # Empty payload
            {"requests": []},  # Empty requests array
            {"requests": [{"invalid": "data"}]},  # Invalid request structure
            {"not_requests": [SAMPLE_TELEMETRY_DATA[0]]},  # Wrong key
        ]
        
        for i, payload in enumerate(invalid_payloads):
            try:
                response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
                
                if response.status_code in [400, 422]:  # Bad request or validation error
                    self.log_test(f"Invalid payload {i+1}", True, "Correctly rejected")
                else:
                    self.log_test(
                        f"Invalid payload {i+1}", 
                        False, 
                        f"Expected 400/422, got {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Invalid payload {i+1}", False, f"Exception: {str(e)}")
    
    def generate_large_batch_data(self, service_name: str, batch_size: int = 500):
        """Generate a large batch of realistic telemetry data"""
        print(f"📊 Generating {batch_size} entries for {service_name}...")
        
        # Realistic endpoints for different services with method-appropriate endpoints and contexts
        service_endpoints = {
            "auth-service": {
                "GET": ["/api/v1/auth/validate", "/api/v1/auth/status", "/api/v1/auth/session"],
                "POST": ["/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/forgot-password", "/api/v1/auth/verify-email"],
                "PUT": ["/api/v1/auth/change-password", "/api/v1/auth/reset-password"],
                "DELETE": ["/api/v1/auth/logout", "/api/v1/auth/revoke"],
                "PATCH": ["/api/v1/auth/refresh", "/api/v1/auth/update-profile"]
            },
            "payment-service": {
                "GET": ["/api/v1/payments/status", "/api/v1/payments/history", "/api/v1/payments/methods"],
                "POST": ["/api/v1/payments/process", "/api/v1/payments/webhook", "/api/v1/payments/subscribe"],
                "PUT": ["/api/v1/payments/update-method"],
                "DELETE": ["/api/v1/payments/cancel"],
                "PATCH": ["/api/v1/payments/refund", "/api/v1/payments/validate"]
            },
            "user-service": {
                "GET": ["/api/v1/users/profile", "/api/v1/users/search", "/api/v1/users/activity", "/api/v1/users/notifications"],
                "POST": ["/api/v1/users/create", "/api/v1/users/verify"],
                "PUT": ["/api/v1/users/update", "/api/v1/users/preferences"],
                "DELETE": ["/api/v1/users/delete", "/api/v1/users/avatar"],
                "PATCH": ["/api/v1/users/partial-update"]
            }
        }

        # Context values only for operations where it provides value (search, history, etc.)
        service_contexts = {
            "auth-service": {
                "/api/v1/auth/login": ["password", "oauth", "sso"],
                "/api/v1/auth/register": ["email", "social", "invite"],
                "/api/v1/auth/update-profile": ["basic", "extended"],
            },
            "payment-service": {
                "/api/v1/payments/process": ["card", "bank-transfer", "wallet", "crypto"],
                "/api/v1/payments/history": ["recent", "all"],
                "/api/v1/payments/webhook": ["stripe", "paypal", "bank"],
                "/api/v1/payments/subscribe": ["monthly", "yearly", "trial"],
            },
            "user-service": {
                "/api/v1/users/search": ["simple", "extended", "advanced"],
                "/api/v1/users/profile": ["basic", "extended", "public"],
                "/api/v1/users/activity": ["recent", "all", "summary"],
                "/api/v1/users/notifications": ["unread", "all", "settings"],
                "/api/v1/users/create": ["basic", "premium", "admin"],
            }
        }

        # Operations that should have context (search, history, profile, etc.)
        context_enabled_endpoints = {
            "auth-service": ["/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/update-profile"],
            "payment-service": ["/api/v1/payments/process", "/api/v1/payments/history", "/api/v1/payments/webhook", "/api/v1/payments/subscribe"],
            "user-service": ["/api/v1/users/search", "/api/v1/users/profile", "/api/v1/users/activity", "/api/v1/users/notifications", "/api/v1/users/create"]
        }
        
        # Realistic HTTP methods with weighted distribution
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        method_weights = [0.4, 0.3, 0.15, 0.08, 0.05, 0.01, 0.01]  # GET and POST are most common
        
        # Realistic status codes with weights
        status_codes = [200, 201, 400, 401, 403, 404, 422, 500, 502, 503]
        status_weights = [0.6, 0.1, 0.05, 0.05, 0.02, 0.05, 0.03, 0.02, 0.01, 0.01]
        
        # Realistic response times (in milliseconds)
        response_times = [50, 100, 150, 200, 300, 500, 1000, 2000, 5000]
        response_weights = [0.3, 0.25, 0.2, 0.1, 0.08, 0.04, 0.02, 0.005, 0.005]
        
        # Realistic consumers
        consumers = ["web-app", "mobile-app", "api-client", "admin-panel", "webhook", "cron-job"]
        
        # Realistic node names
        nodes = [f"{service_name}-node-{i}" for i in range(1, 6)]
        
        # Get service endpoints
        service_endpoint_map = service_endpoints.get(service_name, {
            "GET": [f"/api/v1/{service_name}/status"],
            "POST": [f"/api/v1/{service_name}/action"],
            "PUT": [f"/api/v1/{service_name}/update"],
            "DELETE": [f"/api/v1/{service_name}/delete"],
            "PATCH": [f"/api/v1/{service_name}/patch"]
        })

        # Get service contexts and enabled endpoints
        service_context_map = service_contexts.get(service_name, {})
        enabled_endpoints = context_enabled_endpoints.get(service_name, [])

        batch_data = []
        base_time = datetime.now(timezone.utc)

        for i in range(batch_size):
            # Generate random timestamp within the last hour
            random_minutes = random.randint(0, 60)
            created_at = base_time - timedelta(minutes=random_minutes)

            # Select method first, then appropriate endpoint
            method = random.choices(methods, weights=method_weights)[0]
            available_endpoints = service_endpoint_map.get(method, [f"/api/v1/{service_name}/action"])
            endpoint = random.choice(available_endpoints)

            # Determine if this endpoint should have context
            should_have_context = endpoint in enabled_endpoints

            # Generate context only for enabled endpoints
            if should_have_context:
                available_contexts = service_context_map.get(endpoint, ["default"])
                context = random.choice(available_contexts)

                # Context-based response time multipliers
                context_multipliers = {
                    # User service contexts
                    "extended": 2.5,  # Extended searches take longer
                    "advanced": 3.0,  # Advanced operations take even longer
                    "all": 1.8,       # Full data retrieval takes longer
                    "detailed": 1.5,  # Detailed info takes longer

                    # Payment service contexts
                    "crypto": 2.2,    # Crypto payments can be slower
                    "bank-transfer": 1.7,  # Bank transfers take longer
                    "yearly": 1.3,    # Yearly subscriptions might have more processing

                    # Auth service contexts
                    "social": 1.6,    # Social auth might involve external calls
                    "oauth": 1.4,     # OAuth flows can be more complex
                    "sso": 1.5,       # SSO might have additional validation

                    # Default multiplier for other contexts
                    "default": 1.0
                }

                multiplier = context_multipliers.get(context, 1.0)
                adjusted_response_time = int(random.choices(response_times, weights=response_weights)[0] * multiplier)

                # Select status - some contexts might have different success rates
                status_weights_adjusted = status_weights.copy()
                if context in ["extended", "advanced", "crypto"]:
                    # More complex operations might have slightly higher error rates
                    status_weights_adjusted[2] *= 1.5  # Increase 400 error weight
                    status_weights_adjusted[7] *= 1.3  # Increase 500 error weight
            else:
                # No context for this endpoint
                context = None
                adjusted_response_time = random.choices(response_times, weights=response_weights)[0]
                status_weights_adjusted = status_weights

            # Generate realistic data
            entry = {
                "service": service_name,
                "node": random.choice(nodes),
                "method": method,
                "endpoint": endpoint,
                "status": random.choices(status_codes, weights=status_weights_adjusted)[0],
                "response_time": adjusted_response_time,
                "consumer": random.choice(consumers),
                "created_at": created_at.isoformat()
            }

            # Only add context if it should be included
            if should_have_context:
                entry["context"] = context

            batch_data.append(entry)
        
        return batch_data
    
    def test_large_batch_ingestion(self):
        """Test ingestion with large batches (500 entries per batch)"""
        print("\n🔍 Testing large batch ingestion (500 entries per batch)...")
        
        total_ingested = 0
        total_time = 0
        
        for service_name, api_key in VALID_SERVICE_API_KEYS.items():
            print(f"\n📦 Testing {service_name} with large batch...")
            
            # Generate 500 entries for this service
            batch_data = self.generate_large_batch_data(service_name, 500)
            
            payload = {"requests": batch_data}
            headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
            
            try:
                # Measure ingestion time
                start_time = time.time()
                response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
                end_time = time.time()
                
                ingestion_time = end_time - start_time
                total_time += ingestion_time
                
                if response.status_code == 200:
                    result = response.json()
                    ingested_count = result.get('count', 0)
                    total_ingested += ingested_count
                    
                    # Calculate performance metrics
                    entries_per_second = ingested_count / ingestion_time if ingestion_time > 0 else 0
                    
                    self.log_test(
                        f"Large batch {service_name} ingest", 
                        True, 
                        f"Stored {ingested_count}/500 records in {ingestion_time:.2f}s ({entries_per_second:.1f} entries/sec)"
                    )
                    
                    # Verify the count matches expected
                    if ingested_count == 500:
                        self.log_test(f"Large batch {service_name} count verification", True, "All 500 entries stored")
                    else:
                        self.log_test(
                            f"Large batch {service_name} count verification", 
                            False, 
                            f"Expected 500, got {ingested_count}"
                        )
                        
                else:
                    self.log_test(
                        f"Large batch {service_name} ingest", 
                        False, 
                        f"Status {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test(f"Large batch {service_name} ingest", False, f"Exception: {str(e)}")
        
        # Overall performance summary
        if total_ingested > 0:
            overall_entries_per_second = total_ingested / total_time if total_time > 0 else 0
            self.log_test(
                "Large batch performance summary", 
                True, 
                f"Total: {total_ingested} entries in {total_time:.2f}s ({overall_entries_per_second:.1f} entries/sec)"
            )
    
    def test_large_batch_validation(self):
        """Test that large batches are properly validated"""
        print("\n🔍 Testing large batch validation...")
        
        auth_service_key = VALID_SERVICE_API_KEYS["auth-service"]
        headers = {"X-API-Key": auth_service_key, "Content-Type": "application/json"}
        
        # Test 1: Valid large batch should succeed
        print("  Testing valid large batch...")
        valid_batch = self.generate_large_batch_data("auth-service", 500)
        payload = {"requests": valid_batch}
        
        try:
            response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                ingested_count = result.get('count', 0)
                
                if ingested_count == 500:
                    self.log_test("Valid large batch", True, f"Successfully ingested {ingested_count} valid entries")
                else:
                    self.log_test(
                        "Valid large batch", 
                        False, 
                        f"Expected 500 entries, got {ingested_count}"
                    )
            else:
                self.log_test(
                    "Valid large batch", 
                    False, 
                    f"Expected 200, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Valid large batch", False, f"Exception: {str(e)}")
        
        # Test 2: Invalid large batch should be rejected entirely
        print("  Testing invalid large batch rejection...")
        invalid_batch = [
            {"invalid": "data", "service": "auth-service", "context": "invalid"},  # Missing required fields
            {"service": "auth-service", "node": "test", "method": "GET", "endpoint": "/test", "status": "invalid", "response_time": 100, "consumer": "test", "context": "simple", "created_at": "invalid-date"},  # Invalid status and date
            {"service": "auth-service", "node": "test", "method": "INVALID", "endpoint": "/test", "status": 200, "response_time": -100, "consumer": "test", "context": "extended", "created_at": datetime.now(timezone.utc).isoformat()},  # Invalid method and response time
        ]
        
        payload = {"requests": invalid_batch}
        
        try:
            response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
            
            if response.status_code == 422:  # Validation error
                self.log_test("Invalid large batch rejection", True, "Correctly rejected invalid batch with 422 status")
            else:
                self.log_test(
                    "Invalid large batch rejection", 
                    False, 
                    f"Expected 422, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Invalid large batch rejection", False, f"Exception: {str(e)}")
        
        # Test 3: Mixed valid/invalid batch should be rejected entirely
        print("  Testing mixed valid/invalid batch rejection...")
        valid_entries = self.generate_large_batch_data("auth-service", 10)
        invalid_entries = [
            {"invalid": "data", "service": "auth-service", "context": "invalid"},  # Missing required fields
        ]
        mixed_batch = valid_entries + invalid_entries
        payload = {"requests": mixed_batch}
        
        try:
            response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
            
            if response.status_code == 422:  # Validation error
                self.log_test("Mixed batch rejection", True, "Correctly rejected mixed batch with 422 status")
            else:
                self.log_test(
                    "Mixed batch rejection", 
                    False, 
                    f"Expected 422, got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Mixed batch rejection", False, f"Exception: {str(e)}")
    
    def test_concurrent_large_batches(self):
        """Test concurrent ingestion of large batches from different services"""
        print("\n🔍 Testing concurrent large batch ingestion...")
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def ingest_batch(service_name, api_key, batch_size=100):
            """Ingest a batch for a specific service"""
            try:
                batch_data = self.generate_large_batch_data(service_name, batch_size)
                payload = {"requests": batch_data}
                headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
                
                start_time = time.time()
                response = self.session.post(INGEST_ENDPOINT, json=payload, headers=headers)
                end_time = time.time()
                
                results_queue.put({
                    "service": service_name,
                    "status_code": response.status_code,
                    "count": response.json().get('count', 0) if response.status_code == 200 else 0,
                    "time": end_time - start_time,
                    "success": response.status_code == 200
                })
                
            except Exception as e:
                results_queue.put({
                    "service": service_name,
                    "error": str(e),
                    "success": False
                })
        
        # Start concurrent ingestion threads
        threads = []
        for service_name, api_key in VALID_SERVICE_API_KEYS.items():
            thread = threading.Thread(target=ingest_batch, args=(service_name, api_key, 100))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # Analyze results
        successful_services = [r for r in results if r.get("success", False)]
        total_ingested = sum(r.get("count", 0) for r in successful_services)
        total_time = max(r.get("time", 0) for r in successful_services)
        
        if len(successful_services) == len(VALID_SERVICE_API_KEYS):
            entries_per_second = total_ingested / total_time if total_time > 0 else 0
            self.log_test(
                "Concurrent large batch ingestion", 
                True, 
                f"All {len(successful_services)} services successful, {total_ingested} entries in {total_time:.2f}s ({entries_per_second:.1f} entries/sec)"
            )
        else:
            failed_services = [r["service"] for r in results if not r.get("success", False)]
            self.log_test(
                "Concurrent large batch ingestion", 
                False, 
                f"Failed services: {failed_services}"
            )
    
    def run_all_tests(self):
        """Run all ingest endpoint tests"""
        print("🚀 Starting Ingest Endpoint Tests")
        print("=" * 50)
        
        # Basic functionality tests
        self.test_valid_service_ingest()
        self.test_invalid_api_key_ingest()
        self.test_user_api_key_ingest()
        self.test_service_mismatch()
        self.test_missing_api_key()
        self.test_invalid_payload()
        
        # Large batch tests
        self.test_large_batch_ingestion()
        self.test_large_batch_validation()
        self.test_concurrent_large_batches()
        
        # Summary
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"📊 Ingest Tests Summary: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All ingest tests passed!")
        else:
            print("⚠️  Some ingest tests failed!")
            
        return passed == total
    
    def run_large_batch_tests_only(self):
        """Run only the large batch tests for focused testing"""
        print("🚀 Starting Large Batch Ingest Tests")
        print("=" * 50)
        
        self.test_large_batch_ingestion()
        self.test_large_batch_validation()
        self.test_concurrent_large_batches()
        
        # Summary
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"📊 Large Batch Tests Summary: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All large batch tests passed!")
        else:
            print("⚠️  Some large batch tests failed!")
            
        return passed == total