import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  alpha,
} from '@mui/material';
import { AutoGraph } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login, error } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!apiKey.trim()) return;

    setIsLoading(true);
    const success = await login(apiKey.trim());
    setIsLoading(false);
  };

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: (theme) => 
          theme.palette.mode === 'dark' 
            ? 'linear-gradient(135deg, #0a1929 0%, #1e293b 100%)'
            : `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(theme.palette.secondary.main, 0.1)} 100%)`,
        p: 2,
      }}
    >
      <Box sx={{ width: '100%', maxWidth: 450 }}>
        <Paper 
          elevation={8}
          sx={{ 
            borderRadius: 3,
            overflow: 'hidden',
            width: '100%',
          }}
        >
          <Card sx={{ border: 'none', boxShadow: 'none' }}>
            <CardContent sx={{ p: 6 }}>
              {/* Header */}
              <Box sx={{ textAlign: 'center', mb: 4 }}>
                <Box
                  sx={{
                    p: 2,
                    mb: 2,
                    borderRadius: 3,
                    backgroundColor: (theme) => alpha(theme.palette.primary.main, 0.2),
                    display: 'inline-flex',
                    border: '1px solid',
                    borderColor: (theme) => alpha(theme.palette.primary.main, 0.3),
                  }}
                >
                  <AutoGraph sx={{ fontSize: 40, color: 'primary.main' }} />
                </Box>
                <Typography variant="h4" component="h1" gutterBottom fontWeight={600}>
                  Malti
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Minimalistic Application Load Telemetry Insights
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Enter your API key to access the telemetry dashboard
                </Typography>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                  {error}
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="API Key"
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  margin="normal"
                  required
                  autoFocus
                  placeholder="Enter your user API key"
                  helperText="Your API key will be stored in LocalStorage and cleared on logout"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    },
                  }}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={isLoading || !apiKey.trim()}
                  sx={{ 
                    mt: 3, 
                    mb: 2,
                    py: 1.5,
                    borderRadius: 2,
                    fontWeight: 600,
                  }}
                  startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : null}
                >
                  {isLoading ? 'Authenticating...' : 'Login'}
                </Button>
              </Box>

              <Box 
                sx={{ 
                  mt: 3, 
                  p: 2.5, 
                  bgcolor: (theme) => alpha(theme.palette.grey[500], 0.08),
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  <strong>Note:</strong> This dashboard requires a user API key with metrics permissions.
                  Contact your administrator if you don't have access.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Paper>
      </Box>
    </Box>
  );
};

export default LoginPage;