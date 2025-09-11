import React from 'react';
import {
  Paper,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  ButtonGroup,
  Button,
  Box,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';

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

const FiltersPanel = ({
  selectedService,
  setSelectedService,
  selectedNode,
  setSelectedNode,
  selectedEndpoint,
  setSelectedEndpoint,
  selectedMethod,
  setSelectedMethod,
  selectedContext,
  setSelectedContext,
  selectedTimeRange,
  setSelectedTimeRange,
  services,
  endpoints,
  methods,
  endpointContexts,
  data,
}) => {
  const getFilteredNodes = () => {
    if (!selectedService) return [];
    return [...new Set(
      data
        .filter(item => item.service === selectedService)
        .map(item => item.node)
        .filter(Boolean)
    )];
  };

  const getFilteredContexts = () => {
    if (!selectedEndpoint) return [];

    // If we have endpoint-context mapping from unfiltered data, use it
    if (endpointContexts && endpointContexts[selectedEndpoint]) {
      return endpointContexts[selectedEndpoint];
    }

    // Fallback to filtering current data
    return [...new Set(
      data
        .filter(item => item.endpoint === selectedEndpoint && item.context)
        .map(item => item.context)
    )].sort();
  };

  const activeFiltersCount = [selectedService, selectedNode, selectedEndpoint, selectedMethod, selectedContext].filter(Boolean).length;

  const clearAllFilters = () => {
    setSelectedService('');
    setSelectedNode('');
    setSelectedEndpoint('');
    setSelectedMethod('');
    setSelectedContext('');
  };

  return (
    <Paper 
      sx={{ 
        p: 3, 
        mb: 3,
        borderRadius: 2,
        background: (theme) => theme.palette.background.paper,
      }}
    >
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6" fontWeight={600}>
          Filters & Controls
        </Typography>
        {activeFiltersCount > 0 && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip 
              label={`${activeFiltersCount} filter${activeFiltersCount > 1 ? 's' : ''} active`}
              size="small"
              color="primary"
              variant="outlined"
            />
            <Tooltip title="Clear all filters">
              <IconButton
                size="small"
                onClick={clearAllFilters}
                sx={{
                  color: 'primary.main',
                  '&:hover': {
                    backgroundColor: 'primary.light',
                    color: 'white',
                  },
                }}
              >
                <ClearIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        )}
      </Box>
      
      <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 3, flexWrap: 'wrap' }}>
        {/* Service Selector */}
        <Box>
          <Typography variant="subtitle2" gutterBottom sx={{ color: 'text.secondary', mb: 1 }}>
            Service
          </Typography>
          <Select
            value={selectedService}
            onChange={(e) => {
              setSelectedService(e.target.value);
              setSelectedNode(''); // Reset node when service changes
            }}
            displayEmpty
            size="small"
            sx={{ width: 180, minWidth: 180 }}
            renderValue={(selected) => {
              if (!selected) {
                return <em style={{ color: '#b0bec5', fontStyle: 'normal' }}>All Services</em>;
              }
              return selected;
            }}
          >
            <MenuItem value="">All Services</MenuItem>
            {services.map(service => (
              <MenuItem key={service} value={service}>
                {service}
              </MenuItem>
            ))}
          </Select>
        </Box>
        
        {/* Node Selector */}
        <Box>
          <Typography variant="subtitle2" gutterBottom sx={{ color: 'text.secondary', mb: 1 }}>
            Node
          </Typography>
          <Select
            value={selectedNode}
            onChange={(e) => setSelectedNode(e.target.value)}
            disabled={!selectedService}
            displayEmpty
            size="small"
            sx={{ width: 180, minWidth: 180 }}
            renderValue={(selected) => {
              if (!selected) {
                return <em style={{ color: '#b0bec5', fontStyle: 'normal' }}>All Nodes</em>;
              }
              return selected;
            }}
          >
            <MenuItem value="">All Nodes</MenuItem>
            {getFilteredNodes().map(node => (
              <MenuItem key={node} value={node}>
                {node}
              </MenuItem>
            ))}
          </Select>
        </Box>
        
        {/* Endpoint Selector */}
        <Box>
          <Typography variant="subtitle2" gutterBottom sx={{ color: 'text.secondary', mb: 1 }}>
            Endpoint
          </Typography>
          <Select
            value={selectedEndpoint}
            onChange={(e) => {
              const selectedEndpointValue = e.target.value;
              setSelectedEndpoint(selectedEndpointValue);
              setSelectedContext(''); // Reset context when endpoint changes

              // Find the service that corresponds to this endpoint
              if (selectedEndpointValue) {
                const endpointData = data.find(item => item.endpoint === selectedEndpointValue);
                if (endpointData && endpointData.service) {
                  setSelectedService(endpointData.service);
                }
              }
            }}
            displayEmpty
            size="small"
            sx={{ width: 400, minWidth: 400 }}
            MenuProps={{
              PaperProps: {
                sx: {
                  maxWidth: 500,
                  '& .MuiMenuItem-root': {
                    whiteSpace: 'nowrap',
                  },
                },
              },
            }}
            renderValue={(selected) => {
              if (!selected) {
                return <em style={{ color: '#b0bec5', fontStyle: 'normal' }}>All Endpoints</em>;
              }
              return (
                <Typography 
                  sx={{ 
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    maxWidth: 350,
                  }}
                >
                  {selected}
                </Typography>
              );
            }}
          >
            <MenuItem value="">All Endpoints</MenuItem>
            {endpoints.map(endpoint => (
              <MenuItem key={endpoint} value={endpoint}>
                <Typography 
                  sx={{ 
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                  }}
                >
                  {endpoint}
                </Typography>
              </MenuItem>
            ))}
          </Select>
        </Box>

        {/* Method Selector */}
        <Box>
          <Typography variant="subtitle2" gutterBottom sx={{ color: 'text.secondary', mb: 1 }}>
            Method
          </Typography>
          <Select
            value={selectedMethod}
            onChange={(e) => setSelectedMethod(e.target.value)}
            displayEmpty
            size="small"
            sx={{ width: 160, minWidth: 160 }}
            renderValue={(selected) => {
              if (!selected) {
                return <em style={{ color: '#b0bec5', fontStyle: 'normal' }}>All Methods</em>;
              }
              return selected;
            }}
          >
            <MenuItem value="">All Methods</MenuItem>
            {methods.map(method => (
              <MenuItem key={method} value={method}>
                {method}
              </MenuItem>
            ))}
          </Select>
        </Box>

        {/* Context Selector - Only show when endpoint is selected and there are contexts available */}
        {selectedEndpoint && getFilteredContexts().length > 0 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom sx={{ color: 'text.secondary', mb: 1 }}>
              Context
            </Typography>
            <Select
              value={selectedContext}
              onChange={(e) => setSelectedContext(e.target.value)}
              displayEmpty
              size="small"
              sx={{ width: 200, minWidth: 200 }}
              renderValue={(selected) => {
                if (!selected) {
                  return <em style={{ color: '#b0bec5', fontStyle: 'normal' }}>All Contexts</em>;
                }
                return selected;
              }}
            >
              <MenuItem value="">All Contexts</MenuItem>
              {getFilteredContexts().map(context => (
                <MenuItem key={context} value={context}>
                  {context}
                </MenuItem>
              ))}
            </Select>
          </Box>
        )}

        {/* Spacer to push time range buttons to the right */}
        <Box sx={{ flex: 1 }} />
        
        {/* Time Range Buttons */}
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
          <Typography variant="subtitle2" gutterBottom sx={{ color: 'text.secondary', mb: 1 }}>
            Time Range
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'flex-end' }}>
            {TIME_RANGES.map((range) => (
              <Button
                key={range.label}
                size="small"
                variant={selectedTimeRange.label === range.label ? 'contained' : 'outlined'}
                onClick={() => setSelectedTimeRange(range)}
                sx={{ 
                  minWidth: 'auto', 
                  px: 2,
                  borderRadius: 2,
                  fontWeight: selectedTimeRange.label === range.label ? 600 : 500,
                }}
              >
                {range.shortLabel}
              </Button>
            ))}
          </Box>
        </Box>
      </Box>
    </Paper>
  );
};

export default FiltersPanel;