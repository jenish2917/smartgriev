import { useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuthStore } from '@/store/authStore';
import { logger } from '@/utils/logger';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Refresh token 5 minutes before expiry (access token lifetime is 15 minutes)
const REFRESH_INTERVAL = 10 * 60 * 1000; // 10 minutes

/**
 * Hook to automatically refresh access token before it expires
 */
export const useTokenRefresh = () => {
  const { isAuthenticated, clearAuth } = useAuthStore();
  const intervalRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    if (!isAuthenticated) {
      // Clear interval if user logs out
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      return;
    }

    const refreshToken = async () => {
      try {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) {
          logger.warn('[TOKEN-REFRESH] No refresh token found');
          return;
        }

        logger.log('[TOKEN-REFRESH] Proactively refreshing token...');
        const response = await axios.post(`${API_BASE_URL}/api/auth/token/refresh/`, {
          refresh,
        });

        const { access, refresh: newRefresh } = response.data;
        localStorage.setItem('access_token', access);
        if (newRefresh) {
          localStorage.setItem('refresh_token', newRefresh);
        }
        
        logger.log('[TOKEN-REFRESH] Token refreshed successfully');
      } catch (error) {
        logger.error('[TOKEN-REFRESH] Failed to refresh token:', error);
        // If refresh fails, clear auth and redirect to login
        clearAuth();
        window.location.href = '/login';
      }
    };

    // Initial refresh when component mounts (if needed)
    const checkAndRefresh = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        // Decode JWT to check expiry (simple check without jwt-decode library)
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          const expiryTime = payload.exp * 1000; // Convert to milliseconds
          const now = Date.now();
          const timeUntilExpiry = expiryTime - now;
          
          // If token expires in less than 5 minutes, refresh now
          if (timeUntilExpiry < 5 * 60 * 1000) {
            logger.log('[TOKEN-REFRESH] Token expiring soon, refreshing now...');
            await refreshToken();
          }
        } catch (error) {
          logger.error('[TOKEN-REFRESH] Failed to decode token:', error);
        }
      }
    };

    // Check on mount
    checkAndRefresh();

    // Set up periodic refresh
    intervalRef.current = setInterval(refreshToken, REFRESH_INTERVAL);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isAuthenticated, clearAuth]);
};
