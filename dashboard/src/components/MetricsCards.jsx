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
  TrendingUp,
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

const MetricsCards = ({ data, timeSeries }) => {
  // Prepare chart data from time series
  const prepareChartData = () => {
    if (!Array.isArray(timeSeries) || timeSeries.length === 0) {
      return {
        requestsChart: [],
        avgLatencyChart: [],
        minLatencyChart: [],
        p95LatencyChart: [],
        maxLatencyChart: [],
      };
    }

    return {
      requestsChart: timeSeries.map(d => ({ value: d.total_requests || 0 })),
      avgLatencyChart: timeSeries.map(d => ({ value: d.avg_latency || 0 })),
      minLatencyChart: timeSeries.map(d => ({ value: d.min_latency || 0 })),
      p95LatencyChart: timeSeries.map(d => ({ value: d.p95_latency || 0 })),
      maxLatencyChart: timeSeries.map(d => ({ value: d.max_latency || 0 })),
    };
  };

  const chartData = prepareChartData();

  return (
    <Grid container spacing={3} sx={{ width: '100%' }}>
      <Grid item xs={12} sm={6} md={2.4} sx={{ display: 'flex', flexGrow: 1  }}>
          <MetricCard
            title="Total Requests"
            value={data.total_requests.toLocaleString()}
            icon={Functions}
            color="primary"
            chartData={chartData.requestsChart}
            chartType="area"
          />
      </Grid>

      <Grid item xs={12} sm={6} md={2.4} sx={{ display: 'flex', flexGrow: 1 }}>
          <MetricCard
            title="Average Latency"
            value={data.avg_latency !== null ? `${data.avg_latency.toFixed(1)}ms` : 'N/A'}
            icon={Speed}
            color="warning"
            chartData={chartData.avgLatencyChart}
            chartType="line"
          />
      </Grid>

      <Grid item xs={12} sm={6} md={2.4} sx={{ display: 'flex', flexGrow: 1 }}>
          <MetricCard
            title="P95 Latency"
            value={data.p95_latency !== null ? `${data.p95_latency.toFixed(1)}ms` : 'N/A'}
            icon={TrendingUp}
            color="info"
            chartData={chartData.p95LatencyChart}
            chartType="line"
          />
      </Grid>

      <Grid item xs={12} sm={6} md={2.4} sx={{ display: 'flex', flexGrow: 1 }}>
          <MetricCard
            title="Min Latency"
            value={data.min_latency !== null ? `${data.min_latency.toFixed(1)}ms` : 'N/A'}
            icon={HourglassBottom}
            color="success"
            chartData={chartData.minLatencyChart}
            chartType="line"
          />
      </Grid>

      <Grid item xs={12} sm={6} md={2.4} sx={{ display: 'flex', flexGrow: 1 }}>
          <MetricCard
            title="Max Latency"
            value={data.max_latency !== null ? `${data.max_latency.toFixed(1)}ms` : 'N/A'}
            icon={HourglassFull}
            color="error"
            chartData={chartData.maxLatencyChart}
            chartType="line"
          />
      </Grid>
    </Grid>
  );
};

export default MetricsCards;
