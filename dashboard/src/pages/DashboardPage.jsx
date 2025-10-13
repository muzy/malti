import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  CircularProgress,
  Alert,
  Container,
  Toolbar,
  alpha,
} from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import AppNavbar from '../components/AppNavbar';
import FiltersPanel from '../components/FiltersPanel';
import MetricsCards from '../components/MetricsCards';
import LatencyChart from '../components/LatencyChart';
import EndpointsChart from '../components/EndpointsChart';
import ConsumerChart from '../components/ConsumerChart';
import EmptyState from '../components/EmptyState';
import StatusIndicator from '../components/StatusIndicator';
import ErrorRateChart from '../components/StatusDistributionChart';

const TIME_RANGES = [
  { label: 'Last hour', hours: 1, shortLabel: '1h' },
  { label: 'Last 6 hours', hours: 6, shortLabel: '6h' },
  { label: 'Last 24 hours', hours: 24, shortLabel: '24h' },
  { label: 'Last 7 days', hours: 24 * 7, shortLabel: '7d' },
  { label: 'Last 30 days', hours: 24 * 30, shortLabel: '30d' },
  { label: 'Last 3 months', hours: 24 * 30 * 3, shortLabel: '3m' },
  { label: 'Last 6 months', hours: 24 * 30 * 6, shortLabel: '6m' },
  { label: 'Last 1 year', hours: 24 * 365, shortLabel: '1y' },
];

const DashboardPage = () => {
  const { makeAuthenticatedRequest } = useAuth();
  
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState(TIME_RANGES[0]); // Default to 1 hour
  const [selectedService, setSelectedService] = useState('');
  const [selectedNode, setSelectedNode] = useState('');
  const [selectedEndpoint, setSelectedEndpoint] = useState('');
  const [selectedMethod, setSelectedMethod] = useState('');
  const [selectedContext, setSelectedContext] = useState('');
  const [services, setServices] = useState([]);
  const [endpoints, setEndpoints] = useState([]);
  const [methods, setMethods] = useState([]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const endTime = new Date();
      const startTime = new Date(endTime.getTime() - selectedTimeRange.hours * 60 * 60 * 1000);
      
      const params = new URLSearchParams({
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
      });

      if (selectedService) params.append('service', selectedService);
      if (selectedNode) params.append('node', selectedNode);
      if (selectedEndpoint) params.append('endpoint', selectedEndpoint);
      if (selectedMethod) params.append('method', selectedMethod);
      if (selectedContext) params.append('context', selectedContext);

      // Use realtime endpoint for "Last hour" selection, regular aggregate for others
      const endpoint = selectedTimeRange.hours === 1
        ? '/api/v1/metrics/aggregate/realtime'
        : '/api/v1/metrics/aggregate';

      const response = await makeAuthenticatedRequest(`${endpoint}?${params}`);
      
      if (response.ok) {
        const result = await response.json();
        setData(result);
        
        // Extract unique services, endpoints, methods from the aggregated data
        if (Array.isArray(result.endpoints) && result.endpoints.length > 0) {
          const uniqueEndpoints = [...new Set(result.endpoints.map(item => item.endpoint))].sort();
          const uniqueMethods = [...new Set(result.endpoints.map(item => item.method))].sort();
          const uniqueServices = [...new Set(result.endpoints.map(item => item.service))].sort();
          
          setEndpoints(uniqueEndpoints);
          setMethods(uniqueMethods);
          setServices(uniqueServices);
        }
        
        // Fallback: if no endpoints data, try to get services from status_distribution
        if (Array.isArray(result.status_distribution) && result.status_distribution.length > 0) {
          // Only set services if we haven't already set them from endpoints
          const currentServices = [...new Set(result.status_distribution.map(item => item.service))].sort();
          setServices(prevServices => prevServices.length === 0 ? currentServices : prevServices);
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || `Failed to fetch metrics data (${response.status})`);
      }
    } catch (error) {
      setError(`Network error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [selectedTimeRange, selectedService, selectedNode, selectedEndpoint, selectedMethod, selectedContext, makeAuthenticatedRequest]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleEndpointClick = (endpoint, method) => {
    setSelectedEndpoint(endpoint);
    setSelectedMethod(method);
    setSelectedContext('');

    // Find the service that corresponds to this endpoint from endpoints data
    if (data && data.endpoints && data.endpoints.length > 0) {
      const matchingEndpoint = data.endpoints.find(item => 
        item.endpoint === endpoint && item.method === method
      );
      if (matchingEndpoint) {
        setSelectedService(matchingEndpoint.service);
      }
    }
  };

  // Check if time_series has any actual data (not just gap-filled empty buckets)
  const hasActualTimeSeriesData = data && 
    Array.isArray(data.time_series) && 
    data.time_series.length > 0 && 
    data.time_series.some(item => item.total_requests > 0);

  const hasData = data && (
    hasActualTimeSeriesData ||
    (data.system_overview && data.system_overview.total_requests > 0) ||
    (Array.isArray(data.endpoints) && data.endpoints.length > 0) ||
    (Array.isArray(data.status_distribution) && data.status_distribution.length > 0) ||
    (Array.isArray(data.consumers) && data.consumers.length > 0)
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppNavbar />
      
      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          backgroundColor: (theme) => 
            theme.vars
              ? `rgba(${theme.vars.palette.background.defaultChannel} / 1)`
              : alpha(theme.palette.background.default, 1),
          minHeight: '100vh',
          overflow: 'auto',
        }}
      >
        {/* Add toolbar spacing to account for fixed AppBar */}
        <Toolbar />
        
        <Container maxWidth={false} sx={{ py: 4, px: { xs: 2, sm: 3, md: 4, lg: 6 } }}>
            {/* Filters Panel */}
            <FiltersPanel
              selectedService={selectedService}
              setSelectedService={setSelectedService}
              selectedNode={selectedNode}
              setSelectedNode={setSelectedNode}
              selectedEndpoint={selectedEndpoint}
              setSelectedEndpoint={setSelectedEndpoint}
              selectedMethod={selectedMethod}
              setSelectedMethod={setSelectedMethod}
              selectedContext={selectedContext}
              setSelectedContext={setSelectedContext}
              selectedTimeRange={selectedTimeRange}
              setSelectedTimeRange={setSelectedTimeRange}
              services={services}
              endpoints={endpoints}
              methods={methods}
              data={data}
            />

            {/* Error Alert */}
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {/* Loading State */}
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                <CircularProgress size={48} />
              </Box>
            )}

            {/* Content */}
            {!loading && (
              <>
                {!hasData ? (
                  <EmptyState onRefresh={fetchData} />
                ) : (
                  <>
                    {/* System Overview and Metrics - Same Width */}
                    {data.system_overview && data.system_overview.total_requests > 0 && (
                      <Box sx={{ mb: 4 }}>
                        <StatusIndicator data={data.system_overview} />
                      </Box>
                    )}
                    
                    {data.metrics_summary && data.metrics_summary.total_requests > 0 && (
                      <Box sx={{ mb: 4 }}>
                        <MetricsCards 
                          data={data.metrics_summary} 
                          timeSeries={data.time_series}
                        />
                      </Box>
                    )}

                    {/* Response Time Chart - Full Width, Double Height */}
                    {Array.isArray(data.time_series) && data.time_series.length > 0 && (
                      <Box sx={{ mb: 4 }}>
                        <LatencyChart 
                          data={data.time_series} 
                          height={700} 
                          timeRange={selectedTimeRange} 
                        />
                      </Box>
                    )}

                  {/* Charts Layout - 50% Endpoints, 25% Status Distribution, 25% Consumer */}
                  <Grid container spacing={3} alignItems="flex-start" sx={{ width: '100%' }}>
                    {/* Left Column - Endpoints Chart (50% width) */}
                    {Array.isArray(data.endpoints) && data.endpoints.length > 0 && (
                      <Grid item xs={12} lg={6} sx={{ width: '100%', maxWidth: 'none' }}>
                        <EndpointsChart data={data.endpoints} onEndpointClick={handleEndpointClick} />
                      </Grid>
                    )}

                    {/* Middle Column - Status Distribution Chart (25% width) */}
                    {Array.isArray(data.status_distribution) && data.status_distribution.length > 0 && (
                      <Grid item xs={12} lg={3} sx={{ width: '100%', maxWidth: 'none' }}>
                        <ErrorRateChart data={data.status_distribution} />
                      </Grid>
                    )}

                    {/* Right Column - Consumer Chart (25% width) */}
                    {Array.isArray(data.consumers) && data.consumers.length > 0 && (
                      <Grid item xs={12} lg={3} sx={{ width: '100%', maxWidth: 'none' }}>
                        <ConsumerChart data={data.consumers} />
                      </Grid>
                    )}
                  </Grid>
                  </>
                )}
              </>
            )}
        </Container>
      </Box>
    </Box>
  );
};

export default DashboardPage;
