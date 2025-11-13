import { apiClient, handleApiError } from '@/lib/axios';
import type { LoginCredentials, RegisterData, AuthResponse, User } from '@/types';

/**
 * Authentication API calls
 */
export const authApi = {
  // Login
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login/', credentials);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Register
  register: async (data: RegisterData): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/register/', data);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Logout
  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout/');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Get current user
  getCurrentUser: async (): Promise<User> => {
    try {
      const response = await apiClient.get<User>('/auth/user/');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Verify email
  verifyEmail: async (token: string): Promise<void> => {
    try {
      await apiClient.post('/auth/verify-email/', { token });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Verify mobile OTP
  verifyMobile: async (otp: string): Promise<void> => {
    try {
      await apiClient.post('/auth/verify-mobile/', { otp });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Resend OTP
  resendOTP: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/resend-otp/');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Send OTP for login
  sendOTP: async (mobileNumber: string): Promise<{ message: string }> => {
    try {
      const response = await apiClient.post<{ message: string }>('/auth/send-otp/', {
        mobile_number: mobileNumber
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Verify OTP and login
  verifyOTP: async (mobileNumber: string, otp: string): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/verify-otp/', {
        mobile_number: mobileNumber,
        otp
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Forgot password
  forgotPassword: async (email: string): Promise<void> => {
    try {
      await apiClient.post('/auth/forgot-password/', { email });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Reset password
  resetPassword: async (token: string, password: string): Promise<void> => {
    try {
      await apiClient.post('/auth/reset-password/', { token, password });
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
