from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
import bleach

class TelemetryRequest(BaseModel):
    """Single telemetry request data"""
    service: str
    node: Optional[str] = None
    method: str
    endpoint: str
    status: int
    response_time: int
    consumer: str
    context: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator('service', 'node', 'method', 'endpoint', 'consumer', 'context', mode='before')
    @classmethod
    def sanitize_field(cls, v):
        """Sanitize fields that may be displayed in the dashboard to prevent XSS attacks"""
        if v is None:
            return v

        # Convert to string and sanitize with bleach
        # bleach.clean() removes all HTML tags and attributes by default
        sanitized = bleach.clean(str(v), tags=[], attributes={}, strip=True)

        # Remove null bytes and other control characters that might cause issues
        sanitized = sanitized.replace('\x00', '').replace('\r', '').replace('\n', ' ')

        # Limit length to prevent DoS attacks (reasonable limit for telemetry fields)
        max_length = 500
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()

class TelemetryBatch(BaseModel):
    """Batch of telemetry requests"""
    requests: List[TelemetryRequest]

class MetricsQuery(BaseModel):
    """Query parameters for metrics"""
    service: Optional[str] = None
    node: Optional[str] = None
    method: Optional[str] = None
    endpoint: Optional[str] = None
    consumer: Optional[str] = None
    context: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    interval: str = "5min"

    
    @field_validator('interval', mode='before')
    @classmethod
    def validate_interval(cls, v):
        """Validate interval parameter"""
        valid_intervals = ['1min', '5min', '1hour']
        if v not in valid_intervals:
            raise ValueError(f'Interval must be one of: {valid_intervals}')
        return v

class AggregatedMetrics(BaseModel):
    """Aggregated metrics response"""
    service: str
    node: Optional[str]
    method: str
    endpoint: str
    consumer: str
    context: Optional[str]
    bucket: datetime
    status: int
    count_requests: int
    min_response_time: float
    max_response_time: float
    avg_response_time: float
    p95_response_time: Optional[float]

class RawMetrics(BaseModel):
    """Raw metrics response"""
    service: str
    node: Optional[str]
    method: str
    endpoint: str
    consumer: str
    context: Optional[str]
    created_at: datetime
    status: int
    response_time: int