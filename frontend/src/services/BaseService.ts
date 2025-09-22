import { AxiosError, AxiosResponse } from 'axios';
import { PaginatedResponse, ApiResponse } from '@/types';

/**
 * Custom error class for service layer errors
 */
export class ServiceError extends Error {
  constructor(
    message: string,
    public readonly code?: string,
    public readonly status?: number,
    public readonly details?: any
  ) {
    super(message);
    this.name = 'ServiceError';
  }
}

/**
 * Base service class with common functionality
 * All service classes should extend this base class
 */
export abstract class BaseService {
  protected readonly endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  /**
   * Handle API errors and convert them to ServiceError
   */
  protected handleError(error: AxiosError): never {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data as any;
      
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
      
      throw new ServiceError(message, error.code, status, data);
    } else if (error.request) {
      // Network error
      throw new ServiceError('Network error. Please check your connection.', 'NETWORK_ERROR');
    } else {
      // Other error
      throw new ServiceError(error.message || 'An unexpected error occurred');
    }
  }

  /**
   * Validate request data before sending to API
   */
  protected validateRequest<T>(data: T, requiredFields: (keyof T)[]): void {
    for (const field of requiredFields) {
      if (!data[field]) {
        throw new ServiceError(`Field '${String(field)}' is required`);
      }
    }
  }

  /**
   * Transform API response to expected format
   */
  protected transformResponse<T>(response: AxiosResponse<T>): T {
    return response.data;
  }

  /**
   * Transform paginated API response
   */
  protected transformPaginatedResponse<T>(
    response: AxiosResponse<PaginatedResponse<T>>
  ): PaginatedResponse<T> {
    return response.data;
  }

  /**
   * Build query string from parameters
   */
  protected buildQueryString(params: Record<string, any>): string {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, String(value));
      }
    });
    
    const queryString = queryParams.toString();
    return queryString ? `?${queryString}` : '';
  }

  /**
   * Log service operations for debugging
   */
  protected log(operation: string, data?: any): void {
    if (import.meta.env.DEV) {
      console.log(`[${this.constructor.name}] ${operation}`, data);
    }
  }

  /**
   * Handle file upload data
   */
  protected createFormData(data: Record<string, any>): FormData {
    const formData = new FormData();
    
    Object.entries(data).forEach(([key, value]) => {
      if (value instanceof File) {
        formData.append(key, value);
      } else if (value instanceof FileList) {
        Array.from(value).forEach((file, index) => {
          formData.append(`${key}[${index}]`, file);
        });
      } else if (typeof value === 'object' && value !== null) {
        formData.append(key, JSON.stringify(value));
      } else if (value !== undefined && value !== null) {
        formData.append(key, String(value));
      }
    });
    
    return formData;
  }

  /**
   * Retry failed requests with exponential backoff
   */
  protected async retryRequest<T>(
    operation: () => Promise<T>,
    maxRetries = 3,
    baseDelay = 1000
  ): Promise<T> {
    let lastError: Error;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        
        if (attempt === maxRetries) {
          break;
        }
        
        // Exponential backoff
        const delay = baseDelay * Math.pow(2, attempt - 1);
        await new Promise(resolve => setTimeout(resolve, delay));
        
        this.log(`Retry attempt ${attempt} after ${delay}ms delay`);
      }
    }
    
    throw lastError!;
  }

  /**
   * Cache management for GET requests
   */
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>();

  protected getCached<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;
    
    if (Date.now() - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data;
  }

  protected setCached<T>(key: string, data: T, ttlMs = 5 * 60 * 1000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttlMs,
    });
  }

  protected clearCache(pattern?: string): void {
    if (pattern) {
      const keys = Array.from(this.cache.keys()).filter(key => 
        key.includes(pattern)
      );
      keys.forEach(key => this.cache.delete(key));
    } else {
      this.cache.clear();
    }
  }
}

export default BaseService;