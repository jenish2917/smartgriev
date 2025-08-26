import { apiService } from './api';
import {
  User,
  AuthTokens,
  LoginCredentials,
  RegisterData,
} from '@/types';

export const authService = {
  // Login
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    return apiService.post<AuthTokens>('/token/', credentials);
  },

  // Register
  register: async (data: RegisterData): Promise<User> => {
    return apiService.post<User>('/auth/register/', data);
  },

  // Get current user profile
  getProfile: async (): Promise<User> => {
    return apiService.get<User>('/auth/profile/');
  },

  // Update user profile
  updateProfile: async (data: Partial<User>): Promise<User> => {
    return apiService.patch<User>('/auth/profile/', data);
  },

  // Change password
  changePassword: async (data: {
    old_password: string;
    new_password: string;
  }): Promise<{ message: string }> => {
    return apiService.post('/auth/change-password/', data);
  },

  // Request password reset
  requestPasswordReset: async (email: string): Promise<{ message: string }> => {
    return apiService.post('/auth/password-reset/', { email });
  },

  // Confirm password reset
  confirmPasswordReset: async (data: {
    token: string;
    new_password: string;
  }): Promise<{ message: string }> => {
    return apiService.post('/auth/password-reset/confirm/', data);
  },

  // Verify email
  verifyEmail: async (data: {
    user_id: number;
    token: string;
  }): Promise<{ message: string }> => {
    return apiService.post('/auth/verify-email/', data);
  },

  // Resend verification email
  resendVerification: async (email: string): Promise<{ message: string }> => {
    return apiService.post('/auth/resend-verification/', { email });
  },

  // Refresh token
  refreshToken: async (refresh: string): Promise<AuthTokens> => {
    return apiService.post<AuthTokens>('/token/refresh/', { refresh });
  },

  // Logout (optional - mainly clears local tokens)
  logout: async (): Promise<void> => {
    // If backend has a logout endpoint, call it here
    // await apiService.post('/auth/logout/');
  },
};
