# Malti API Test Suite

This directory contains a comprehensive test suite for the Malti telemetry API.

## Test Structure

- `test_config.py` - Configuration and test data
- `test_health.py` - Health and basic endpoint tests
- `test_ingest.py` - Ingestion endpoint tests
- `test_metrics.py` - Metrics query endpoint tests
- `run_tests.py` - Main test runner

## Prerequisites

1. **Malti server must be running** on `http://localhost:8000`
2. **TimescaleDB must be running** and accessible
3. **Python requests library** (usually included in Python 3)

## Running Tests

### Run all tests:
```bash
cd /home/muzy/dev/malti
python test/run_tests.py
```

### Run individual test modules:
```bash
# Health tests only
python -c "from test.test_health import TestHealthEndpoints; TestHealthEndpoints().run_all_tests()"

# Ingest tests only  
python -c "from test.test_ingest import TestIngestEndpoint; TestIngestEndpoint().run_all_tests()"

# Metrics tests only
python -c "from test.test_metrics import TestMetricsEndpoints; TestMetricsEndpoints().run_all_tests()"
```

## Test Coverage

### Health Endpoints
- ✅ `/health` endpoint returns healthy status
- ✅ `/` root endpoint returns API info or dashboard
- ✅ `/docs` API documentation is accessible

### Ingestion Endpoint (`/api/v1/ingest`)
- ✅ Valid service API keys can ingest data
- ✅ Invalid API keys are rejected (401)
- ✅ User API keys are rejected for ingest (403)
- ✅ Service mismatch validation (services can only send their own data)
- ✅ Missing API key handling (401)
- ✅ Invalid payload validation (400/422)

### Metrics Endpoints (`/api/v1/metrics/*`)
- ✅ Valid user API keys can query metrics
- ✅ Invalid API keys are rejected (401)
- ✅ Service API keys are rejected for metrics (403)
- ✅ Missing API key handling (401)
- ✅ Filter parameters work correctly
- ✅ Time range filters work correctly
- ✅ Invalid parameters are handled gracefully

### Sample Telemetry Data:
The tests use realistic sample data including:
- Various HTTP methods (GET, POST)
- Different endpoints (`/api/v1/login`, `/api/v1/charge`, etc.)
- Different status codes (200, 401)
- Various response times
- Different consumers (`web-app`, `mobile-app`)

## Expected Results

When all tests pass, you should see:
```
🎉 ALL TESTS PASSED! 🎉
The Malti API is working correctly!
```

If tests fail, the output will show which specific tests failed and why.

## Troubleshooting

1. **"Connection refused" errors**: Make sure the Malti server is running
2. **"Database connection failed"**: Make sure TimescaleDB is running
3. **Authentication errors**: Check that the config file is properly loaded
4. **Import errors**: Make sure you're running from the project root directory