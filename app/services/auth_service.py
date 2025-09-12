import toml
import os
import time
from typing import Optional, Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication with in-memory user and service management"""
    
    def __init__(self):
        self.config_path = settings.malti_config_path
        self.config_mtime = 0
        self.last_config_check = 0
        self.config_check_interval = 30  # Check config file every 30 seconds
        self.services: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.api_key_to_service: Dict[str, str] = {}
        self.api_key_to_user: Dict[str, Dict[str, Any]] = {}
        self.dashboard_thresholds: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from TOML file and build in-memory lookup tables"""
        try:
            # Check if config file exists and get modification time
            if not os.path.exists(self.config_path):
                logger.error(f"Config file not found: {self.config_path}")
                return
            
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime == self.config_mtime:
                return  # Config hasn't changed
            
            # Load config
            with open(self.config_path, 'r') as f:
                config = toml.load(f)
            
            # Clear existing data
            self.services.clear()
            self.users.clear()
            self.api_key_to_service.clear()
            self.api_key_to_user.clear()
            self.dashboard_thresholds.clear()
            
            # Load services
            services_config = config.get('services', {})
            for service_name, service_config in services_config.items():
                api_key = service_config.get('api_key')
                if api_key:
                    self.services[service_name] = {
                        'api_key': api_key,
                        'description': service_config.get('description', '')
                    }
                    self.api_key_to_service[api_key] = service_name
            
            # Load users
            users_config = config.get('users', {})
            for username, user_config in users_config.items():
                api_key = user_config.get('api_key')
                if api_key:
                    user_data = {
                        'username': username,
                        'api_key': api_key
                    }
                    self.users[username] = user_data
                    self.api_key_to_user[api_key] = user_data

            # Load dashboard thresholds
            dashboard_config = config.get('dashboard', {})
            thresholds_config = dashboard_config.get('thresholds', {})

            # Load with defaults if not specified
            self.dashboard_thresholds = {
                'error_rate_success_threshold': thresholds_config.get('error_rate_success_threshold', 1.0),
                'error_rate_warning_threshold': thresholds_config.get('error_rate_warning_threshold', 2.0),
                'latency_success_threshold': thresholds_config.get('latency_success_threshold', 300),
                'latency_warning_threshold': thresholds_config.get('latency_warning_threshold', 600)
            }

            self.config_mtime = current_mtime

            logger.info(f"Loaded {len(self.services)} services, {len(self.users)} users, and dashboard thresholds from config")
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    def _check_config_changed(self) -> bool:
        """Check if config file has changed and reload if necessary (with 30-second cache)"""
        current_time = time.time()
        
        # Only check config file every 30 seconds to reduce disk I/O
        if current_time - self.last_config_check < self.config_check_interval:
            return False
        
        self.last_config_check = current_time
        
        try:
            if not os.path.exists(self.config_path):
                return False
            
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime != self.config_mtime:
                logger.info("Config file changed, reloading...")
                self._load_config()
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking config file: {e}")
            return False
    
    async def authenticate_service(self, api_key: str) -> Optional[str]:
        """Authenticate a service by API key"""
        self._check_config_changed()
        
        if api_key in self.api_key_to_service:
            service_name = self.api_key_to_service[api_key]
            logger.debug(f"Service authenticated: {service_name}")
            return service_name
        
        logger.warning(f"Invalid service API key: {api_key[:10]}...")
        return None
    
    async def authenticate_user_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user by API key"""
        self._check_config_changed()
        
        if api_key in self.api_key_to_user:
            user_data = self.api_key_to_user[api_key]
            logger.debug(f"User authenticated: {user_data['username']}")
            return user_data
        
        logger.warning(f"Invalid user API key: {api_key[:10]}...")
        return None
    
    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service information by name"""
        return self.services.get(service_name)
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username"""
        return self.users.get(username)

    def get_dashboard_thresholds(self) -> Dict[str, Any]:
        """Get dashboard thresholds for visual indicators"""
        self._check_config_changed()
        return self.dashboard_thresholds.copy()
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return authentication info"""
        self._check_config_changed()
        
        # Check if it's a service API key
        if api_key in self.api_key_to_service:
            service_name = self.api_key_to_service[api_key]
            return {
                'type': 'service',
                'name': service_name,
                'permissions': ['ingest']
            }
        
        # Check if it's a user API key
        if api_key in self.api_key_to_user:
            user_data = self.api_key_to_user[api_key]
            return {
                'type': 'user',
                'name': user_data['username'],
                'permissions': ['metrics']
            }
        
        return None