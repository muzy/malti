"""
Test configuration and constants
"""
import os
import toml
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
API_V1_PREFIX = "/api/v1"

def load_config():
    """Load configuration from malti.toml file"""
    config_path = Path(__file__).parent.parent / "config" / "malti.toml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = toml.load(f)
    
    return config

def get_valid_service_api_keys():
    """Get valid service API keys from config"""
    config = load_config()
    services = config.get('services', {})
    
    service_keys = {}
    for service_name, service_config in services.items():
        api_key = service_config.get('api_key')
        if api_key:
            service_keys[service_name] = api_key
    
    return service_keys

def get_valid_user_api_keys():
    """Get valid user API keys from config"""
    config = load_config()
    users = config.get('users', {})
    
    user_keys = {}
    for username, user_config in users.items():
        api_key = user_config.get('api_key')
        if api_key:
            user_keys[username] = api_key
    
    return user_keys

def get_api_config():
    """Get API configuration from config"""
    config = load_config()
    api_config = config.get('api', {})
    
    return {
        'base_url': api_config.get('base_url', BASE_URL),
        'ingest_endpoint': api_config.get('ingest_endpoint', '/api/v1/ingest'),
        'metrics_endpoint': api_config.get('metrics_endpoint', '/api/v1/metrics')
    }

# Load actual configuration values with error handling
try:
    VALID_SERVICE_API_KEYS = get_valid_service_api_keys()
    VALID_USER_API_KEYS = get_valid_user_api_keys()
    API_CONFIG = get_api_config()
except Exception as e:
    print(f"⚠️  Warning: Could not load config from malti.toml: {e}")
    print("Using fallback configuration...")
    
    # Fallback configuration
    VALID_SERVICE_API_KEYS = {
        "auth-service": "auth-service-key-12345",
        "payment-service": "payment-service-key-67890", 
        "user-service": "user-service-key-abcde"
    }
    VALID_USER_API_KEYS = {
        "viewer": "viewer-api-key-67890",
        "analyst": "analyst-api-key-abcde"
    }
    API_CONFIG = {
        'base_url': BASE_URL,
        'ingest_endpoint': '/api/v1/ingest',
        'metrics_endpoint': '/api/v1/metrics'
    }

# Use config values or fallback to defaults
BASE_URL = API_CONFIG['base_url']
INGEST_PATH = API_CONFIG['ingest_endpoint']
METRICS_PATH = API_CONFIG['metrics_endpoint']

# Invalid API keys for testing
INVALID_API_KEYS = [
    "invalid-key-12345",
    "wrong-service-key",
    "expired-key-xyz",
    "",
    None
]

# Generate test data based on actual services in config
def generate_sample_telemetry_data():
    """Generate sample telemetry data based on actual services in config"""
    from datetime import datetime, timezone
    
    sample_data = []
    now = datetime.now(timezone.utc)
    
    # Context values only for specific meaningful endpoints
    service_contexts = {
        "auth-service": {
            "/api/v1/auth/login": "password",
            "/api/v1/auth/register": "email"
        },
        "payment-service": {
            "/api/v1/payments/process": "card",
            "/api/v1/payments/history": "recent"
        },
        "user-service": {
            "/api/v1/users/search": "simple",
            "/api/v1/users/profile": "basic"
        }
    }

    # Create sample data for each service in the config
    for service_name in VALID_SERVICE_API_KEYS.keys():
        context_map = service_contexts.get(service_name, {})

        # First entry - POST action (may have context if it's a meaningful endpoint)
        post_entry = {
            "service": service_name,
            "node": f"{service_name}-node-1",
            "method": "POST",
            "endpoint": f"/api/v1/{service_name}/action",
            "status": 200,
            "response_time": 150,
            "consumer": "web-app",
            "created_at": now.isoformat()
        }

        # Add context only if this is a meaningful endpoint
        if f"/api/v1/{service_name}/action" in context_map:
            post_entry["context"] = context_map[f"/api/v1/{service_name}/action"]

        # Second entry - GET status (no context for basic status checks)
        get_entry = {
            "service": service_name,
            "node": f"{service_name}-node-1",
            "method": "GET",
            "endpoint": f"/api/v1/{service_name}/status",
            "status": 200,
            "response_time": 75,
            "consumer": "mobile-app",
            "created_at": now.isoformat()
        }

        sample_data.extend([post_entry, get_entry])
    
    return sample_data

# Test data
SAMPLE_TELEMETRY_DATA = generate_sample_telemetry_data()

# Endpoints
INGEST_ENDPOINT = f"{BASE_URL}{INGEST_PATH}"
METRICS_AGGREGATE_ENDPOINT = f"{BASE_URL}{METRICS_PATH}/aggregate"
METRICS_REALTIME_ENDPOINT = f"{BASE_URL}{METRICS_PATH}/aggregate/realtime"
HEALTH_ENDPOINT = f"{BASE_URL}/health"
ROOT_ENDPOINT = f"{BASE_URL}/"

# Print loaded configuration for verification
def print_loaded_config():
    """Print the loaded configuration for verification"""
    print("📋 Loaded Test Configuration:")
    print(f"  Base URL: {BASE_URL}")
    print(f"  Services: {list(VALID_SERVICE_API_KEYS.keys())}")
    print(f"  Users: {list(VALID_USER_API_KEYS.keys())}")
    print(f"  Sample data entries: {len(SAMPLE_TELEMETRY_DATA)}")
    print(f"  Ingest endpoint: {INGEST_ENDPOINT}")
    print(f"  Metrics aggregate endpoint: {METRICS_AGGREGATE_ENDPOINT}")
    print(f"  Metrics realtime endpoint: {METRICS_REALTIME_ENDPOINT}")