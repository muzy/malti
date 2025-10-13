from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.telemetry import MetricsQuery, DashboardMetricsResponse
from app.services.metrics_service import MetricsService
from app.core.auth_dependency import authenticate_user_endpoint
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter()

@router.get("/metrics/aggregate", response_model=DashboardMetricsResponse)
async def get_aggregated_metrics(
    service: Optional[str] = Query(None, description="Filter by service"),
    node: Optional[str] = Query(None, description="Filter by node"),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    consumer: Optional[str] = Query(None, description="Filter by consumer"),
    context: Optional[str] = Query(None, description="Filter by context"),
    start_time: Optional[datetime] = Query(None, description="Start time for query"),
    end_time: Optional[datetime] = Query(None, description="End time for query"),
    interval: str = Query("5min", description="Aggregation interval (5min, 1hour)"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(authenticate_user_endpoint)
):
    """
    Get aggregated dashboard metrics with server-side calculations.
    Returns structured data for all dashboard components.
    Requires API key authentication via X-API-Key header.
    """
    
    try:
        query = MetricsQuery(
            service=service,
            node=node,
            method=method,
            endpoint=endpoint,
            consumer=consumer,
            context=context,
            start_time=start_time,
            end_time=end_time,
            interval=interval
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    metrics_service = MetricsService(db)
    try:
        results = await metrics_service.get_dashboard_metrics(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")

@router.get("/metrics/aggregate/realtime", response_model=DashboardMetricsResponse)
async def get_realtime_aggregated_metrics(
    service: Optional[str] = Query(None, description="Filter by service"),
    node: Optional[str] = Query(None, description="Filter by node"),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    consumer: Optional[str] = Query(None, description="Filter by consumer"),
    context: Optional[str] = Query(None, description="Filter by context"),
    start_time: Optional[datetime] = Query(None, description="Start time for query (max 60 minutes ago)"),
    end_time: Optional[datetime] = Query(None, description="End time for query (max 60 minutes range)"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(authenticate_user_endpoint)
):
    """
    Get real-time aggregated metrics with 1-minute resolution.
    Time range is limited to 60 minutes maximum.
    Returns structured data for all dashboard components.
    Requires API key authentication via X-API-Key header.
    """

    try:
        query = MetricsQuery(
            service=service,
            node=node,
            method=method,
            endpoint=endpoint,
            consumer=consumer,
            context=context,
            start_time=start_time,
            end_time=end_time,
            interval="1min"  # Force 1-minute intervals for real-time
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Validate time range doesn't exceed 60 minutes
    if query.start_time and query.end_time:
        from datetime import timedelta
        time_range = query.end_time - query.start_time
        max_range = timedelta(minutes=60)
        
        if time_range > max_range:
            raise HTTPException(
                status_code=422, 
                detail="Time range cannot exceed 60 minutes for real-time metrics"
            )

    metrics_service = MetricsService(db)
    try:
        results = await metrics_service.get_dashboard_metrics(query)
        return results
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch real-time metrics: {str(e)}")
