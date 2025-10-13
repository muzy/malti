import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  LinearProgress,
  Collapse,
  IconButton,
  alpha,
  useTheme,
} from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { getErrorRateColor } from '../utils/statusUtils';

const ConsumerChart = ({ data }) => {
  const theme = useTheme();
  const [expandedConsumers, setExpandedConsumers] = useState(new Set());

  const toggleConsumerExpansion = (consumer) => {
    setExpandedConsumers(prev => {
      const newSet = new Set(prev);
      if (newSet.has(consumer)) {
        newSet.delete(consumer);
      } else {
        newSet.add(consumer);
      }
      return newSet;
    });
  };

  const isConsumerExpanded = (consumer) => {
    return expandedConsumers.has(consumer);
  };

  return (
    <Paper
      sx={{
        p: 3,
        borderRadius: 2,
        width: '100%',
        maxWidth: 'none',
        minWidth: 0,
        background: (theme) => theme.palette.background.paper,
      }}
    >
      <Typography variant="h6" gutterBottom fontWeight={600}>
        Request Distribution by Consumer
      </Typography>

      {!Array.isArray(data) || data.length === 0 ? (
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
            {data.map((item) => {
              const successCount = item.total_requests - item.error_count;
              
              return (
                <ListItem
                  key={item.consumer}
                  sx={{
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
                    {/* Header with consumer name and stats */}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                      <Typography
                        variant="body1"
                        sx={{
                          fontWeight: 600,
                          maxWidth: { xs: 200, md: 400 },
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {item.consumer}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Typography
                          variant="body2"
                          color={getErrorRateColor(item.error_rate)}
                          fontWeight={600}
                        >
                          {item.error_rate.toFixed(1)}% errors
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          in
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {item.total_requests.toLocaleString()} requests
                        </Typography>
                      </Box>
                    </Box>

                    {/* Progress bars */}
                    <Box sx={{ mb: 1 }}>
                      {/* Success bar (successful requests) */}
                      {successCount > 0 && (
                        <Box sx={{ mb: 1 }}>
                          <Box
                            sx={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              mb: 0.5,
                              cursor: 'pointer',
                              '&:hover': {
                                '& .status-label': { opacity: 0.8 },
                              },
                            }}
                            onClick={() => toggleConsumerExpansion(item.consumer)}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography
                                variant="caption"
                                color="success.main"
                                fontWeight={500}
                                className="status-label"
                              >
                                Successful Requests
                              </Typography>
                              <IconButton size="small" sx={{ p: 0 }}>
                                {isConsumerExpanded(item.consumer) ? (
                                  <ExpandLess sx={{ fontSize: 16, color: 'success.main' }} />
                                ) : (
                                  <ExpandMore sx={{ fontSize: 16, color: 'success.main' }} />
                                )}
                              </IconButton>
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                              {successCount.toLocaleString()}
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={(successCount / item.total_requests) * 100}
                            sx={{
                              height: 6,
                              borderRadius: 3,
                              backgroundColor: alpha(theme.palette.success.main, 0.1),
                              '& .MuiLinearProgress-bar': {
                                borderRadius: 3,
                                backgroundColor: theme.palette.success.main,
                              },
                              cursor: 'pointer',
                              '&:hover': {
                                opacity: 0.8,
                              },
                            }}
                            onClick={() => toggleConsumerExpansion(item.consumer)}
                          />
                          <Collapse in={isConsumerExpanded(item.consumer)}>
                            <Box sx={{ mt: 1, ml: 2 }}>
                              <Box
                                sx={{
                                  display: 'flex',
                                  justifyContent: 'space-between',
                                  mb: 0.5,
                                  pl: 1,
                                  borderLeft: `2px solid ${theme.palette.success.main}`,
                                }}
                              >
                                <Typography variant="caption" color="text.secondary">
                                  Success Rate
                                </Typography>
                                <Typography variant="caption" color="success.main" fontWeight={500}>
                                  {((successCount / item.total_requests) * 100).toFixed(1)}%
                                </Typography>
                              </Box>
                            </Box>
                          </Collapse>
                        </Box>
                      )}

                      {/* Error bar (failed requests) */}
                      {item.error_count > 0 && (
                        <Box sx={{ mb: 1 }}>
                          <Box
                            sx={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              mb: 0.5,
                              cursor: 'pointer',
                              '&:hover': {
                                '& .status-label': { opacity: 0.8 },
                              },
                            }}
                            onClick={() => toggleConsumerExpansion(item.consumer)}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography
                                variant="caption"
                                color="error.main"
                                fontWeight={500}
                                className="status-label"
                              >
                                Failed Requests
                              </Typography>
                              <IconButton size="small" sx={{ p: 0 }}>
                                {isConsumerExpanded(item.consumer) ? (
                                  <ExpandLess sx={{ fontSize: 16, color: 'error.main' }} />
                                ) : (
                                  <ExpandMore sx={{ fontSize: 16, color: 'error.main' }} />
                                )}
                              </IconButton>
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                              {item.error_count.toLocaleString()}
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={item.error_rate}
                            sx={{
                              height: 6,
                              borderRadius: 3,
                              backgroundColor: alpha(theme.palette.error.main, 0.1),
                              '& .MuiLinearProgress-bar': {
                                borderRadius: 3,
                                backgroundColor: theme.palette.error.main,
                              },
                              cursor: 'pointer',
                              '&:hover': {
                                opacity: 0.8,
                              },
                            }}
                            onClick={() => toggleConsumerExpansion(item.consumer)}
                          />
                          <Collapse in={isConsumerExpanded(item.consumer)}>
                            <Box sx={{ mt: 1, ml: 2 }}>
                              <Box
                                sx={{
                                  display: 'flex',
                                  justifyContent: 'space-between',
                                  mb: 0.5,
                                  pl: 1,
                                  borderLeft: `2px solid ${theme.palette.error.main}`,
                                }}
                              >
                                <Typography variant="caption" color="text.secondary">
                                  Error Rate
                                </Typography>
                                <Typography variant="caption" color="error.main" fontWeight={500}>
                                  {item.error_rate.toFixed(1)}%
                                </Typography>
                              </Box>
                            </Box>
                          </Collapse>
                        </Box>
                      )}
                    </Box>
                  </Box>
                </ListItem>
              );
            })}
          </List>
        </Box>
      )}
    </Paper>
  );
};

export default ConsumerChart;
