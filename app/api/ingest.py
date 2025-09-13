from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.telemetry import TelemetryBatch, TelemetryRequest
from app.services.telemetry_service import TelemetryService
from app.core.auth_dependency import authenticate_service_endpoint
from typing import Optional

router = APIRouter()

@router.post("/ingest")
async def ingest_telemetry(
    batch: TelemetryBatch,
    service_name: str = Depends(authenticate_service_endpoint),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest telemetry data from worker nodes.
    Requires service API key authentication.
    Only services can use this endpoint.
    """
    # Validate that batch is not empty
    if not batch.requests:
        raise HTTPException(
            status_code=400, 
            detail="Empty requests array is not allowed"
        )
    
    # Validate that all requests belong to the authenticated service
    # Sanitize the service_name for comparison since request.service is sanitized
    sanitized_service_name = TelemetryRequest.sanitize_string(service_name)
    for request in batch.requests:
        if request.service != sanitized_service_name:
            raise HTTPException(
                status_code=403,
                detail=f"Service mismatch: expected {sanitized_service_name}, got {request.service}"
            )
    
    # Store telemetry data
    telemetry_service = TelemetryService(db)
    try:
        result = await telemetry_service.store_batch(batch.requests)
        return {
            "message": "Telemetry data ingested successfully",
            "count": len(batch.requests),
            "service": service_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store telemetry: {str(e)}")