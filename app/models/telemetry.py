from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

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

    
    @validator('interval')
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