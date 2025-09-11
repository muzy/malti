import React from 'react';
import {
  Paper,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  alpha,
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Circle } from '@mui/icons-material';

const COLORS = [
  '#1976d2', // Primary blue
  '#2e7d32', // Green
  '#ed6c02', // Orange
  '#d32f2f', // Red
  '#7b1fa2', // Purple
  '#00796b', // Teal
  '#f57c00', // Amber
  '#c2185b', // Pink
  '#5d4037', // Brown
  '#455a64', // Blue grey
];

const ConsumerChart = ({ data }) => {
  const prepareConsumerData = () => {
    if (!data || data.length === 0) return [];
    
    const consumerMap = new Map();
    
    data.forEach(item => {
      if (item.consumer) {
        const current = consumerMap.get(item.consumer) || { requests: 0, errors: 0 };
        current.requests += item.count_requests;
        if (item.status >= 400 && item.status !== 401) {
          current.errors += item.count_requests;
        }
        consumerMap.set(item.consumer, current);
      }
    });
    
    return Array.from(consumerMap.entries())
      .map(([consumer, stats]) => ({
        name: consumer,
        value: stats.requests,
        errors: stats.errors,
        errorRate: stats.requests > 0 ? (stats.errors / stats.requests) * 100 : 0,
      }))
      .sort((a, b) => b.value - a.value);
  };

  const consumerData = prepareConsumerData();
  const totalRequests = consumerData.reduce((sum, item) => sum + item.value, 0);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Paper sx={{ p: 2, border: '1px solid', borderColor: 'divider' }}>
          <Typography variant="subtitle2" gutterBottom>
            {data.name}
          </Typography>
          <Typography variant="body2">
            Requests: {data.value.toLocaleString()} ({((data.value / totalRequests) * 100).toFixed(1)}%)
          </Typography>
          <Typography variant="body2" color="error">
            Errors: {data.errors.toLocaleString()} ({data.errorRate.toFixed(1)}%)
          </Typography>
        </Paper>
      );
    }
    return null;
  };

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    if (percent < 0.05) return null; // Hide labels for slices < 5%
    
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight={600}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
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
      
      {consumerData.length === 0 ? (
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
          {/* Pie Chart */}
          <Box sx={{ height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={consumerData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={renderCustomizedLabel}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {consumerData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={COLORS[index % COLORS.length]} 
                    />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </Box>
          
          {/* Legend List */}
          <Box sx={{ mt: 2, maxHeight: 120, overflow: 'auto' }}>
            <List dense>
              {consumerData.map((item, index) => (
                <ListItem key={item.name} sx={{ py: 0.5 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <Circle 
                      sx={{ 
                        color: COLORS[index % COLORS.length],
                        fontSize: 16,
                      }} 
                    />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Typography variant="body2" fontWeight={500}>
                          {item.name}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip
                            label={`${item.value.toLocaleString()} req`}
                            size="small"
                            variant="outlined"
                          />
                          {item.errors > 0 && (
                            <Chip
                              label={`${item.errorRate.toFixed(1)}% err`}
                              size="small"
                              color="error"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default ConsumerChart;