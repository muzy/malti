from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models.telemetry import MetricsQuery, AggregatedMetrics, RawMetrics
from typing import List
from datetime import datetime, timezone, timedelta

class MetricsService:
    """Service for querying metrics data from materialized views"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_aggregated_metrics(self, query: MetricsQuery) -> List[AggregatedMetrics]:
        """Get aggregated metrics from the appropriate materialized view"""
        
        # Determine time range for querying
        now = datetime.now(timezone.utc)
        
        # If no start_time provided, default to 7 days ago for better performance
        if not query.start_time:
            query.start_time = now - timedelta(days=7)
        
        # If no end_time provided, use current time
        if not query.end_time:
            query.end_time = now
        
        # Calculate time range duration
        time_range = query.end_time - query.start_time
        
        # Determine which materialized view to use based on time range and user preference
        # For ranges > 4 days or explicit hourly request: use 1-hour aggregates
        # For ranges <= 4 days with 5min request: use 5-minute aggregates
        use_hourly = (time_range.days > 4) or (query.interval == "1hour")
        
        if use_hourly:
            table_name = "requests_1hour"
        else:
            table_name = "requests_5min"
        
        # Build WHERE clause for filtering
        where_conditions = []
        params = {
            'start_time': query.start_time,
            'end_time': query.end_time
        }
        
        if query.service:
            where_conditions.append("service = :service")
            params['service'] = query.service
        
        if query.node:
            where_conditions.append("node = :node")
            params['node'] = query.node
        
        if query.method:
            where_conditions.append("method = :method")
            params['method'] = query.method
        
        if query.endpoint:
            where_conditions.append("endpoint = :endpoint")
            params['endpoint'] = query.endpoint
        
        if query.consumer:
            where_conditions.append("consumer = :consumer")
            params['consumer'] = query.consumer

        if query.context:
            where_conditions.append("context = :context")
            params['context'] = query.context

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Simple query against the appropriate materialized view
        sql_query = text(f"""
            SELECT
                service,
                node,
                method,
                endpoint,
                consumer,
                context,
                status,
                bucket,
                count_requests,
                min_response_time,
                max_response_time,
                avg_response_time,
                p95_response_time
            FROM {table_name}
            WHERE {where_clause}
            AND bucket >= :start_time
            AND bucket <= :end_time
            ORDER BY bucket DESC
        """)
        
        try:
            result = await self.db.execute(sql_query, params)
            rows = result.fetchall()
            
            return [
                AggregatedMetrics(
                    service=row.service,
                    node=row.node,
                    method=row.method,
                    endpoint=row.endpoint,
                    consumer=row.consumer,
                    context=row.context,
                    status=row.status,
                    bucket=row.bucket,
                    count_requests=row.count_requests,
                    min_response_time=row.min_response_time,
                    max_response_time=row.max_response_time,
                    avg_response_time=row.avg_response_time,
                    p95_response_time=row.p95_response_time
                )
                for row in rows
            ]
        except Exception as e:
            raise e
    
    async def get_raw_metrics(self, query: MetricsQuery) -> List[RawMetrics]:
        """Get raw metrics based on query parameters"""
        
        # Build WHERE clause
        where_conditions = []
        params = {}
        
        if query.service:
            where_conditions.append("service = :service")
            params['service'] = query.service
        
        if query.node:
            where_conditions.append("node = :node")
            params['node'] = query.node
        
        if query.method:
            where_conditions.append("method = :method")
            params['method'] = query.method
        
        if query.endpoint:
            where_conditions.append("endpoint = :endpoint")
            params['endpoint'] = query.endpoint
        
        if query.consumer:
            where_conditions.append('consumer = :consumer')
            params['consumer'] = query.consumer

        if query.context:
            where_conditions.append('context = :context')
            params['context'] = query.context

        if query.start_time:
            where_conditions.append("created_at >= :start_time")
            params['start_time'] = query.start_time

        if query.end_time:
            where_conditions.append("created_at <= :end_time")
            params['end_time'] = query.end_time
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Build query
        sql_query = text(f"""
            SELECT
                service,
                node,
                method,
                endpoint,
                consumer,
                context,
                created_at,
                status,
                response_time
            FROM requests
            WHERE {where_clause}
            ORDER BY created_at DESC
        """)
        
        try:
            result = await self.db.execute(sql_query, params)
            rows = result.fetchall()
            
            return [
                RawMetrics(
                    service=row.service,
                    node=row.node,
                    method=row.method,
                    endpoint=row.endpoint,
                    consumer=row.consumer,
                    context=row.context,
                    created_at=row.created_at,
                    status=row.status,
                    response_time=row.response_time
                )
                for row in rows
            ]
        except Exception as e:
            raise e

    async def get_realtime_aggregated_metrics(self, query: MetricsQuery) -> List[AggregatedMetrics]:
        """Get real-time 1-minute aggregated metrics with 60-minute limit"""

        # Determine time range for querying
        now = datetime.now(timezone.utc)

        # If no start_time provided, default to 60 minutes ago
        if not query.start_time:
            query.start_time = now - timedelta(minutes=60)

        # If no end_time provided, use current time
        if not query.end_time:
            query.end_time = now

        # Validate time range doesn't exceed 60 minutes
        time_range = query.end_time - query.start_time
        max_range = timedelta(minutes=60)

        if time_range > max_range:
            raise ValueError("Time range cannot exceed 60 minutes for real-time metrics")

        # Build WHERE clause for filtering
        where_conditions = []
        params = {
            'start_time': query.start_time,
            'end_time': query.end_time
        }

        if query.service:
            where_conditions.append("service = :service")
            params['service'] = query.service

        if query.node:
            where_conditions.append("node = :node")
            params['node'] = query.node

        if query.method:
            where_conditions.append("method = :method")
            params['method'] = query.method

        if query.endpoint:
            where_conditions.append("endpoint = :endpoint")
            params['endpoint'] = query.endpoint

        if query.consumer:
            where_conditions.append("consumer = :consumer")
            params['consumer'] = query.consumer

        if query.context:
            where_conditions.append("context = :context")
            params['context'] = query.context

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # Query raw requests table with 1-minute aggregation
        sql_query = text(f"""
            SELECT
                service,
                node,
                method,
                endpoint,
                consumer,
                context,
                status,
                time_bucket('1 minute', created_at) as bucket,
                COUNT(*) as count_requests,
                MIN(response_time) as min_response_time,
                MAX(response_time) as max_response_time,
                AVG(response_time) as avg_response_time,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) as p95_response_time
            FROM requests
            WHERE {where_clause}
            AND created_at >= :start_time
            AND created_at <= :end_time
            GROUP BY service, node, method, endpoint, consumer, context, status, time_bucket('1 minute', created_at)
            ORDER BY bucket DESC
        """)

        try:
            result = await self.db.execute(sql_query, params)
            rows = result.fetchall()

            return [
                AggregatedMetrics(
                    service=row.service,
                    node=row.node,
                    method=row.method,
                    endpoint=row.endpoint,
                    consumer=row.consumer,
                    context=row.context,
                    status=row.status,
                    bucket=row.bucket,
                    count_requests=row.count_requests,
                    min_response_time=float(row.min_response_time) if row.min_response_time else 0.0,
                    max_response_time=float(row.max_response_time) if row.max_response_time else 0.0,
                    avg_response_time=float(row.avg_response_time) if row.avg_response_time else 0.0,
                    p95_response_time=float(row.p95_response_time) if row.p95_response_time else None
                )
                for row in rows
            ]
        except Exception as e:
            raise e