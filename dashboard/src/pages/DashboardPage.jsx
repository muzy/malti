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
import { useAuth } from '../contexts/AuthContext';
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
  
  const [data, setData] = useState([]);
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
  const [endpointContexts, setEndpointContexts] = useState({}); // Store endpoint-context mapping from unfiltered data

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

      // Check if this is an unfiltered request (no filters applied)
      const isUnfilteredRequest = !selectedService && !selectedNode && !selectedEndpoint && !selectedMethod && !selectedContext;

      // Use realtime endpoint for "Last hour" selection, regular aggregate for others
      const endpoint = selectedTimeRange.hours === 1
        ? '/api/v1/metrics/aggregate/realtime'
        : '/api/v1/metrics/aggregate';

      const response = await makeAuthenticatedRequest(`${endpoint}?${params}`);
      
      if (response.ok) {
        const result = await response.json();
        setData(result || []);
        
        // Extract unique services, endpoints, methods, and contexts
        const uniqueServices = [...new Set(result.map(item => item.service))].sort();
        const uniqueEndpoints = [...new Set(result.map(item => item.endpoint))].sort();
        const uniqueMethods = [...new Set(result.map(item => item.method))].sort();

        setServices(uniqueServices);
        setEndpoints(uniqueEndpoints);
        setMethods(uniqueMethods);

        // If this is an unfiltered request, store endpoint-context mapping for later use
        if (isUnfilteredRequest) {
          const endpointContextMap = {};
          result.forEach(item => {
            if (item.endpoint && item.context) {
              if (!endpointContextMap[item.endpoint]) {
                endpointContextMap[item.endpoint] = new Set();
              }
              endpointContextMap[item.endpoint].add(item.context);
            }
          });
          // Convert Sets to Arrays for easier use
          const finalMap = {};
          Object.keys(endpointContextMap).forEach(endpoint => {
            finalMap[endpoint] = Array.from(endpointContextMap[endpoint]).sort();
          });
          setEndpointContexts(finalMap);
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
    setSelectedMethod(method); // Set the method from the clicked endpoint
    setSelectedContext(''); // Reset context when endpoint changes

    // Find the service that corresponds to this endpoint
    const endpointData = data.find(item => item.endpoint === endpoint);
    if (endpointData && endpointData.service) {
      setSelectedService(endpointData.service);
    }
  };

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
              endpointContexts={endpointContexts}
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
                {data.length === 0 ? (
                  <EmptyState onRefresh={fetchData} />
                ) : (
                  <>
                    {/* System Overview and Metrics - Same Width */}
                    <Box sx={{ mb: 4 }}>
                      <StatusIndicator data={data} />
                    </Box>
                    
                    <Box sx={{ mb: 4 }}>
                      <MetricsCards data={data} timeRange={selectedTimeRange} />
                    </Box>

                    {/* Response Time Chart - Full Width, Double Height */}
                    <Box sx={{ mb: 4 }}>
                      <LatencyChart data={data} height={700} timeRange={selectedTimeRange} />
                    </Box>

                  {/* Charts Layout - 50% Endpoints, 25% Status Distribution, 25% Consumer */}
                  <Grid container spacing={3} alignItems="flex-start" sx={{ width: '100%' }}>
                    {/* Left Column - Endpoints Chart (50% width) */}
                    <Grid item xs={12} lg={6} sx={{ width: '100%', maxWidth: 'none' }}>
                      <EndpointsChart data={data} onEndpointClick={handleEndpointClick} />
                    </Grid>

                    {/* Middle Column - Status Distribution Chart (25% width) */}
                    <Grid item xs={12} lg={3} sx={{ width: '100%', maxWidth: 'none' }}>
                      <ErrorRateChart data={data} />
                    </Grid>

                    {/* Right Column - Consumer Chart (25% width) */}
                    <Grid item xs={12} lg={3} sx={{ width: '100%', maxWidth: 'none' }}>
                      <ConsumerChart data={data} />
                    </Grid>
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