import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Chip,
  Button,
} from '@mui/material';
import { LogoutOutlined } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const AppNavbar = () => {
  const { user, logout } = useAuth();

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: 'background.paper',
        color: 'text.primary',
        boxShadow: 1,
      }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          noWrap
          component="div"
          sx={{
            flexGrow: 1,
            fontWeight: 600,
          }}
        >
          Malti Dashboard
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            label={`${user?.name || 'Unknown User'}`}
            variant="outlined"
            size="small"
            color="primary"
          />
          <Button
            variant="outlined"
            size="small"
            startIcon={<LogoutOutlined />}
            onClick={logout}
            sx={{ ml: 1 }}
          >
            Logout
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default AppNavbar;