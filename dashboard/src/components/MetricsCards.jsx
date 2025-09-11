import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Speed,
  Functions,
  HourglassBottom,
  HourglassFull,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';

const MetricCard = ({ title, value, icon, color = 'primary', chartData, chartType = 'line' }) => {
  const IconComponent = icon;
  const theme = useTheme();
  
  return (
    <Card
      sx={{
        height: '100%',
        width: '100%',
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        '&:hover': {
          boxShadow: 6,
          transform: 'translateY(-2px)',
        },
        transition: 'all 0.2s ease-in-out',
      }}
    >
      {/* Background Chart */}
      {chartData && chartData.length > 0 && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            opacity: 0.1,
            zIndex: 1,
          }}
        >
          <ResponsiveContainer width="100%" height="100%">
            {chartType === 'area' ? (
              <AreaChart data={chartData}>
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke={theme.palette[color].main}
                  fill={theme.palette[color].main}
                  strokeWidth={2}
                />
              </AreaChart>
            ) : (
              <LineChart data={chartData}>
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke={theme.palette[color].main}
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        </Box>
      )}
      
      <CardContent sx={{ p: 3, position: 'relative', zIndex: 2, flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography
              color="text.secondary"
              gutterBottom
              variant="h6"
              fontWeight={500}
            >
              {title}
            </Typography>
            <Typography 
              variant={title.includes('Latency') ? 'h2' : 'h3'} 
              sx={{ 
                fontWeight: 700, 
                color: 'text.primary',
                fontSize: title.includes('Latency') ? '2.5rem' : undefined,
              }}
            >
              {value}
            </Typography>
          </Box>
          <Box
            sx={{
              p: 1.5,
              ml: 4,
              borderRadius: 3,
              backgroundColor: (theme) => alpha(theme.palette[color].main, 0.15),
              border: '1px solid',
              borderColor: (theme) => alpha(theme.palette[color].main, 0.2),
              color: `${color}.main`,
            }}
          >
            <IconComponent fontSize="large" />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const MetricsCards = ({ data, timeRange }) => {
  const calculateMetrics = () => {
    if (data.length === 0) {
      return {
        minLatency: 0,
        maxLatency: 0,
        avgLatency: 0,
        totalRequests: 0,
      };
    }
    
    const latencies = data.flatMap(item => [item.min_response_time, item.max_response_time]);
    const totalRequests = data.reduce((sum, item) => sum + item.count_requests, 0);
    const totalLatency = data.reduce((sum, item) => sum + (item.avg_response_time * item.count_requests), 0);
    
    return {
      minLatency: Math.min(...latencies),
      maxLatency: Math.max(...latencies),
      avgLatency: totalRequests > 0 ? totalLatency / totalRequests : 0,
      totalRequests,
    };
  };

  const prepareChartData = () => {
    if (!data || data.length === 0) return {};

    // Group data by time bucket and sort chronologically
    const bucketMap = new Map();

    data.forEach(item => {
      const bucket = item.bucket;
      if (!bucketMap.has(bucket)) {
        bucketMap.set(bucket, {
          timestamp: new Date(bucket),
          requests: 0,
          totalLatency: 0,
          minLatency: Infinity,
          maxLatency: 0,
          weightedLatency: 0,
        });
      }

      const current = bucketMap.get(bucket);
      current.requests += item.count_requests;
      current.weightedLatency += item.avg_response_time * item.count_requests;
      current.minLatency = Math.min(current.minLatency, item.min_response_time);
      current.maxLatency = Math.max(current.maxLatency, item.max_response_time);
    });

    // Find timestamps from existing data
    const timestamps = Array.from(bucketMap.values()).map(b => b.timestamp);
    if (timestamps.length === 0 && !timeRange) return {};

    // Determine bucket interval based on time range (matches backend logic)
    let bucketInterval;
    if (timeRange) {
      if (timeRange.hours === 1) {
        // Real-time endpoint: 1 minute buckets
        bucketInterval = 1 * 60 * 1000;
      } else if (timeRange.hours <= 24) {
        // 6 hours and 24 hours: 5 minute buckets
        bucketInterval = 5 * 60 * 1000;
      } else {
        // 7 days and longer: 1 hour buckets
        bucketInterval = 60 * 60 * 1000;
      }
    } else {
      // Fallback: detect from data if no timeRange provided
      const sortedTimestamps = timestamps.sort((a, b) => a - b);
      bucketInterval = 5 * 60 * 1000; // Default to 5 minutes

      if (sortedTimestamps.length > 1) {
        // Calculate intervals between consecutive buckets
        const intervals = [];
        for (let i = 1; i < sortedTimestamps.length; i++) {
          intervals.push(sortedTimestamps[i] - sortedTimestamps[i - 1]);
        }

        if (intervals.length > 0) {
          // Use the most common interval
          const intervalCounts = {};
          intervals.forEach(interval => {
            intervalCounts[interval] = (intervalCounts[interval] || 0) + 1;
          });

          const mostCommonInterval = Object.keys(intervalCounts).reduce((a, b) =>
            intervalCounts[a] > intervalCounts[b] ? a : b
          );

          bucketInterval = parseInt(mostCommonInterval);
        }
      }
    }

    // Determine the time range to display
    const now = new Date();
    const requestedEndTime = now.getTime();
    const requestedStartTime = timeRange
      ? now.getTime() - (timeRange.hours * 60 * 60 * 1000)
      : (timestamps.length > 0 ? Math.min(...timestamps) : requestedEndTime);

    // Align start time to bucket boundary
    const alignedStartTime = Math.floor(requestedStartTime / bucketInterval) * bucketInterval;

    const minTime = alignedStartTime;
    const maxTime = requestedEndTime;

    // Fill in missing buckets - use timestamp-based approach to avoid duplicates
    const filledBuckets = new Map();

    // Create a set of existing bucket timestamps for quick lookup
    const existingTimestamps = new Set();
    bucketMap.forEach((value, key) => {
      existingTimestamps.add(value.timestamp.getTime());
      filledBuckets.set(key, value); // Keep original backend data
    });

    // Add missing buckets
    for (let time = minTime; time <= maxTime; time += bucketInterval) {
      if (!existingTimestamps.has(time)) {
        const bucketKey = new Date(time).toISOString();
        filledBuckets.set(bucketKey, {
          timestamp: new Date(time),
          requests: 0,
          totalLatency: 0,
          minLatency: 0,
          maxLatency: 0,
          weightedLatency: 0,
        });
      }
    }

    const sortedData = Array.from(filledBuckets.values())
      .sort((a, b) => a.timestamp - b.timestamp)
      .map((bucket, index) => ({
        x: index,
        requests: bucket.requests,
        avgLatency: bucket.requests > 0 ? bucket.weightedLatency / bucket.requests : 0,
        minLatency: bucket.minLatency === Infinity ? 0 : bucket.minLatency,
        maxLatency: bucket.maxLatency,
      }));

    return {
      requestsChart: sortedData.map(d => ({ value: d.requests })),
      avgLatencyChart: sortedData.map(d => ({ value: d.avgLatency })),
      minLatencyChart: sortedData.map(d => ({ value: d.minLatency })),
      maxLatencyChart: sortedData.map(d => ({ value: d.maxLatency })),
    };
  };

  const metrics = calculateMetrics();
  const chartData = prepareChartData();

  return (
    <Grid container spacing={3} sx={{ width: '100%' }}>
      <Grid item xs={12} sm={6} md={3} sx={{ display: 'flex', flexGrow: 1  }}>
          <MetricCard
            title="Total Requests"
            value={metrics.totalRequests.toLocaleString()}
            icon={Functions}
            color="primary"
            chartData={chartData.requestsChart}
            chartType="area"
          />
      </Grid>

      <Grid item xs={12} sm={6} md={3} sx={{ display: 'flex', flexGrow: 1 }}>
          <MetricCard
            title="Average Latency"
            value={`${metrics.avgLatency.toFixed(1)}ms`}
            icon={Speed}
            color="secondary"
            chartData={chartData.avgLatencyChart}
            chartType="line"
          />
      </Grid>

      <Grid item xs={12} sm={6} md={3} sx={{ display: 'flex', flexGrow: 1 }}>
          <MetricCard
            title="Min Latency"
            value={`${metrics.minLatency.toFixed(1)}ms`}
            icon={HourglassBottom}
            color="success"
            chartData={chartData.minLatencyChart}
            chartType="line"
          />
      </Grid>

      <Grid item xs={12} sm={6} md={3} sx={{ display: 'flex', flexGrow: 1 }}>
          <MetricCard
            title="Max Latency"
            value={`${metrics.maxLatency.toFixed(1)}ms`}
            icon={HourglassFull}
            color="warning"
            chartData={chartData.maxLatencyChart}
            chartType="line"
          />
      </Grid>
    </Grid>
  );
};

export default MetricsCards;