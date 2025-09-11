import React from 'react';
import {
  Box,
  Typography,
  Button,
  alpha,
} from '@mui/material';
import {
  Timeline,
  Refresh,
} from '@mui/icons-material';

const EmptyState = ({
  onRefresh,
  message = "No data available for the selected time range and filters"
}) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 3,
        textAlign: 'center',
        minHeight: 300,
      }}
    >
      <Box
        sx={{
          p: 3,
          borderRadius: 3,
          backgroundColor: (theme) => alpha(theme.palette.primary.main, 0.1),
          mb: 3,
        }}
      >
        <Timeline sx={{ fontSize: 48, color: 'primary.main' }} />
      </Box>

      <Typography variant="h6" gutterBottom fontWeight={600}>
        No Data Found
      </Typography>

      <Typography
        variant="body1"
        color="text.secondary"
        sx={{ maxWidth: 400, mb: 3 }}
      >
        {message}
      </Typography>

      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ maxWidth: 500, mb: 4 }}
      >
        Try adjusting your time range or filters.
        <br />
        For larger intervals, it may take some time until data is first processed.
        <br />
        Also check that your services are sending telemetry data to Malti.
      </Typography>

      <Button
        variant="outlined"
        startIcon={<Refresh />}
        onClick={onRefresh}
        sx={{ borderRadius: 2 }}
      >
        Refresh Data
      </Button>
    </Box>
  );
};

export default EmptyState;