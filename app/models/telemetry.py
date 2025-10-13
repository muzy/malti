from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import datetime
import nh3

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

        # Convert to string and sanitize with nh3
        # nh3.clean() with empty tags and attributes removes all HTML tags and attributes
        sanitized = nh3.clean(str(v))

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

class TimeSeriesDataPoint(BaseModel):
    """Single time series data point for charting"""
    bucket: datetime
    total_requests: int
    min_latency: Optional[float] = None
    avg_latency: Optional[float] = None
    p95_latency: Optional[float] = None
    max_latency: Optional[float] = None

class MetricsCardsSummary(BaseModel):
    """Summary metrics for dashboard cards"""
    total_requests: int
    avg_latency: Optional[float] = None
    min_latency: Optional[float] = None
    p95_latency: Optional[float] = None
    max_latency: Optional[float] = None

class EndpointAggregation(BaseModel):
    """Aggregated metrics per endpoint"""
    endpoint: str
    method: str
    service: str
    total_requests: int
    error_count: int
    error_rate: float

class StatusDistribution(BaseModel):
    """Status code distribution per service"""
    service: str
    total_requests: int
    success_2xx: int
    warning_3xx: int
    error_4xx_5xx: int
    status_breakdown: Dict[int, int]

class ConsumerAggregation(BaseModel):
    """Aggregated metrics per consumer"""
    consumer: str
    total_requests: int
    error_count: int
    error_rate: float

class SystemOverview(BaseModel):
    """System-wide overview metrics"""
    total_requests: int
    total_errors: int
    error_rate: float
    avg_latency: Optional[float] = None

class DashboardMetricsResponse(BaseModel):
    """Complete dashboard metrics response"""
    time_series: List[TimeSeriesDataPoint]
    metrics_summary: MetricsCardsSummary
    endpoints: List[EndpointAggregation]
    status_distribution: List[StatusDistribution]
    consumers: List[ConsumerAggregation]
    system_overview: SystemOverview
    distinct_nodes: List[str] = Field(default_factory=list, description="List of distinct nodes for filtering")
    distinct_contexts: List[str] = Field(default_factory=list, description="List of distinct contexts for filtering")