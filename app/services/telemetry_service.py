from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models.telemetry import TelemetryRequest
from typing import List
from datetime import datetime, timezone

class TelemetryService:
    """Service for handling telemetry data operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def store_batch(self, requests: List[TelemetryRequest]) -> int:
        """Store a batch of telemetry requests"""
        if not requests:
            return 0
        
        # Prepare batch insert data
        batch_data = []
        for req in requests:
            batch_data.append({
                'service': req.service,
                'node': req.node,
                'method': req.method,
                'created_at': req.created_at or datetime.now(timezone.utc),
                'endpoint': req.endpoint,
                'status': req.status,
                'response_time': req.response_time,
                'consumer': req.consumer,
                'context': req.context
            })
        
        # Use raw SQL for efficient batch insert
        insert_query = text("""
            INSERT INTO requests (service, node, method, created_at, endpoint, status, response_time, consumer, context)
            VALUES (:service, :node, :method, :created_at, :endpoint, :status, :response_time, :consumer, :context)
        """)
        
        try:
            await self.db.execute(insert_query, batch_data)
            await self.db.commit()
            return len(batch_data)
        except Exception as e:
            await self.db.rollback()
            raise e