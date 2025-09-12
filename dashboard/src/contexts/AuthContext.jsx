import React, { useState, useCallback, useEffect } from 'react';
import { updateThresholds } from '../utils/statusUtils';
import { AuthContext } from '../hooks/useAuth';

const STORAGE_KEY = 'malti_api_key';

export const AuthProvider = ({ children }) => {
  const [apiKey, setApiKey] = useState(() => {
    // Try to load from localStorage on initialization
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch {
      return null;
    }
  });
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState(null);

  const login = useCallback(async (key) => {
    try {
      const response = await fetch(`${window.location.origin}/api/v1/auth/test`, {
        method: 'GET',
        headers: {
          'X-API-Key': key,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setApiKey(key);
        setUser(data.user);
        setIsAuthenticated(true);
        setError(null);

        // Update global thresholds with values from API
        if (data.thresholds) {
          updateThresholds(data.thresholds);
        }
        
        // Cache the key in localStorage
        try {
          localStorage.setItem(STORAGE_KEY, key);
        } catch (e) {
          console.warn('Failed to cache API key:', e);
        }
        
        return true;
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || `Authentication failed (${response.status})`);
        
        // If unauthorized, clear cached key
        if (response.status === 401 || response.status === 403) {
          try {
            localStorage.removeItem(STORAGE_KEY);
          } catch (e) {
            console.warn('Failed to clear cached API key:', e);
          }
        }
        
        return false;
      }
    } catch (error) {
      setError(`Network error: ${error.message}`);
      return false;
    }
  }, []);

  // Auto-login on mount if we have a cached key
  useEffect(() => {
    if (apiKey && !isAuthenticated) {
      login(apiKey);
    }
  }, [apiKey, isAuthenticated, login]);

  const logout = useCallback(() => {
    setApiKey(null);
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
    
    // Clear cached key
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      console.warn('Failed to clear cached API key:', e);
    }
  }, []);

  const makeAuthenticatedRequest = useCallback(async (url, options = {}) => {
    if (!apiKey) {
      throw new Error('No API key available');
    }

    const headers = {
      'X-API-Key': apiKey,
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Ensure URL is absolute
    const fullUrl = url.startsWith('http') ? url : `${window.location.origin}${url}`;

    const response = await fetch(fullUrl, {
      ...options,
      headers,
    });

    // If unauthorized, clear cached key and logout
    if (response.status === 401 || response.status === 403) {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (e) {
        console.warn('Failed to clear cached API key:', e);
      }
      logout();
    }

    return response;
  }, [apiKey, logout]);

  const value = {
    apiKey,
    user,
    isAuthenticated,
    error,
    login,
    logout,
    makeAuthenticatedRequest,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};