import React from 'react';
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  alpha,
  useTheme,
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';

const StatusDistributionChart = ({ data }) => {
  const theme = useTheme();

  const prepareStatusData = () => {
    if (!data || data.length === 0) return { groupedData: [] };

    // Group by service, then by status within each service
    const serviceMap = new Map();

    data.forEach(item => {
      if (!serviceMap.has(item.service)) {
        serviceMap.set(item.service, new Map());
      }
      const statusMap = serviceMap.get(item.service);

      if (!statusMap.has(item.status)) {
        statusMap.set(item.status, 0);
      }
      statusMap.set(item.status, statusMap.get(item.status) + item.count_requests);
    });

    // Status colors
    const statusColors = {
      200: theme.palette.success.main,
      201: theme.palette.success.main,
      202: theme.palette.success.main,
      204: theme.palette.success.main,
      301: theme.palette.warning.main,
      302: theme.palette.warning.main,
      401: theme.palette.warning.main,
      400: theme.palette.error.main,
      403: theme.palette.error.main,
      404: theme.palette.error.main,
      422: theme.palette.error.main,
      500: theme.palette.error.main,
      502: theme.palette.error.main,
      503: theme.palette.error.main,
    };

    // Prepare grouped data for visualization
    const groupedData = Array.from(serviceMap.entries())
      .map(([service, statusMap]) => ({
        service,
        statuses: Array.from(statusMap.entries())
          .map(([status, count]) => ({
            status,
            count,
            color: statusColors[status] || theme.palette.grey.main,
          }))
          .sort((a, b) => a.status - b.status), // Sort by status code
        totalRequests: Array.from(statusMap.values()).reduce((sum, count) => sum + count, 0),
      }))
      .sort((a, b) => b.totalRequests - a.totalRequests); // Sort services by total requests

    return { groupedData };
  };

  const { groupedData } = prepareStatusData();

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const category = data.category;
      const count = data.count;
      const breakdown = data.breakdown || [];


      return (
        <Paper sx={{ p: 2, border: '1px solid', borderColor: 'divider', minWidth: 200 }}>
          <Typography variant="subtitle2" gutterBottom>
            {data.service}
          </Typography>
          <Typography variant="body2" sx={{ mb: 1 }}>
            {category.charAt(0).toUpperCase() + category.slice(1)}: {count?.toLocaleString() || 0} requests
          </Typography>
          {breakdown && breakdown.length > 0 ? (
            <>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                Status Breakdown:
              </Typography>
              {breakdown.map(statusData => (
                <Typography key={statusData.status} variant="body2" sx={{ fontSize: '0.875rem', color: 'text.secondary' }}>
                  HTTP {statusData.status}: {statusData.count.toLocaleString()}
                </Typography>
              ))}
            </>
          ) : (
            <Typography variant="body2" sx={{ fontSize: '0.875rem', color: 'text.secondary', fontStyle: 'italic' }}>
              No detailed status codes available
            </Typography>
          )}
        </Paper>
      );
    }
    return null;
  };

  // Transform data for individual bars - one entry per service-status combination
  const chartData = [];
  groupedData.forEach(serviceData => {
    const successCount = serviceData.statuses
      .filter(statusData => statusData.status >= 200 && statusData.status < 300)
      .reduce((sum, statusData) => sum + statusData.count, 0);

    const warningCount = serviceData.statuses
      .filter(statusData => statusData.status >= 300 && statusData.status < 400)
      .reduce((sum, statusData) => sum + statusData.count, 0);

    const errorCount = serviceData.statuses
      .filter(statusData => statusData.status >= 400)
      .reduce((sum, statusData) => sum + statusData.count, 0);

    // Create separate entries for each status category with unique service-category key
    if (successCount > 0) {
      chartData.push({
        serviceCategory: `${serviceData.service}-success`,
        service: serviceData.service,
        category: 'success',
        count: successCount,
        breakdown: serviceData.statuses.filter(statusData => statusData.status >= 200 && statusData.status < 300),
        color: theme.palette.success.main,
      });
    }
    if (warningCount > 0) {
      chartData.push({
        serviceCategory: `${serviceData.service}-warning`,
        service: serviceData.service,
        category: 'warning',
        count: warningCount,
        breakdown: serviceData.statuses.filter(statusData => statusData.status >= 300 && statusData.status < 400),
        color: theme.palette.warning.main,
      });
    }
    if (errorCount > 0) {
      chartData.push({
        serviceCategory: `${serviceData.service}-error`,
        service: serviceData.service,
        category: 'error',
        count: errorCount,
        breakdown: serviceData.statuses.filter(statusData => statusData.status >= 400),
        color: theme.palette.error.main,
      });
    }
  });


  return (
    <Paper sx={{ p: 3, borderRadius: 2, width: '100%' }}>
      <Typography variant="h6" gutterBottom fontWeight={600}>
        Status Distribution by Service
      </Typography>

      {groupedData.length === 0 ? (
        <Box sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4,
          color: 'text.secondary'
        }}>
          <Typography variant="body1">No data available</Typography>
        </Box>
      ) : (
        <Box sx={{ minHeight: 200 }}>
          <ResponsiveContainer width="100%" height={Math.max(500, chartData.length * 30 + 150)}>
            <BarChart
              data={chartData}
              margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
              barCategoryGap="10%"
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke={alpha(theme.palette.divider, 0.5)}
              />
              <XAxis
                dataKey="serviceCategory"
                tick={{ fontSize: 11, fill: theme.palette.text.secondary }}
                axisLine={{ stroke: theme.palette.divider }}
                angle={-45}
                textAnchor="end"
                height={80}
                tickFormatter={(value) => {
                  // Extract just the service name from "service-category"
                  const parts = value.split('-');
                  const service = parts.slice(0, -1).join('-'); // Handle service names with hyphens
                  const category = parts[parts.length - 1];
                  return `${service} (${category.charAt(0).toUpperCase()})`;
                }}
              />
              <YAxis
                tick={{ fontSize: 11, fill: theme.palette.text.secondary }}
                axisLine={{ stroke: theme.palette.divider }}
                label={{
                  value: 'Request Count',
                  angle: -90,
                  position: 'insideLeft',
                  style: { textAnchor: 'middle', fill: theme.palette.text.secondary }
                }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar
                dataKey="count"
                radius={[2, 2, 0, 0]}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>
      )}
    </Paper>
  );
};

export default StatusDistributionChart;