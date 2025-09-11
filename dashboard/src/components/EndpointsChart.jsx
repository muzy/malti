import React from 'react';
import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  LinearProgress,
  alpha,
  useTheme,
} from '@mui/material';

const EndpointsChart = ({ data, onEndpointClick }) => {
  const theme = useTheme();
  const prepareEndpointData = () => {
    if (!data || data.length === 0) return [];
    
    const endpointMap = new Map();
    
    data.forEach(item => {
      const key = `${item.method} ${item.endpoint}`;
      if (!endpointMap.has(key)) {
        endpointMap.set(key, {
          endpoint: item.endpoint,
          method: item.method,
          fullEndpoint: key,
          count: 0,
          errors: 0,
        });
      }
      
      const current = endpointMap.get(key);
      current.count += item.count_requests;
      if (item.status >= 400 && item.status !== 401) {
        current.errors += item.count_requests;
      }
    });
    
    return Array.from(endpointMap.values())
      .sort((a, b) => b.count - a.count);
  };

  const endpointData = prepareEndpointData();
  const maxCount = endpointData.length > 0 ? Math.max(...endpointData.map(item => item.count)) : 1;

  const getMethodColor = (method) => {
    const colors = {
      GET: '#2e7d32',
      POST: '#1976d2', 
      PUT: '#ed6c02',
      DELETE: '#d32f2f',
      PATCH: '#7b1fa2',
    };
    return colors[method] || '#666666';
  };

  return (
    <Paper 
      sx={{ 
        p: 3,
        borderRadius: 2,
        width: '100%',
        maxWidth: 'none',
        minWidth: 0,
        flex: 1,
        background: (theme) => theme.palette.background.paper,
      }}
    >
      <Typography variant="h6" gutterBottom fontWeight={600}>
        Top Endpoints by Request Count
      </Typography>
      
      {endpointData.length === 0 ? (
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: 200,
          color: 'text.secondary' 
        }}>
          <Typography variant="body1">No data available</Typography>
        </Box>
      ) : (
        <Box sx={{ mt: 2 }}>
          <List sx={{ p: 0 }}>
            {endpointData.map((item, index) => (
              <ListItem
                key={index}
                onClick={() => onEndpointClick?.(item.endpoint, item.method)}
                sx={{
                  cursor: 'pointer',
                  borderRadius: 2,
                  mb: 1,
                  p: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.05),
                    borderColor: theme.palette.primary.main,
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                <Box sx={{ width: '100%' }}>
                  {/* Header with method, endpoint and stats */}
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={item.method}
                        size="small"
                        sx={{
                          backgroundColor: getMethodColor(item.method),
                          color: 'white',
                          fontWeight: 600,
                          minWidth: 60,
                        }}
                      />
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontFamily: 'monospace', 
                          fontWeight: 500,
                          maxWidth: { xs: 200, md: 400 },
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {item.endpoint}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Typography variant="body2" fontWeight={600}>
                        {item.count.toLocaleString()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        requests
                      </Typography>
                    </Box>
                  </Box>
                  
                  {/* Progress bar */}
                  <Box sx={{ mb: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={(item.count / maxCount) * 100}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 4,
                          backgroundColor: theme.palette.primary.main,
                        },
                      }}
                    />
                  </Box>
                  
                  {/* Error rate indicator */}
                  {item.errors > 0 && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ flex: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={(item.errors / item.count) * 100}
                          color="error"
                          sx={{
                            height: 4,
                            borderRadius: 2,
                            backgroundColor: alpha(theme.palette.error.main, 0.1),
                            '& .MuiLinearProgress-bar': {
                              borderRadius: 2,
                            },
                          }}
                        />
                      </Box>
                      <Typography variant="caption" color="error.main" sx={{ minWidth: 'fit-content' }}>
                        {item.errors} errors ({((item.errors / item.count) * 100).toFixed(1)}%)
                      </Typography>
                    </Box>
                  )}
                </Box>
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
};

export default EndpointsChart;