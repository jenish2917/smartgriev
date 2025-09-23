/**
 * Repository Implementations
 * Data access layer following Repository pattern
 */

import { 
  IAuthRepository,
  IComplaintRepository,
  IAnalyticsRepository,
  IChatbotRepository,
  INotificationRepository,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  User,
  ProfileUpdateData,
  ComplaintQueryParams,
  PaginatedResponse,
  Complaint,
  CreateComplaintData,
  UpdateComplaintData,
  ComplaintHistory,
  DashboardMetrics,
  TrendParams,
  TrendData,
  PerformanceParams,
  PerformanceData,
  GeospatialParams,
  GeospatialData,
  ChatContext,
  ChatResponse,
  ChatMessage,
  QuickReply,
  NotificationParams,
  Notification,
  NotificationSettings
} from '@/types/core';
import { InjectableService } from '@/core/container';

/**
 * Authentication Repository Implementation
 */
export class AuthRepository extends InjectableService implements IAuthRepository {
  private readonly endpoint = '/auth';

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const httpClient = this.getService('httpClient');
    const logger = this.getService('logger');
    const storage = this.getService('storage');

    try {
      logger.info('Attempting user login');
      
      const response = await httpClient.post<AuthResponse>(`${this.endpoint}/login/`, {
        username: credentials.username,
        password: credentials.password,
      });

      // Store tokens
      storage.setItem('access_token', response.accessToken);
      storage.setItem('refresh_token', response.refreshToken);
      
      if (credentials.rememberMe) {
        storage.setItem('remember_me', true);
      }

      logger.info('Login successful');
      return response;
    } catch (error) {
      logger.error('Login failed', error as Error);
      throw this.getService('errorHandler').handleError(error);
    }
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const httpClient = this.getService('httpClient');
    const logger = this.getService('logger');
    const validation = this.getService('validation');

    try {
      logger.info('Attempting user registration');
      
      // Validate required fields
      validation.validateRequired(userData, ['username', 'email', 'password', 'firstName', 'lastName']);

      const response = await httpClient.post<AuthResponse>(`${this.endpoint}/register/`, userData);
      
      logger.info('Registration successful');
      return response;
    } catch (error) {
      logger.error('Registration failed', error as Error);
      throw this.getService('errorHandler').handleError(error);
    }
  }

  async logout(): Promise<void> {
    const httpClient = this.getService('httpClient');
    const logger = this.getService('logger');
    const storage = this.getService('storage');

    try {
      const refreshToken = storage.getItem<string>('refresh_token');
      
      if (refreshToken) {
        await httpClient.post(`${this.endpoint}/logout/`, {
          refresh_token: refreshToken,
        });
      }

      // Clear stored tokens
      storage.removeItem('access_token');
      storage.removeItem('refresh_token');
      storage.removeItem('remember_me');

      logger.info('Logout successful');
    } catch (error) {
      logger.error('Logout failed', error as Error);
      // Don't throw on logout errors, just clear local tokens
      storage.removeItem('access_token');
      storage.removeItem('refresh_token');
    }
  }

  async refreshToken(): Promise<AuthResponse> {
    const httpClient = this.getService('httpClient');
    const storage = this.getService('storage');

    const refreshToken = storage.getItem<string>('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await httpClient.post<AuthResponse>(`${this.endpoint}/refresh/`, {
      refresh: refreshToken,
    });

    // Update stored tokens
    storage.setItem('access_token', response.accessToken);
    storage.setItem('refresh_token', response.refreshToken);

    return response;
  }

  async getCurrentUser(): Promise<User> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = 'current_user';
    const cached = cache.get<User>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const user = await httpClient.get<User>(`${this.endpoint}/profile/`);
    cache.set(cacheKey, user, 10 * 60 * 1000); // Cache for 10 minutes
    
    return user;
  }

  async updateProfile(data: ProfileUpdateData): Promise<User> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const formData = new FormData();
    
    Object.entries(data).forEach(([key, value]) => {
      if (value instanceof File) {
        formData.append(key, value);
      } else if (typeof value === 'object' && value !== null) {
        formData.append(key, JSON.stringify(value));
      } else if (value !== undefined) {
        formData.append(key, String(value));
      }
    });

    const user = await httpClient.patch<User>(`${this.endpoint}/profile/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    // Update cache
    cache.set('current_user', user);
    
    return user;
  }
}

/**
 * Complaint Repository Implementation
 */
export class ComplaintRepository extends InjectableService implements IComplaintRepository {
  private readonly endpoint = '/complaints';

  async getComplaints(params: ComplaintQueryParams): Promise<PaginatedResponse<Complaint>> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = `complaints_${JSON.stringify(params)}`;
    const cached = cache.get<PaginatedResponse<Complaint>>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const queryString = this.buildQueryString(params);
    const response = await httpClient.get<PaginatedResponse<Complaint>>(`${this.endpoint}/${queryString}`);
    
    cache.set(cacheKey, response, 2 * 60 * 1000); // Cache for 2 minutes
    return response;
  }

  async getComplaintById(id: string): Promise<Complaint> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = `complaint_${id}`;
    const cached = cache.get<Complaint>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const complaint = await httpClient.get<Complaint>(`${this.endpoint}/${id}/`);
    cache.set(cacheKey, complaint);
    
    return complaint;
  }

  async createComplaint(data: CreateComplaintData): Promise<Complaint> {
    const httpClient = this.getService('httpClient');
    const validation = this.getService('validation');
    const cache = this.getService('cache');

    validation.validateRequired(data, ['title', 'description', 'category', 'location']);

    const formData = new FormData();
    
    Object.entries(data).forEach(([key, value]) => {
      if (key === 'attachments' && value instanceof FileList) {
        Array.from(value).forEach((file) => {
          formData.append('attachments', file);
        });
      } else if (value instanceof File) {
        formData.append(key, value);
      } else if (typeof value === 'object' && value !== null) {
        formData.append(key, JSON.stringify(value));
      } else if (value !== undefined) {
        formData.append(key, String(value));
      }
    });

    const complaint = await httpClient.post<Complaint>(`${this.endpoint}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    // Clear complaints cache
    cache.clear('complaints_');
    
    return complaint;
  }

  async updateComplaint(id: string, data: UpdateComplaintData): Promise<Complaint> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const complaint = await httpClient.patch<Complaint>(`${this.endpoint}/${id}/`, data);
    
    // Update caches
    cache.set(`complaint_${id}`, complaint);
    cache.clear('complaints_');
    
    return complaint;
  }

  async deleteComplaint(id: string): Promise<void> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    await httpClient.delete(`${this.endpoint}/${id}/`);
    
    // Clear caches
    cache.delete(`complaint_${id}`);
    cache.clear('complaints_');
  }

  async getComplaintHistory(id: string): Promise<ComplaintHistory[]> {
    const httpClient = this.getService('httpClient');
    return httpClient.get<ComplaintHistory[]>(`${this.endpoint}/${id}/history/`);
  }

  private buildQueryString(params: Record<string, any>): string {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, String(value));
      }
    });
    
    const queryString = queryParams.toString();
    return queryString ? `?${queryString}` : '';
  }
}

/**
 * Analytics Repository Implementation
 */
export class AnalyticsRepository extends InjectableService implements IAnalyticsRepository {
  private readonly endpoint = '/analytics';

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = 'dashboard_metrics';
    const cached = cache.get<DashboardMetrics>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const metrics = await httpClient.get<DashboardMetrics>(`${this.endpoint}/dashboard/`);
    cache.set(cacheKey, metrics, 5 * 60 * 1000); // Cache for 5 minutes
    
    return metrics;
  }

  async getComplaintTrends(params: TrendParams): Promise<TrendData> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = `trends_${JSON.stringify(params)}`;
    const cached = cache.get<TrendData>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const queryString = this.buildQueryString(params);
    const trends = await httpClient.get<TrendData>(`${this.endpoint}/trends/${queryString}`);
    
    cache.set(cacheKey, trends, 10 * 60 * 1000); // Cache for 10 minutes
    return trends;
  }

  async getPerformanceMetrics(params: PerformanceParams): Promise<PerformanceData> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = `performance_${JSON.stringify(params)}`;
    const cached = cache.get<PerformanceData>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const queryString = this.buildQueryString(params);
    const performance = await httpClient.get<PerformanceData>(`${this.endpoint}/performance/${queryString}`);
    
    cache.set(cacheKey, performance, 15 * 60 * 1000); // Cache for 15 minutes
    return performance;
  }

  async getGeospatialData(params: GeospatialParams): Promise<GeospatialData> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = `geospatial_${JSON.stringify(params)}`;
    const cached = cache.get<GeospatialData>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const queryString = this.buildQueryString(params);
    const geospatial = await httpClient.get<GeospatialData>(`${this.endpoint}/geospatial/${queryString}`);
    
    cache.set(cacheKey, geospatial, 5 * 60 * 1000); // Cache for 5 minutes
    return geospatial;
  }

  private buildQueryString(params: Record<string, any>): string {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (typeof value === 'object') {
          queryParams.append(key, JSON.stringify(value));
        } else {
          queryParams.append(key, String(value));
        }
      }
    });
    
    const queryString = queryParams.toString();
    return queryString ? `?${queryString}` : '';
  }
}

/**
 * Chatbot Repository Implementation
 */
export class ChatbotRepository extends InjectableService implements IChatbotRepository {
  private readonly endpoint = '/chatbot';

  async sendMessage(message: string, context?: ChatContext): Promise<ChatResponse> {
    const httpClient = this.getService('httpClient');
    const validation = this.getService('validation');

    validation.validateRequired({ message }, ['message']);

    return httpClient.post<ChatResponse>(`${this.endpoint}/message/`, {
      message,
      context,
    });
  }

  async getConversationHistory(sessionId: string): Promise<ChatMessage[]> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = `conversation_${sessionId}`;
    const cached = cache.get<ChatMessage[]>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const history = await httpClient.get<ChatMessage[]>(`${this.endpoint}/conversation/${sessionId}/`);
    cache.set(cacheKey, history, 2 * 60 * 1000); // Cache for 2 minutes
    
    return history;
  }

  async clearConversation(sessionId: string): Promise<void> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    await httpClient.delete(`${this.endpoint}/conversation/${sessionId}/`);
    cache.delete(`conversation_${sessionId}`);
  }

  async getQuickReplies(intent: string): Promise<QuickReply[]> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = `quick_replies_${intent}`;
    const cached = cache.get<QuickReply[]>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const replies = await httpClient.get<QuickReply[]>(`${this.endpoint}/quick-replies/${intent}/`);
    cache.set(cacheKey, replies, 30 * 60 * 1000); // Cache for 30 minutes
    
    return replies;
  }
}

/**
 * Notification Repository Implementation
 */
export class NotificationRepository extends InjectableService implements INotificationRepository {
  private readonly endpoint = '/notifications';

  async getNotifications(params: NotificationParams): Promise<PaginatedResponse<Notification>> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = `notifications_${JSON.stringify(params)}`;
    const cached = cache.get<PaginatedResponse<Notification>>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const queryString = this.buildQueryString(params);
    const notifications = await httpClient.get<PaginatedResponse<Notification>>(`${this.endpoint}/${queryString}`);
    
    cache.set(cacheKey, notifications, 1 * 60 * 1000); // Cache for 1 minute
    return notifications;
  }

  async markAsRead(id: string): Promise<void> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    await httpClient.patch(`${this.endpoint}/${id}/`, { isRead: true });
    cache.clear('notifications_');
  }

  async markAllAsRead(): Promise<void> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    await httpClient.post(`${this.endpoint}/mark-all-read/`);
    cache.clear('notifications_');
  }

  async deleteNotification(id: string): Promise<void> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    await httpClient.delete(`${this.endpoint}/${id}/`);
    cache.clear('notifications_');
  }

  async getNotificationSettings(): Promise<NotificationSettings> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const cacheKey = 'notification_settings';
    const cached = cache.get<NotificationSettings>(cacheKey);
    
    if (cached) {
      return cached;
    }

    const settings = await httpClient.get<NotificationSettings>(`${this.endpoint}/settings/`);
    cache.set(cacheKey, settings, 30 * 60 * 1000); // Cache for 30 minutes
    
    return settings;
  }

  async updateNotificationSettings(settings: NotificationSettings): Promise<NotificationSettings> {
    const httpClient = this.getService('httpClient');
    const cache = this.getService('cache');

    const updatedSettings = await httpClient.put<NotificationSettings>(`${this.endpoint}/settings/`, settings);
    cache.set('notification_settings', updatedSettings);
    
    return updatedSettings;
  }

  private buildQueryString(params: Record<string, any>): string {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, String(value));
      }
    });
    
    const queryString = queryParams.toString();
    return queryString ? `?${queryString}` : '';
  }
}