import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  Button,
  alpha,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
} from 'recharts';

const LatencyChart = ({ data, height = 350, timeRange }) => {
  const theme = useTheme();
  const [isLeftLogScale, setIsLeftLogScale] = useState(false);
  const [isRightLogScale, setIsRightLogScale] = useState(false);
  const prepareTimeSeriesData = () => {
    if (!data || data.length === 0) return [];

    // Group by bucket and aggregate
    const bucketMap = new Map();

    data.forEach(item => {
      const bucket = item.bucket;
      if (!bucketMap.has(bucket)) {
        bucketMap.set(bucket, {
          time: new Date(bucket).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          }),
          timestamp: new Date(bucket),
          avgLatency: 0,
          minLatency: Infinity,
          maxLatency: 0,
          totalRequests: 0,
          weightedLatency: 0,
        });
      }

      const current = bucketMap.get(bucket);
      current.totalRequests += item.count_requests;
      current.weightedLatency += item.avg_response_time * item.count_requests;
      current.minLatency = Math.min(current.minLatency, item.min_response_time);
      current.maxLatency = Math.max(current.maxLatency, item.max_response_time);
    });

    // Find timestamps from existing data
    const timestamps = Array.from(bucketMap.values()).map(b => b.timestamp);
    if (timestamps.length === 0 && !timeRange) return [];

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
          time: new Date(time).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
          }),
          timestamp: new Date(time),
          avgLatency: 0,
          minLatency: 0,
          maxLatency: 0,
          totalRequests: 0,
          weightedLatency: 0,
        });
      }
    }

    // Calculate weighted averages and sort by time
    return Array.from(filledBuckets.values())
      .map(bucket => {
        const avgLatency = bucket.totalRequests > 0 ? bucket.weightedLatency / bucket.totalRequests : 0;
        const minLatency = bucket.minLatency === Infinity ? 0 : bucket.minLatency;
        const maxLatency = bucket.maxLatency;

        // Ensure minimum values for log scale compatibility
        const adjustedAvgLatency = avgLatency <= 0 ? 0.1 : avgLatency;
        const adjustedMinLatency = minLatency <= 0 ? 0.1 : minLatency;
        const adjustedMaxLatency = maxLatency <= 0 ? 0.1 : maxLatency;
        const adjustedTotalRequests = bucket.totalRequests <= 0 ? 1 : bucket.totalRequests;

        return {
          ...bucket,
          avgLatency: adjustedAvgLatency,
          minLatency: adjustedMinLatency,
          maxLatency: adjustedMaxLatency,
          totalRequests: adjustedTotalRequests,
        };
      })
      .sort((a, b) => a.timestamp - b.timestamp);
  };

  const timeSeriesData = prepareTimeSeriesData();

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Paper sx={{ p: 2, border: '1px solid', borderColor: 'divider' }}>
          <Typography variant="subtitle2" gutterBottom>
            {label}
          </Typography>
          {payload.map((entry, index) => {
            // Use contrasting colors for better readability
            let textColor = theme.palette.text.primary;
            if (entry.name === 'Average Latency') textColor = theme.palette.warning.main;
            else if (entry.name === 'Minimum Latency') textColor = theme.palette.success.main;
            else if (entry.name === 'Maximum Latency') textColor = theme.palette.error.light;
            else if (entry.name === 'Total Requests') textColor = theme.palette.primary.main;

            return (
              <Typography
                key={index}
                variant="body2"
                sx={{ color: textColor }}
              >
                {entry.name}: {entry.name === 'Total Requests'
                  ? entry.value.toLocaleString()
                  : `${entry.value.toFixed(1)}ms`}
              </Typography>
            );
          })}
        </Paper>
      );
    }
    return null;
  };

  return (
    <Paper 
      sx={{ 
        p: 3,
        borderRadius: 2,
        height: '100%',
        background: (theme) => theme.palette.background.paper,
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight={700}>
          Response Time Over Time and Number of Requests
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant={isLeftLogScale ? "contained" : "outlined"}
            size="small"
            onClick={() => setIsLeftLogScale(!isLeftLogScale)}
            sx={{
              minWidth: 'auto',
              px: 2,
              fontSize: '0.75rem',
            }}
          >
            Latency Log Scale
          </Button>
          <Button
            variant={isRightLogScale ? "contained" : "outlined"}
            size="small"
            onClick={() => setIsRightLogScale(!isRightLogScale)}
            sx={{
              minWidth: 'auto',
              px: 2,
              fontSize: '0.75rem',
            }}
          >
            Requests Log Scale
          </Button>
        </Box>
      </Box>
      
      <Box sx={{ mt: 2, height }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={timeSeriesData}>
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke={alpha(theme.palette.divider, 0.5)}
            />
            <XAxis 
              dataKey="time"
              tick={{ fontSize: 12, fill: theme.palette.text.secondary }}
              axisLine={{ stroke: theme.palette.divider }}
            />
            <YAxis
              yAxisId="left"
              scale={isLeftLogScale ? "log" : "linear"}
              domain={isLeftLogScale ? [0.1, 'dataMax'] : ['dataMin', 'dataMax']}
              tick={{ fontSize: 12, fill: theme.palette.text.secondary }}
              axisLine={{ stroke: theme.palette.divider }}
              label={{
                value: 'Response Time (ms)',
                angle: -90,
                position: 'insideLeft',
                style: { textAnchor: 'middle', fill: theme.palette.text.secondary }
              }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              scale={isRightLogScale ? "log" : "linear"}
              domain={isRightLogScale ? [1, 'dataMax'] : ['dataMin', 'dataMax']}
              tick={{ fontSize: 12, fill: theme.palette.text.secondary }}
              axisLine={{ stroke: theme.palette.divider }}
              label={{
                value: 'Number of Requests',
                angle: 90,
                position: 'insideRight',
                style: { textAnchor: 'middle', fill: theme.palette.text.secondary }
              }}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* Request count bars (rendered first so lines appear on top) */}
            <Bar
              yAxisId="right"
              dataKey="totalRequests"
              fill={alpha(theme.palette.primary.dark, 0.6)}
              stroke={alpha(theme.palette.primary.dark, 0.6)}
              strokeWidth={1}
              name="Total Requests"
            />

            {/* Min line */}
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="minLatency"
              stroke={theme.palette.success.main}
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 8, fill: theme.palette.success.light }}
              name="Minimum Latency"
            />

            {/* Max line */}
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="maxLatency"
              stroke={theme.palette.error.main}
              strokeWidth={3}
              dot={false}
              activeDot={{ r: 8, fill: theme.palette.error.light }}
              name="Maximum Latency"
            />

            {/* Average line */}
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="avgLatency"
              stroke={theme.palette.warning.main}
              strokeWidth={4}
              dot={{ r: 3, fill: theme.palette.warning.main }}
              activeDot={{ r: 8, fill: theme.palette.warning.light }}
              name="Average Latency"
            />

          </ComposedChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default LatencyChart;