from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models.telemetry import (
    MetricsQuery,
    DashboardMetricsResponse,
    TimeSeriesDataPoint,
    MetricsCardsSummary,
    EndpointAggregation,
    StatusDistribution,
    ConsumerAggregation,
    SystemOverview
)
from typing import Dict, List
from datetime import datetime, timezone, timedelta

class MetricsService:
    """Service for querying metrics data from materialized views"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_metrics(self, query: MetricsQuery) -> DashboardMetricsResponse:
        """Get all dashboard metrics with server-side aggregation and gap filling"""
        
        # Determine time range for querying
        now = datetime.now(timezone.utc)
        
        # If no start_time provided, default based on whether it's realtime
        if not query.start_time:
            if query.interval == "1min":
                query.start_time = now - timedelta(minutes=60)  # 1 hour for realtime
            else:
                query.start_time = now - timedelta(days=7)  # 7 days for regular
        
        # If no end_time provided, use current time
        if not query.end_time:
            query.end_time = now
        
        # Calculate time range duration
        time_range = query.end_time - query.start_time
        
        # Determine which table/view to use and bucket size
        if query.interval == "1min":
            # Real-time: use raw requests table with 1-minute buckets
            table_name = "requests"
            bucket_size = "1 minute"
            time_column = "created_at"
        elif time_range.days > 4 or query.interval == "1hour":
            # Long range: use 1-hour aggregates
            table_name = "requests_1hour"
            bucket_size = "1 hour"
            time_column = "bucket"
        else:
            # Short range: use 5-minute aggregates
            table_name = "requests_5min"
            bucket_size = "5 minutes"
            time_column = "bucket"
        
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
        
        # Build comprehensive SQL query with CTEs
        # Note: For raw requests table, we need to aggregate on-the-fly
        if table_name == "requests":
            # Query raw requests table with runtime aggregation
            sql_query = text(f"""
                WITH base_data AS (
                    SELECT
                        service,
                        node,
                        method,
                        endpoint,
                        consumer,
                        context,
                        status,
                        response_time,
                        created_at
                    FROM requests
                    WHERE {where_clause}
                    AND created_at >= :start_time
                    AND created_at <= :end_time
                ),
                time_series AS (
                    SELECT
                        time_bucket_gapfill('{bucket_size}', created_at, :start_time, :end_time) as bucket,
                        COALESCE(COUNT(*), 0) as total_requests,
                        CASE WHEN COUNT(*) > 0 THEN MIN(response_time)::float ELSE NULL END as min_latency,
                        CASE WHEN COUNT(*) > 0 THEN AVG(response_time)::float ELSE NULL END as avg_latency,
                        CASE WHEN COUNT(*) > 0 THEN PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time)::float ELSE NULL END as p95_latency,
                        CASE WHEN COUNT(*) > 0 THEN MAX(response_time)::float ELSE NULL END as max_latency
                    FROM base_data
                    GROUP BY time_bucket_gapfill('{bucket_size}', created_at, :start_time, :end_time)
                    ORDER BY bucket
                ),
                metrics_summary AS (
                    SELECT
                        COUNT(*) as total_requests,
                        AVG(response_time)::float as avg_latency,
                        MIN(response_time)::float as min_latency,
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time)::float as p95_latency,
                        MAX(response_time)::float as max_latency
                    FROM base_data
                ),
                endpoint_agg AS (
                    SELECT
                        endpoint,
                        method,
                        service,
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN status >= 400 AND status != 401 THEN 1 ELSE 0 END) as error_count,
                        (SUM(CASE WHEN status >= 400 AND status != 401 THEN 1 ELSE 0 END)::float / COUNT(*)::float * 100) as error_rate
                    FROM base_data
                    GROUP BY endpoint, method, service
                    ORDER BY total_requests DESC
                ),
                status_dist AS (
                    SELECT
                        service,
                        status,
                        COUNT(*) as count
                    FROM base_data
                    GROUP BY service, status
                ),
                status_agg AS (
                    SELECT
                        service,
                        SUM(count) as total_requests,
                        SUM(CASE WHEN status >= 200 AND status < 300 THEN count ELSE 0 END) as success_2xx,
                        SUM(CASE WHEN status >= 300 AND status < 400 THEN count ELSE 0 END) as warning_3xx,
                        SUM(CASE WHEN status >= 400 THEN count ELSE 0 END) as error_4xx_5xx,
                        jsonb_object_agg(status::text, count) as status_breakdown
                    FROM status_dist
                    GROUP BY service
                    ORDER BY total_requests DESC
                ),
                consumer_agg AS (
                    SELECT
                        consumer,
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN status >= 400 AND status != 401 THEN 1 ELSE 0 END) as error_count,
                        (SUM(CASE WHEN status >= 400 AND status != 401 THEN 1 ELSE 0 END)::float / COUNT(*)::float * 100) as error_rate
                    FROM base_data
                    GROUP BY consumer
                    ORDER BY total_requests DESC
                ),
                system_overview AS (
                    SELECT
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN status >= 400 AND status != 401 THEN 1 ELSE 0 END) as total_errors,
                        (SUM(CASE WHEN status >= 400 AND status != 401 THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*), 0)::float * 100) as error_rate,
                        AVG(response_time)::float as avg_latency
                    FROM base_data
                ),
                distinct_nodes AS (
                    SELECT DISTINCT node
                    FROM requests
                    WHERE node IS NOT NULL
                    AND created_at >= :start_time
                    AND created_at <= :end_time
                ),
                distinct_contexts AS (
                    SELECT DISTINCT context
                    FROM requests
                    WHERE context IS NOT NULL
                    AND created_at >= :start_time
                    AND created_at <= :end_time
                )
                SELECT
                    'time_series' as data_type,
                    jsonb_agg(jsonb_build_object(
                        'bucket', bucket,
                        'total_requests', total_requests,
                        'min_latency', min_latency,
                        'avg_latency', avg_latency,
                        'p95_latency', p95_latency,
                        'max_latency', max_latency
                    ) ORDER BY bucket) as data
                FROM time_series
                UNION ALL
                SELECT
                    'metrics_summary' as data_type,
                    jsonb_build_object(
                        'total_requests', COALESCE(total_requests, 0),
                        'avg_latency', avg_latency,
                        'min_latency', min_latency,
                        'p95_latency', p95_latency,
                        'max_latency', max_latency
                    ) as data
                FROM metrics_summary
                UNION ALL
                SELECT
                    'endpoints' as data_type,
                    jsonb_agg(jsonb_build_object(
                        'endpoint', endpoint,
                        'method', method,
                        'service', service,
                        'total_requests', total_requests,
                        'error_count', error_count,
                        'error_rate', error_rate
                    ) ORDER BY total_requests DESC) as data
                FROM endpoint_agg
                UNION ALL
                SELECT
                    'status_distribution' as data_type,
                    jsonb_agg(jsonb_build_object(
                        'service', service,
                        'total_requests', total_requests,
                        'success_2xx', success_2xx,
                        'warning_3xx', warning_3xx,
                        'error_4xx_5xx', error_4xx_5xx,
                        'status_breakdown', status_breakdown
                    ) ORDER BY total_requests DESC) as data
                FROM status_agg
                UNION ALL
                SELECT
                    'consumers' as data_type,
                    jsonb_agg(jsonb_build_object(
                        'consumer', consumer,
                        'total_requests', total_requests,
                        'error_count', error_count,
                        'error_rate', error_rate
                    ) ORDER BY total_requests DESC) as data
                FROM consumer_agg
                UNION ALL
                SELECT
                    'system_overview' as data_type,
                    jsonb_build_object(
                        'total_requests', COALESCE(total_requests, 0),
                        'total_errors', COALESCE(total_errors, 0),
                        'error_rate', COALESCE(error_rate, 0),
                        'avg_latency', avg_latency
                    ) as data
                FROM system_overview
                UNION ALL
                SELECT
                    'distinct_nodes' as data_type,
                    jsonb_agg(node ORDER BY node) as data
                FROM distinct_nodes
                UNION ALL
                SELECT
                    'distinct_contexts' as data_type,
                    jsonb_agg(context ORDER BY context) as data
                FROM distinct_contexts
            """)
        else:
            # Query from materialized views (requests_5min or requests_1hour)
            sql_query = text(f"""
                WITH base_data AS (
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
                ),
                time_series AS (
                    SELECT
                        time_bucket_gapfill('{bucket_size}', bucket, :start_time, :end_time) as bucket,
                        COALESCE(SUM(count_requests), 0) as total_requests,
                        CASE WHEN SUM(count_requests) > 0 THEN MIN(min_response_time) FILTER (WHERE min_response_time IS NOT NULL)::float ELSE NULL END as min_latency,
                        CASE WHEN SUM(count_requests) > 0 THEN 
                            (SUM(avg_response_time * count_requests) / SUM(count_requests))::float 
                        ELSE NULL END as avg_latency,
                        -- Note: P95 in time series is approximate when aggregating pre-aggregated data
                        -- For accurate overall P95, see metrics_summary which queries raw data
                        CASE WHEN SUM(count_requests) > 0 THEN MAX(p95_response_time) FILTER (WHERE p95_response_time IS NOT NULL)::float ELSE NULL END as p95_latency,
                        CASE WHEN SUM(count_requests) > 0 THEN MAX(max_response_time) FILTER (WHERE max_response_time IS NOT NULL)::float ELSE NULL END as max_latency
                    FROM base_data
                    GROUP BY time_bucket_gapfill('{bucket_size}', bucket, :start_time, :end_time)
                    ORDER BY bucket
                ),
                metrics_summary AS (
                    SELECT
                        SUM(count_requests) as total_requests,
                        (SUM(avg_response_time * count_requests) / SUM(count_requests))::float as avg_latency,
                        MIN(min_response_time) FILTER (WHERE min_response_time IS NOT NULL)::float as min_latency,
                        -- Note: P95 calculation from pre-aggregated data is approximate
                        MAX(p95_response_time) FILTER (WHERE p95_response_time IS NOT NULL)::float as p95_latency,
                        MAX(max_response_time) FILTER (WHERE max_response_time IS NOT NULL)::float as max_latency
                    FROM base_data
                ),
                endpoint_agg AS (
                    SELECT
                        endpoint,
                        method,
                        service,
                        SUM(count_requests) as total_requests,
                        SUM(CASE WHEN status >= 400 AND status != 401 THEN count_requests ELSE 0 END) as error_count,
                        (SUM(CASE WHEN status >= 400 AND status != 401 THEN count_requests ELSE 0 END)::float / 
                         NULLIF(SUM(count_requests), 0)::float * 100) as error_rate
                    FROM base_data
                    GROUP BY endpoint, method, service
                    ORDER BY total_requests DESC
                ),
                status_dist AS (
                    SELECT
                        service,
                        status,
                        SUM(count_requests) as count
                    FROM base_data
                    GROUP BY service, status
                ),
                status_agg AS (
                    SELECT
                        service,
                        SUM(count) as total_requests,
                        SUM(CASE WHEN status >= 200 AND status < 300 THEN count ELSE 0 END) as success_2xx,
                        SUM(CASE WHEN status >= 300 AND status < 400 THEN count ELSE 0 END) as warning_3xx,
                        SUM(CASE WHEN status >= 400 THEN count ELSE 0 END) as error_4xx_5xx,
                        jsonb_object_agg(status::text, count) as status_breakdown
                    FROM status_dist
                    GROUP BY service
                    ORDER BY total_requests DESC
                ),
                consumer_agg AS (
                    SELECT
                        consumer,
                        SUM(count_requests) as total_requests,
                        SUM(CASE WHEN status >= 400 AND status != 401 THEN count_requests ELSE 0 END) as error_count,
                        (SUM(CASE WHEN status >= 400 AND status != 401 THEN count_requests ELSE 0 END)::float / 
                         NULLIF(SUM(count_requests), 0)::float * 100) as error_rate
                    FROM base_data
                    GROUP BY consumer
                    ORDER BY total_requests DESC
                ),
                system_overview AS (
                    SELECT
                        SUM(count_requests) as total_requests,
                        SUM(CASE WHEN status >= 400 AND status != 401 THEN count_requests ELSE 0 END) as total_errors,
                        (SUM(CASE WHEN status >= 400 AND status != 401 THEN count_requests ELSE 0 END)::float / 
                         NULLIF(SUM(count_requests), 0)::float * 100) as error_rate,
                        (SUM(avg_response_time * count_requests) / SUM(count_requests))::float as avg_latency
                    FROM base_data
                ),
                distinct_nodes AS (
                    SELECT DISTINCT node
                    FROM {table_name}
                    WHERE node IS NOT NULL
                    AND bucket >= :start_time
                    AND bucket <= :end_time
                ),
                distinct_contexts AS (
                    SELECT DISTINCT context
                    FROM {table_name}
                    WHERE context IS NOT NULL
                    AND bucket >= :start_time
                    AND bucket <= :end_time
                )
                SELECT
                    'time_series' as data_type,
                    jsonb_agg(jsonb_build_object(
                        'bucket', bucket,
                        'total_requests', total_requests,
                        'min_latency', min_latency,
                        'avg_latency', avg_latency,
                        'p95_latency', p95_latency,
                        'max_latency', max_latency
                    ) ORDER BY bucket) as data
                FROM time_series
                UNION ALL
                SELECT
                    'metrics_summary' as data_type,
                    jsonb_build_object(
                        'total_requests', COALESCE(total_requests, 0),
                        'avg_latency', avg_latency,
                        'min_latency', min_latency,
                        'p95_latency', p95_latency,
                        'max_latency', max_latency
                    ) as data
                FROM metrics_summary
                UNION ALL
                SELECT
                    'endpoints' as data_type,
                    jsonb_agg(jsonb_build_object(
                        'endpoint', endpoint,
                        'method', method,
                        'service', service,
                        'total_requests', total_requests,
                        'error_count', error_count,
                        'error_rate', error_rate
                    ) ORDER BY total_requests DESC) as data
                FROM endpoint_agg
                UNION ALL
                SELECT
                    'status_distribution' as data_type,
                    jsonb_agg(jsonb_build_object(
                        'service', service,
                        'total_requests', total_requests,
                        'success_2xx', success_2xx,
                        'warning_3xx', warning_3xx,
                        'error_4xx_5xx', error_4xx_5xx,
                        'status_breakdown', status_breakdown
                    ) ORDER BY total_requests DESC) as data
                FROM status_agg
                UNION ALL
                SELECT
                    'consumers' as data_type,
                    jsonb_agg(jsonb_build_object(
                        'consumer', consumer,
                        'total_requests', total_requests,
                        'error_count', error_count,
                        'error_rate', error_rate
                    ) ORDER BY total_requests DESC) as data
                FROM consumer_agg
                UNION ALL
                SELECT
                    'system_overview' as data_type,
                    jsonb_build_object(
                        'total_requests', COALESCE(total_requests, 0),
                        'total_errors', COALESCE(total_errors, 0),
                        'error_rate', COALESCE(error_rate, 0),
                        'avg_latency', avg_latency
                    ) as data
                FROM system_overview
                UNION ALL
                SELECT
                    'distinct_nodes' as data_type,
                    jsonb_agg(node ORDER BY node) as data
                FROM distinct_nodes
                UNION ALL
                SELECT
                    'distinct_contexts' as data_type,
                    jsonb_agg(context ORDER BY context) as data
                FROM distinct_contexts
            """)
        
        try:
            result = await self.db.execute(sql_query, params)
            rows = result.fetchall()
            
            # Parse the results into structured data
            response_data = {
                'time_series': [],
                'metrics_summary': None,
                'endpoints': [],
                'status_distribution': [],
                'consumers': [],
                'system_overview': None,
                'distinct_nodes': [],
                'distinct_contexts': []
            }
            
            for row in rows:
                data_type = row.data_type
                data = row.data
                
                if data_type == 'time_series' and data:
                    response_data['time_series'] = [
                        TimeSeriesDataPoint(**item) for item in data
                    ]
                elif data_type == 'metrics_summary' and data:
                    response_data['metrics_summary'] = MetricsCardsSummary(**data)
                elif data_type == 'endpoints' and data:
                    response_data['endpoints'] = [
                        EndpointAggregation(**item) for item in data
                    ]
                elif data_type == 'status_distribution' and data:
                    response_data['status_distribution'] = [
                        StatusDistribution(**item) for item in data
                    ]
                elif data_type == 'consumers' and data:
                    response_data['consumers'] = [
                        ConsumerAggregation(**item) for item in data
                    ]
                elif data_type == 'system_overview' and data:
                    response_data['system_overview'] = SystemOverview(**data)
                elif data_type == 'distinct_nodes' and data:
                    response_data['distinct_nodes'] = data
                elif data_type == 'distinct_contexts' and data:
                    response_data['distinct_contexts'] = data
            
            # Provide defaults if no data
            if not response_data['metrics_summary']:
                response_data['metrics_summary'] = MetricsCardsSummary(
                    total_requests=0,
                    avg_latency=None,
                    min_latency=None,
                    p95_latency=None,
                    max_latency=None
                )
            
            if not response_data['system_overview']:
                response_data['system_overview'] = SystemOverview(
                    total_requests=0,
                    total_errors=0,
                    error_rate=0.0,
                    avg_latency=None
                )
            
            return DashboardMetricsResponse(**response_data)
            
        except Exception as e:
            raise e
