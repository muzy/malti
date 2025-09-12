import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  Chip,
  LinearProgress,
  Collapse,
  IconButton,
  alpha,
  useTheme,
} from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { getErrorRateColor } from '../utils/statusUtils';

const StatusDistributionChart = ({ data }) => {
  const theme = useTheme();
  const [expandedServices, setExpandedServices] = useState(new Set());

  const prepareServiceData = () => {
    if (!data || data.length === 0) return [];

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

    // Prepare service data for visualization
    return Array.from(serviceMap.entries())
      .map(([service, statusMap]) => {
        const statuses = Array.from(statusMap.entries())
          .map(([status, count]) => ({
            status,
            count,
            color: statusColors[status] || theme.palette.grey.main,
          }))
          .sort((a, b) => a.status - b.status);

        const totalRequests = Array.from(statusMap.values()).reduce((sum, count) => sum + count, 0);

        // Group by status ranges
        const success = statuses
          .filter(s => s.status >= 200 && s.status < 300)
          .reduce((sum, s) => sum + s.count, 0);

        const warning = statuses
          .filter(s => s.status >= 300 && s.status < 400)
          .reduce((sum, s) => sum + s.count, 0);

        const error = statuses
          .filter(s => s.status >= 400)
          .reduce((sum, s) => sum + s.count, 0);

        return {
          service,
          totalRequests,
          success,
          warning,
          error,
          statuses,
        };
      })
      .sort((a, b) => b.totalRequests - a.totalRequests); // Sort services by total requests
  };

  const serviceData = prepareServiceData();

  const toggleServiceExpansion = (service, category) => {
    const key = `${service}-${category}`;
    setExpandedServices(prev => {
      const newSet = new Set(prev);
      if (newSet.has(key)) {
        newSet.delete(key);
      } else {
        newSet.add(key);
      }
      return newSet;
    });
  };

  const isServiceExpanded = (service, category) => {
    return expandedServices.has(`${service}-${category}`);
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
        Status Distribution by Service
      </Typography>

      {serviceData.length === 0 ? (
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
            {serviceData.map((item, index) => (
              <ListItem
                key={index}
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
                  {/* Header with service name and stats */}
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
                      {item.service}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Typography
                        variant="body2"
                        color={getErrorRateColor((item.error / item.totalRequests) * 100)}
                        fontWeight={600}
                      >
                        {((item.error / item.totalRequests) * 100).toFixed(1)}% errors
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        in
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {item.totalRequests.toLocaleString()} requests
                      </Typography>
                    </Box>
                  </Box>

                  {/* Status progress bars */}
                  <Box sx={{ mb: 1 }}>
                    {/* Success bar (2xx) */}
                    {item.success > 0 && (
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
                          onClick={() => toggleServiceExpansion(item.service, 'success')}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography
                              variant="caption"
                              color="success.main"
                              fontWeight={500}
                              className="status-label"
                            >
                              Success (2xx)
                            </Typography>
                            <IconButton size="small" sx={{ p: 0 }}>
                              {isServiceExpanded(item.service, 'success') ? (
                                <ExpandLess sx={{ fontSize: 16, color: 'success.main' }} />
                              ) : (
                                <ExpandMore sx={{ fontSize: 16, color: 'success.main' }} />
                              )}
                            </IconButton>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {item.success.toLocaleString()}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={(item.success / item.totalRequests) * 100}
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
                          onClick={() => toggleServiceExpansion(item.service, 'success')}
                        />
                        <Collapse in={isServiceExpanded(item.service, 'success')}>
                          <Box sx={{ mt: 1, ml: 2 }}>
                            {item.statuses
                              .filter(s => s.status >= 200 && s.status < 300)
                              .sort((a, b) => a.status - b.status)
                              .map(status => (
                                <Box
                                  key={status.status}
                                  sx={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    mb: 0.5,
                                    pl: 1,
                                    borderLeft: `2px solid ${theme.palette.success.main}`,
                                  }}
                                >
                                  <Typography variant="caption" color="text.secondary">
                                    HTTP {status.status}
                                  </Typography>
                                  <Typography variant="caption" color="success.main" fontWeight={500}>
                                    {status.count.toLocaleString()}
                                  </Typography>
                                </Box>
                              ))}
                          </Box>
                        </Collapse>
                      </Box>
                    )}

                    {/* Warning bar (3xx) */}
                    {item.warning > 0 && (
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
                          onClick={() => toggleServiceExpansion(item.service, 'warning')}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography
                              variant="caption"
                              color="warning.main"
                              fontWeight={500}
                              className="status-label"
                            >
                              Warning (3xx)
                            </Typography>
                            <IconButton size="small" sx={{ p: 0 }}>
                              {isServiceExpanded(item.service, 'warning') ? (
                                <ExpandLess sx={{ fontSize: 16, color: 'warning.main' }} />
                              ) : (
                                <ExpandMore sx={{ fontSize: 16, color: 'warning.main' }} />
                              )}
                            </IconButton>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {item.warning.toLocaleString()}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={(item.warning / item.totalRequests) * 100}
                          sx={{
                            height: 6,
                            borderRadius: 3,
                            backgroundColor: alpha(theme.palette.warning.main, 0.1),
                            '& .MuiLinearProgress-bar': {
                              borderRadius: 3,
                              backgroundColor: theme.palette.warning.main,
                            },
                            cursor: 'pointer',
                            '&:hover': {
                              opacity: 0.8,
                            },
                          }}
                          onClick={() => toggleServiceExpansion(item.service, 'warning')}
                        />
                        <Collapse in={isServiceExpanded(item.service, 'warning')}>
                          <Box sx={{ mt: 1, ml: 2 }}>
                            {item.statuses
                              .filter(s => s.status >= 300 && s.status < 400)
                              .sort((a, b) => a.status - b.status)
                              .map(status => (
                                <Box
                                  key={status.status}
                                  sx={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    mb: 0.5,
                                    pl: 1,
                                    borderLeft: `2px solid ${theme.palette.warning.main}`,
                                  }}
                                >
                                  <Typography variant="caption" color="text.secondary">
                                    HTTP {status.status}
                                  </Typography>
                                  <Typography variant="caption" color="warning.main" fontWeight={500}>
                                    {status.count.toLocaleString()}
                                  </Typography>
                                </Box>
                              ))}
                          </Box>
                        </Collapse>
                      </Box>
                    )}

                    {/* Error bar (4xx/5xx) */}
                    {item.error > 0 && (
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
                          onClick={() => toggleServiceExpansion(item.service, 'error')}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography
                              variant="caption"
                              color="error.main"
                              fontWeight={500}
                              className="status-label"
                            >
                              Error (4xx/5xx)
                            </Typography>
                            <IconButton size="small" sx={{ p: 0 }}>
                              {isServiceExpanded(item.service, 'error') ? (
                                <ExpandLess sx={{ fontSize: 16, color: 'error.main' }} />
                              ) : (
                                <ExpandMore sx={{ fontSize: 16, color: 'error.main' }} />
                              )}
                            </IconButton>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {item.error.toLocaleString()}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={(item.error / item.totalRequests) * 100}
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
                          onClick={() => toggleServiceExpansion(item.service, 'error')}
                        />
                        <Collapse in={isServiceExpanded(item.service, 'error')}>
                          <Box sx={{ mt: 1, ml: 2 }}>
                            {item.statuses
                              .filter(s => s.status >= 400)
                              .sort((a, b) => a.status - b.status)
                              .map(status => (
                                <Box
                                  key={status.status}
                                  sx={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    mb: 0.5,
                                    pl: 1,
                                    borderLeft: `2px solid ${theme.palette.error.main}`,
                                  }}
                                >
                                  <Typography variant="caption" color="text.secondary">
                                    HTTP {status.status}
                                  </Typography>
                                  <Typography variant="caption" color="error.main" fontWeight={500}>
                                    {status.count.toLocaleString()}
                                  </Typography>
                                </Box>
                              ))}
                          </Box>
                        </Collapse>
                      </Box>
                    )}
                  </Box>
                </Box>
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
};

export default StatusDistributionChart;