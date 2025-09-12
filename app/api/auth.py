from fastapi import APIRouter, Depends, Request
from app.core.auth_dependency import authenticate_user_endpoint, get_auth_service
from app.core.rate_limiting import auth_test_rate_limit
from typing import Dict, Any
from datetime import datetime, timezone

router = APIRouter()

@router.get("/auth/test")
@auth_test_rate_limit()
async def test_user_auth(
    request: Request,
    current_user: Dict[str, Any] = Depends(authenticate_user_endpoint)
):
    """
    Test user authentication and return user information.
    This endpoint is rate limited to 10 requests per minute per IP.
    Useful for UI components to validate API keys and get user context.
    """
    return {
        "authenticated": True,
        "user": {
            "name": current_user["name"],
            "type": current_user["type"],
            "permissions": current_user["permissions"]
        },
        "thresholds": get_auth_service().get_dashboard_thresholds(),
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "rate_limit_info": {
            "endpoint": "auth_test",
            "limit": "10/minute",
            "description": "Rate limited to prevent abuse of authentication testing"
        }
    }
