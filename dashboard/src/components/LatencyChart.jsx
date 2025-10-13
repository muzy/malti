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
    if (!Array.isArray(data) || data.length === 0) return [];

    return data.map(item => {
      const timestamp = new Date(item.bucket);
      
      // Format time based on time range
      let timeFormat;
      if (timeRange && timeRange.hours === 1) {
        timeFormat = { hour: '2-digit', minute: '2-digit' };
      } else if (timeRange && timeRange.hours <= 24) {
        timeFormat = { hour: '2-digit', minute: '2-digit' };
      } else {
        timeFormat = { month: 'short', day: 'numeric', hour: '2-digit' };
      }

      // Use null for missing data to create gaps in the chart
      const hasData = item.total_requests > 0;
      
      const avgLatency = (hasData && item.avg_latency != null && item.avg_latency > 0) 
        ? item.avg_latency 
        : null;
      
      const minLatency = (hasData && item.min_latency != null && item.min_latency > 0) 
        ? item.min_latency 
        : null;
      
      const p95Latency = (hasData && item.p95_latency != null && item.p95_latency > 0) 
        ? item.p95_latency 
        : null;
      
      const totalRequests = (item.total_requests > 0) 
        ? item.total_requests 
        : null;

      return {
        time: timestamp.toLocaleTimeString('en-US', timeFormat),
        timestamp: timestamp,
        avgLatency: avgLatency,
        minLatency: minLatency,
        p95Latency: p95Latency,
        totalRequests: totalRequests,
      };
    });
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
            else if (entry.name === 'P95 Latency') textColor = theme.palette.error.main;
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
              domain={isLeftLogScale ? [0.1, (dataMax) => Math.ceil(dataMax * 1.05)] : [0, (dataMax) => Math.ceil(dataMax * 1.05)]}
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
              domain={isRightLogScale ? [1, (dataMax) => Math.ceil(dataMax * 1.05)] : [0, (dataMax) => Math.ceil(dataMax * 1.05)]}
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
              connectNulls={false}
              activeDot={{ r: 8, fill: theme.palette.success.light }}
              name="Minimum Latency"
            />

            {/* P95 line (replaces Max) */}
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="p95Latency"
              stroke={theme.palette.error.main}
              strokeWidth={3}
              dot={false}
              connectNulls={false}
              activeDot={{ r: 8, fill: theme.palette.error.light }}
              name="P95 Latency"
            />

            {/* Average line */}
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="avgLatency"
              stroke={theme.palette.warning.main}
              strokeWidth={4}
              dot={{ r: 3, fill: theme.palette.warning.main }}
              connectNulls={false}
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
