"""
Authentication dependency module to avoid circular imports.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, Header
from app.services.auth_service import AuthService

# Global auth service instance
_auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    """Get the global auth service instance"""
    global _auth_service
    if _auth_service is None:
        raise RuntimeError("Auth service not initialized. Make sure the application has started properly.")
    return _auth_service

def set_auth_service(auth_service: AuthService) -> None:
    """Set the global auth service instance"""
    global _auth_service
    _auth_service = auth_service

async def authenticate_service_endpoint(x_api_key: Optional[str] = Header(None)) -> str:
    """Authenticate service for ingest endpoint"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    auth_service = get_auth_service()
    auth_info = auth_service.validate_api_key(x_api_key)
    
    if not auth_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if auth_info['type'] != 'service':
        raise HTTPException(status_code=403, detail="Service API key required for ingest endpoint")
    
    if 'ingest' not in auth_info['permissions']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return auth_info['name']

async def authenticate_user_endpoint(x_api_key: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Authenticate user for metrics endpoints"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    auth_service = get_auth_service()
    auth_info = auth_service.validate_api_key(x_api_key)
    
    if not auth_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if auth_info['type'] != 'user':
        raise HTTPException(status_code=403, detail="User API key required for metrics endpoints")
    
    if 'metrics' not in auth_info['permissions']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return auth_info