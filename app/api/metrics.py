from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.telemetry import MetricsQuery, AggregatedMetrics, RawMetrics
from app.services.metrics_service import MetricsService
from app.core.auth_dependency import authenticate_user_endpoint
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter()

@router.get("/metrics/aggregate", response_model=List[AggregatedMetrics])
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
    Get aggregated metrics data.
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
        results = await metrics_service.get_aggregated_metrics(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")

@router.get("/metrics/raw", response_model=List[RawMetrics])
async def get_raw_metrics(
    service: Optional[str] = Query(None, description="Filter by service"),
    node: Optional[str] = Query(None, description="Filter by node"),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    consumer: Optional[str] = Query(None, description="Filter by consumer"),
    context: Optional[str] = Query(None, description="Filter by context"),
    start_time: Optional[datetime] = Query(None, description="Start time for query"),
    end_time: Optional[datetime] = Query(None, description="End time for query"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(authenticate_user_endpoint)
):
    """
    Get raw metrics data.
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
            end_time=end_time
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    metrics_service = MetricsService(db)
    try:
        results = await metrics_service.get_raw_metrics(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch raw metrics: {str(e)}")

@router.get("/metrics/aggregate/realtime", response_model=List[AggregatedMetrics])
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

    metrics_service = MetricsService(db)
    try:
        results = await metrics_service.get_realtime_aggregated_metrics(query)
        return results
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch real-time metrics: {str(e)}")
