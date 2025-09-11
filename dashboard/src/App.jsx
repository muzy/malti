import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9', // Light blue for dark theme
      dark: '#42a5f5',
      light: '#e3f2fd',
    },
    secondary: {
      main: '#f48fb1', // Pink accent
      dark: '#f06292',
      light: '#fce4ec',
    },
    background: {
      default: '#0a1929', // Dark blue-black
      paper: '#1e293b', // Slightly lighter blue-black
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0bec5',
    },
    divider: '#334155',
    success: {
      main: '#66bb6a',
    },
    warning: {
      main: '#ffa726',
    },
    error: {
      main: '#f44336',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
      letterSpacing: '-0.02em',
    },
    h6: {
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    body1: {
      letterSpacing: '0.00938em',
    },
    body2: {
      letterSpacing: '0.01071em',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage: 'linear-gradient(180deg, #0a1929 0%, #1e293b 100%)',
          backgroundAttachment: 'fixed',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
          borderRadius: 16,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(148, 163, 184, 0.1)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 10,
          fontWeight: 600,
          letterSpacing: '0.02em',
        },
        contained: {
          boxShadow: '0 4px 14px rgba(144, 202, 249, 0.4)',
          '&:hover': {
            boxShadow: '0 6px 20px rgba(144, 202, 249, 0.6)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(148, 163, 184, 0.1)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 600,
        },
      },
    },
  },
});

const AppContent = () => {
  const { isAuthenticated } = useAuth();

  return (
    <>
      <CssBaseline />
      {isAuthenticated ? <DashboardPage /> : <LoginPage />}
    </>
  );
};

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;