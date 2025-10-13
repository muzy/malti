import React from 'react';
import {
  Box,
  Typography,
  alpha,
} from '@mui/material';
import { getErrorRateColor, getLatencyColor } from '../utils/statusUtils';

const StatusIndicator = ({ data }) => {
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
            {data.total_requests.toLocaleString()}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Total Requests
          </Typography>
        </Box>
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography
            variant="h5"
            fontWeight={700}
            color={getErrorRateColor(data.error_rate)}
          >
            {data.error_rate.toFixed(1)}%
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Error Rate
          </Typography>
        </Box>
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography
            variant="h5"
            fontWeight={700}
            color={getLatencyColor(data.avg_latency)}
          >
            {data.avg_latency !== null ? `${data.avg_latency.toFixed(0)}ms` : 'N/A'}
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
