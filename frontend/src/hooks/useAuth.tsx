// Authentication Hook for SmartGriev
// Provides user authentication state and methods

import { useState, useEffect, useContext, createContext, ReactNode } from 'react';
import { message } from 'antd';
import { apiService } from '@/services/api';

interface User {
  id: string;
  username: string;
  email: string;
  phone?: string;
  firstName?: string;
  lastName?: string;
  isVerified: boolean;
  role: 'citizen' | 'admin' | 'officer';
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => void;
  register: (data: RegisterData) => Promise<boolean>;
  verifyOTP: (phone: string, otp: string) => Promise<boolean>;
  refreshToken: () => Promise<boolean>;
}

interface LoginCredentials {
  username?: string;
  password?: string;
  phone?: string;
  email?: string;
}

interface RegisterData {
  username: string;
  email: string;
  phone: string;
  firstName: string;
  lastName: string;
  password: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setIsLoading(false);
        return;
      }

      // Verify token with backend
      const response = await apiService.get('/auth/verify-token/');
      if (response.data.valid) {
        setUser(response.data.user);
        setIsAuthenticated(true);
      } else {
        // Token invalid, clear storage
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      // Clear invalid tokens
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      let endpoint = '/auth/login/';
      let payload = credentials;

      // Determine login method (email, phone, or username)
      if (credentials.phone && !credentials.password) {
        endpoint = '/auth/request-otp/';
        payload = { phone: credentials.phone };
      }

      const response = await apiService.post(endpoint, payload);
      
      if (response.data.success) {
        if (response.data.token) {
          // Direct login successful
          localStorage.setItem('authToken', response.data.token);
          if (response.data.refresh_token) {
            localStorage.setItem('refreshToken', response.data.refresh_token);
          }
          setUser(response.data.user);
          setIsAuthenticated(true);
          message.success('Login successful!');
          return true;
        } else if (response.data.otp_sent) {
          // OTP sent, need verification
          message.success('OTP sent to your phone. Please verify to continue.');
          return false; // Indicates OTP verification needed
        }
      }
      
      message.error(response.data.message || 'Login failed');
      return false;
    } catch (error: any) {
      console.error('Login error:', error);
      const errorMessage = error.response?.data?.message || 'Login failed. Please try again.';
      message.error(errorMessage);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const verifyOTP = async (phone: string, otp: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      const response = await apiService.post('/auth/verify-otp/', {
        phone,
        otp,
      });

      if (response.data.success) {
        localStorage.setItem('authToken', response.data.token);
        if (response.data.refresh_token) {
          localStorage.setItem('refreshToken', response.data.refresh_token);
        }
        setUser(response.data.user);
        setIsAuthenticated(true);
        message.success('Phone verified successfully!');
        return true;
      }
      
      message.error(response.data.message || 'OTP verification failed');
      return false;
    } catch (error: any) {
      console.error('OTP verification error:', error);
      const errorMessage = error.response?.data?.message || 'OTP verification failed';
      message.error(errorMessage);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterData): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      const response = await apiService.post('/auth/register/', data);
      
      if (response.data.success) {
        message.success('Registration successful! Please verify your phone number.');
        return true;
      }
      
      message.error(response.data.message || 'Registration failed');
      return false;
    } catch (error: any) {
      console.error('Registration error:', error);
      const errorMessage = error.response?.data?.message || 'Registration failed';
      message.error(errorMessage);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const refreshToken = async (): Promise<boolean> => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) return false;

      const response = await apiService.post('/auth/refresh-token/', {
        refresh_token: refreshToken,
      });

      if (response.data.success) {
        localStorage.setItem('authToken', response.data.token);
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  };

  const logout = () => {
    // Clear local storage
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    
    // Reset state
    setUser(null);
    setIsAuthenticated(false);
    
    // Optional: Call logout endpoint
    apiService.post('/auth/logout/').catch(console.error);
    
    message.success('Logged out successfully');
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    register,
    verifyOTP,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// HOC for protected routes
export const withAuth = <P extends object>(Component: React.ComponentType<P>) => {
  return (props: P) => {
    const { isAuthenticated, isLoading } = useAuth();
    
    if (isLoading) {
      return <div>Loading...</div>; // Or your loading component
    }
    
    if (!isAuthenticated) {
      return <div>Please log in to access this page.</div>; // Or redirect to login
    }
    
    return <Component {...props} />;
  };
};

export default useAuth;