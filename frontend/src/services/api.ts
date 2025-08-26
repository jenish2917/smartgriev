import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { AuthTokens } from '@/types';
import { useNavigate } from 'react-router-dom';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

class TokenManager {
  private static ACCESS_TOKEN_KEY = 'smartgriev_access_token';
  private static REFRESH_TOKEN_KEY = 'smartgriev_refresh_token';

  static getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static setTokens(tokens: AuthTokens): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.access);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, tokens.refresh);
  }

  static clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  static isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
}

api.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    const navigate = useNavigate();

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = TokenManager.getRefreshToken();
        if (refreshToken) {
          const response = await axios.post('/api/token/refresh/', {
            refresh: refreshToken,
          });

          const newTokens: AuthTokens = response.data;
          TokenManager.setTokens(newTokens);

          originalRequest.headers.Authorization = `Bearer ${newTokens.access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        TokenManager.clearTokens();
        navigate('/login');
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

if (import.meta.env.PROD) {
  api.interceptors.request.use(
    (config) => {
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  api.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
}

export const apiService = {
  get: async <T = any>(url: string, params?: any): Promise<T> => {
    const response = await api.get(url, { params });
    return response.data;
  },

  post: async <T = any>(url: string, data?: any, config?: any): Promise<T> => {
    const response = await api.post(url, data, config);
    return response.data;
  },

  put: async <T = any>(url: string, data?: any): Promise<T> => {
    const response = await api.put(url, data);
    return response.data;
  },

  patch: async <T = any>(url: string, data?: any): Promise<T> => {
    const response = await api.patch(url, data);
    return response.data;
  },

  delete: async <T = any>(url: string): Promise<T> => {
    const response = await api.delete(url);
    return response.data;
  },

  upload: async <T = any>(url: string, formData: FormData): Promise<T> => {
    const response = await api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  download: async (url: string, filename?: string): Promise<void> => {
    const response = await api.get(url, {
      responseType: 'blob',
    });

    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },
};

export const handleApiError = (error: AxiosError): string => {
  if (error.response?.data) {
    const errorData = error.response.data as any;
    
    if (typeof errorData === 'object' && errorData.detail) {
      return errorData.detail;
    }
    
    if (typeof errorData === 'object' && errorData.non_field_errors) {
      return Array.isArray(errorData.non_field_errors) 
        ? errorData.non_field_errors[0] 
        : errorData.non_field_errors;
    }

    if (typeof errorData === 'object') {
      const firstKey = Object.keys(errorData)[0];
      if (firstKey && Array.isArray(errorData[firstKey])) {
        return `${firstKey}: ${errorData[firstKey][0]}`;
      }
    }

    if (typeof errorData === 'string') {
      return errorData;
    }
  }

  if (error.code === 'NETWORK_ERROR') {
    return 'Network error. Please check your connection.';
  }

  if (error.code === 'TIMEOUT') {
    return 'Request timeout. Please try again.';
  }

  return error.message || 'An unexpected error occurred.';
};

export { TokenManager };

export default api;