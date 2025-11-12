import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// Type definitions
export interface Department {
  id: number;
  name: string;
  zone: string;
  officer?: {
    id: string;
    username: string;
    first_name: string;
    last_name: string;
  };
  avg_resolution_days?: number;
}

export interface ComplaintData {
  title: string;
  description: string;
  category?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  department_id?: number;
  location?: string;
  incident_latitude?: number;
  incident_longitude?: number;
  incident_address?: string;
  incident_landmark?: string;
  gps_accuracy?: number;
  location_method?: 'gps' | 'manual' | 'address';
  area_type?: 'residential' | 'commercial' | 'industrial' | 'public' | 'road' | 'park' | 'other';
  contact_method?: 'email' | 'phone' | 'both';
  audio_file?: File;
  image_file?: File;
  text?: string;
}

export interface ComplaintResponse {
  id: number;
  title: string;
  description: string;
  status: 'submitted' | 'pending' | 'in_progress' | 'resolved' | 'rejected' | 'closed';
  priority: string;
  urgency_level?: string;
  department: Department;
  created_at: string;
  updated_at: string;
  complaint_id?: string;
  tracking_id?: string;
  ai_enhanced_description?: string;
  ai_assigned_department?: string;
  ai_priority_score?: number;
  processed_text?: string;
  estimated_resolution_days?: number;
  sentiment?: number;
  ai_confidence_score?: number;
  ai_processed_text?: string;
}

export interface AuthRequest {
  username?: string;
  email?: string;
  phone?: string;
  phone_number?: string;
  identifier?: string;
  password?: string;
  otp?: string;
  first_name?: string;
  last_name?: string;
  user_id?: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  token?: string;
  access?: string;
  refresh?: string;
  refresh_token?: string;
  user?: {
    id: string;
    username: string;
    email: string;
    phone?: string;
    first_name?: string;
    last_name?: string;
    is_verified: boolean;
  };
  user_id?: string;
  otp_sent?: boolean;
  otp_sent_to?: string;
  requires_otp?: boolean;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/complaints/api',
  timeout: 30000,
  withCredentials: true, // Enable sending cookies with requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token manager
export class TokenManager {
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

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = TokenManager.getRefreshToken();
        if (refreshToken) {
          const response = await api.post('/auth/refresh/', {
            refresh: refreshToken,
          });

          const newTokens = response.data;
          TokenManager.setTokens(newTokens);
          return api(originalRequest);
        }
      } catch (refreshError) {
        TokenManager.clearTokens();
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// File validation utility
export const validateFile = (file: File): string | null => {
  const maxSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'audio/mp3',
    'audio/wav',
    'audio/ogg',
    'application/pdf',
    'text/plain',
  ];

  if (file.size > maxSize) {
    return 'File size must be less than 10MB';
  }

  if (!allowedTypes.includes(file.type)) {
    return 'File type not supported';
  }

  return null;
};

// Error handler
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

// Main API service
export const apiService = {
  // Generic HTTP methods
  get: <T = any>(url: string, params?: any): Promise<T> => {
    return api.get(url, { params }).then(response => response.data);
  },

  post: <T = any>(url: string, data?: any, config?: any): Promise<T> => {
    return api.post(url, data, config).then(response => response.data);
  },

  put: <T = any>(url: string, data?: any): Promise<T> => {
    return api.put(url, data).then(response => response.data);
  },

  patch: <T = any>(url: string, data?: any): Promise<T> => {
    return api.patch(url, data).then(response => response.data);
  },

  delete: <T = any>(url: string): Promise<T> => {
    return api.delete(url).then(response => response.data);
  },

  upload: <T = any>(url: string, formData: FormData): Promise<T> => {
    return api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }).then(response => response.data);
  },

  // Health check
  getHealth: (): Promise<{ status: string; timestamp: string }> => {
    return apiService.get('/health/');
  },

  // Department methods
  getDepartments: (): Promise<Department[]> => {
    return apiService.get('/departments/');
  },

  getDepartment: (id: number): Promise<Department> => {
    return apiService.get(`/departments/${id}/`);
  },

  // Complaint methods
  getComplaints: (params?: any): Promise<ComplaintResponse[]> => {
    return apiService.get('/complaints/', params);
  },

  getComplaint: (id: number): Promise<ComplaintResponse> => {
    return apiService.get(`/complaints/${id}/`);
  },

  submitComplaint: (data: ComplaintData): Promise<ComplaintResponse> => {
    const formData = new FormData();
    
    // Add required text fields
    formData.append('title', data.title);
    formData.append('description', data.description);
    formData.append('priority', data.priority);
    
    // Add optional fields if they exist
    if (data.category) {
      formData.append('category', data.category);
    }
    
    if (data.contact_method) {
      formData.append('contact_method', data.contact_method);
    }
    
    if (data.department_id) {
      formData.append('department_id', data.department_id.toString());
    }
    
    if (data.location) {
      formData.append('location', data.location);
    }
    
    // GPS coordinates
    if (data.incident_latitude) {
      formData.append('incident_latitude', data.incident_latitude.toString());
    }
    
    if (data.incident_longitude) {
      formData.append('incident_longitude', data.incident_longitude.toString());
    }
    
    if (data.incident_address) {
      formData.append('incident_address', data.incident_address);
    }
    
    if (data.incident_landmark) {
      formData.append('incident_landmark', data.incident_landmark);
    }
    
    if (data.gps_accuracy) {
      formData.append('gps_accuracy', data.gps_accuracy.toString());
    }
    
    if (data.location_method) {
      formData.append('location_method', data.location_method);
    }
    
    if (data.area_type) {
      formData.append('area_type', data.area_type);
    }
    
    // Add files
    if (data.audio_file) {
      formData.append('audio_file', data.audio_file);
    }
    
    if (data.image_file) {
      formData.append('image_file', data.image_file);
    }
    
    if (data.text) {
      formData.append('text', data.text);
    }

    return apiService.upload('/complaints/', formData);
  },

  updateComplaint: (id: number, data: Partial<ComplaintData>): Promise<ComplaintResponse> => {
    return apiService.patch(`/complaints/${id}/`, data);
  },

  deleteComplaint: (id: number): Promise<void> => {
    return apiService.delete(`/complaints/${id}/`);
  },

  // Authentication methods
  login: (credentials: AuthRequest): Promise<AuthResponse> => {
    return apiService.post('/auth/login/', credentials);
  },

  register: (userData: AuthRequest): Promise<AuthResponse> => {
    return apiService.post('/auth/register/', userData);
  },

  verifyOTP: (data: { phone: string; otp: string }): Promise<AuthResponse> => {
    return apiService.post('/auth/verify-otp/', data);
  },

  sendOTP: (data: { phone: string }): Promise<AuthResponse> => {
    return apiService.post('/auth/send-otp/', data);
  },

  logout: (): Promise<void> => {
    return apiService.post('/auth/logout/').finally(() => {
      TokenManager.clearTokens();
    });
  },

  refreshToken: (refreshToken: string): Promise<AuthTokens> => {
    return apiService.post('/auth/refresh/', { refresh: refreshToken });
  },

  // Analytics methods
  getAnalytics: (params?: any): Promise<any> => {
    return apiService.get('/analytics/', params);
  },

  // File download
  downloadFile: async (url: string, filename?: string): Promise<void> => {
    const response = await api.get(url, { responseType: 'blob' });
    const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },
};

export default api;