"""
Rate limiting utilities for the Malti application.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors"""
    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Rate limit exceeded: {exc.detail}",
            "retry_after": 60  # Default to 60 seconds
        }
    )
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response

# Rate limiting decorators for different use cases
def auth_test_rate_limit():
    """Rate limit for auth test endpoint - 10 requests per minute per IP"""
    return limiter.limit("10/minute")

def general_rate_limit():
    """General rate limit - 100 requests per minute per IP"""
    return limiter.limit("100/minute")

def strict_rate_limit():
    """Strict rate limit - 5 requests per minute per IP"""
    return limiter.limit("5/minute")