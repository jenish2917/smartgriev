/**
 * Core Service Implementations
 * Concrete implementations of core infrastructure services
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { 
  ILogger, 
  IHttpClient, 
  IStorageService, 
  ICacheService, 
  IValidationService,
  IErrorHandlingService 
} from '@/types/core';
import { ApplicationLogger } from '@/core/errorHandling';
import { getApiBaseUrl } from '@/config/api.config';

/**
 * Console Logger Implementation
 */
export class ConsoleLogger implements ILogger {
  private isDevelopment = import.meta.env.DEV;

  debug(message: string, ...args: any[]): void {
    if (this.isDevelopment) {
      console.debug(`[DEBUG] ${message}`, ...args);
    }
  }

  info(message: string, ...args: any[]): void {
    console.info(`[INFO] ${message}`, ...args);
  }

  warn(message: string, ...args: any[]): void {
    console.warn(`[WARN] ${message}`, ...args);
  }

  error(message: string, error?: Error, ...args: any[]): void {
    console.error(`[ERROR] ${message}`, error, ...args);
  }
}

/**
 * Axios HTTP Client Implementation
 */
export class AxiosHttpClient implements IHttpClient {
  private client: AxiosInstance;

  constructor(baseURL?: string) {
    this.client = axios.create({
      baseURL: baseURL || getApiBaseUrl(),
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor for auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Try to refresh token
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              // Use correct token refresh endpoint
              const response = await axios.post('/api/token/refresh/', {
                refresh: refreshToken,
              });
              
              localStorage.setItem('access_token', response.data.access);
              
              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${response.data.access}`;
                return this.client.request(error.config);
              }
            } catch (refreshError) {
              // Refresh failed, redirect to login
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              window.location.href = '/login';
            }
          } else {
            // No refresh token, redirect to login
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config);
    return response.data;
  }

  async patch<T>(url: string, data?: any, config?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.patch(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url, config);
    return response.data;
  }
}

/**
 * Local Storage Service Implementation
 */
export class LocalStorageService implements IStorageService {
  getItem<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error(`Error reading from localStorage:`, error);
      return null;
    }
  }

  setItem<T>(key: string, value: T): void {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error writing to localStorage:`, error);
    }
  }

  removeItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error(`Error removing from localStorage:`, error);
    }
  }

  clear(): void {
    try {
      localStorage.clear();
    } catch (error) {
      console.error(`Error clearing localStorage:`, error);
    }
  }
}

/**
 * In-Memory Cache Service Implementation
 */
export class InMemoryCacheService implements ICacheService {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();
  private defaultTtl = 5 * 60 * 1000; // 5 minutes

  get<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    if (Date.now() - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  set<T>(key: string, value: T, ttlMs = this.defaultTtl): void {
    this.cache.set(key, {
      data: value,
      timestamp: Date.now(),
      ttl: ttlMs,
    });
  }

  delete(key: string): void {
    this.cache.delete(key);
  }

  clear(pattern?: string): void {
    if (pattern) {
      const keys = Array.from(this.cache.keys()).filter(key =>
        key.includes(pattern)
      );
      keys.forEach(key => this.cache.delete(key));
    } else {
      this.cache.clear();
    }
  }

  // Cleanup expired entries periodically
  private cleanup(): void {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > value.ttl) {
        this.cache.delete(key);
      }
    }
  }

  constructor() {
    // Run cleanup every 5 minutes
    setInterval(() => this.cleanup(), 5 * 60 * 1000);
  }
}

/**
 * Validation Service Implementation
 */
export class ValidationService implements IValidationService {
  async validate<T>(data: T, schema: any): Promise<T> {
    // Implementation would depend on chosen validation library (e.g., Joi, Yup, Zod)
    // For now, just return data as-is
    return data;
  }

  validateRequired<T>(data: T, fields: (keyof T)[]): void {
    for (const field of fields) {
      if (!data[field]) {
        throw new Error(`Field '${String(field)}' is required`);
      }
    }
  }
}

/**
 * Error Handling Service Implementation
 */
export class ErrorHandlingService implements IErrorHandlingService {
  handleError(error: any): never {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data;
      
      let message = 'An error occurred';
      
      if (typeof data === 'object' && data.detail) {
        message = data.detail;
      } else if (typeof data === 'object' && data.message) {
        message = data.message;
      } else if (typeof data === 'string') {
        message = data;
      } else if (status === 401) {
        message = 'Authentication required';
      } else if (status === 403) {
        message = 'Permission denied';
      } else if (status === 404) {
        message = 'Resource not found';
      } else if (status === 500) {
        message = 'Server error occurred';
      }
      
      throw this.createError(message, error.code, status);
    } else if (error.request) {
      // Network error
      throw this.createError('Network error. Please check your connection.', 'NETWORK_ERROR');
    } else {
      // Other error
      throw this.createError(error.message || 'An unexpected error occurred');
    }
  }

  createError(message: string, code?: string, status?: number): Error {
    const error = new Error(message);
    (error as any).code = code;
    (error as any).status = status;
    return error;
  }

  isNetworkError(error: any): boolean {
    return error.code === 'NETWORK_ERROR' || !error.response;
  }

  isAuthenticationError(error: any): boolean {
    return error.status === 401;
  }
}

/**
 * Service Factory for creating core services
 */
export class CoreServiceFactory {
  static createLogger(): ILogger {
    return new ApplicationLogger();
  }

  static createHttpClient(): IHttpClient {
    return new AxiosHttpClient();
  }

  static createStorageService(): IStorageService {
    return new LocalStorageService();
  }

  static createCacheService(): ICacheService {
    return new InMemoryCacheService();
  }

  static createValidationService(): IValidationService {
    return new ValidationService();
  }

  static createErrorHandlingService(): IErrorHandlingService {
    return new ErrorHandlingService();
  }
}