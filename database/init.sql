-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create the requests table
CREATE TABLE IF NOT EXISTS requests (
    service TEXT NOT NULL,
    node TEXT,
    method TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    endpoint TEXT NOT NULL,
    context TEXT,
    status SMALLINT NOT NULL,
    response_time INT NOT NULL,
    consumer TEXT NOT NULL
);

-- Convert to hypertable (TimescaleDB requirement)
SELECT create_hypertable('requests', 'created_at', if_not_exists => TRUE);
SELECT set_chunk_time_interval('requests', INTERVAL '1 day');

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_requests_service_created_at ON requests (service, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests (status);
CREATE INDEX IF NOT EXISTS idx_requests_endpoint ON requests (endpoint);
CREATE INDEX IF NOT EXISTS idx_requests_consumer ON requests (consumer);
CREATE INDEX IF NOT EXISTS idx_requests_context ON requests (context);

-- Create continuous aggregates for 5-minute intervals
CREATE MATERIALIZED VIEW IF NOT EXISTS requests_5min
WITH (timescaledb.continuous) AS
SELECT
    service,
    node,
    method,
    endpoint,
    consumer,
    context,
    status,
    time_bucket('5 minutes', created_at) AS bucket,
    COUNT(*) as count_requests,
    MIN(response_time) as min_response_time,
    MAX(response_time) as max_response_time,
    AVG(response_time) as avg_response_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) as p95_response_time
FROM requests
GROUP BY service, node, method, endpoint, consumer, context, status, bucket;

-- Create continuous aggregates for 1-hour intervals
CREATE MATERIALIZED VIEW IF NOT EXISTS requests_1hour
WITH (timescaledb.continuous) AS
SELECT
    service,
    node,
    method,
    endpoint,
    consumer,
    context,
    status,
    time_bucket('1 hour', created_at) AS bucket,
    COUNT(*) as count_requests,
    MIN(response_time) as min_response_time,
    MAX(response_time) as max_response_time,
    AVG(response_time) as avg_response_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) as p95_response_time
FROM requests
GROUP BY service, node, method, endpoint, consumer, context, status, bucket;

-- Set up data retention policies
-- Raw data: 6 hours
SELECT add_retention_policy('requests', INTERVAL '6 hours');

-- 5-minute aggregates: 90 days
SELECT add_retention_policy('requests_5min', INTERVAL '90 days');

-- 1-hour aggregates: 720 days
SELECT add_retention_policy('requests_1hour', INTERVAL '720 days');

-- Create refresh policies for continuous aggregates
SELECT add_continuous_aggregate_policy('requests_5min',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '0',
    schedule_interval => INTERVAL '1 minute');

SELECT add_continuous_aggregate_policy('requests_1hour',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '0',
    schedule_interval => INTERVAL '15 minutes');
