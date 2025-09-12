import React from 'react';
import {
  Box,
  Typography,
  Chip,
  alpha,
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Error,
} from '@mui/icons-material';
import { getErrorRateColor, getLatencyColor } from '../utils/statusUtils';

const StatusIndicator = ({ data }) => {
  const calculateStats = () => {
    if (!data || data.length === 0) return { totalRequests: 0, totalErrors: 0, errorRate: 0, avgLatency: 0 };
    
    const totalRequests = data.reduce((sum, item) => sum + item.count_requests, 0);
    const totalErrors = data.reduce((sum, item) => {
      if (item.status >= 400 && item.status !== 401) {
        return sum + item.count_requests;
      }
      return sum;
    }, 0);
    const errorRate = totalRequests > 0 ? (totalErrors / totalRequests) * 100 : 0;
    
    const avgLatency = totalRequests > 0 
      ? data.reduce((sum, item) => sum + (item.avg_response_time * item.count_requests), 0) / totalRequests
      : 0;
    
    return { totalRequests, totalErrors, errorRate, avgLatency };
  };

  const stats = calculateStats();

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 2,
        p: 3,
        borderRadius: 2,
        backgroundColor: (theme) => alpha(theme.palette.primary.main, 0.05),
        border: '1px solid',
        borderColor: (theme) => alpha(theme.palette.primary.main, 0.2),
      }}
    >
      <Box>
        <Typography variant="h6" fontWeight={600} color="text.primary">
          System Overview
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Real-time metrics from selected time range and filters
        </Typography>
      </Box>
      
      <Box sx={{ display: 'flex', gap: 3, alignItems: 'center' }}>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h5" fontWeight={700} color="primary.main">
            {stats.totalRequests.toLocaleString()}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Total Requests
          </Typography>
        </Box>
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography
            variant="h5"
            fontWeight={700}
            color={getErrorRateColor(stats.errorRate)}
          >
            {stats.errorRate.toFixed(1)}%
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Error Rate
          </Typography>
        </Box>
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography
            variant="h5"
            fontWeight={700}
            color={getLatencyColor(stats.avgLatency)}
          >
            {stats.avgLatency.toFixed(0)}ms
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Avg Latency
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default StatusIndicator;