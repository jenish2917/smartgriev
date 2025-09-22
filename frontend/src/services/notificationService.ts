import api from './api';
import { BaseService, ServiceError } from './BaseService';
import {
  Notification,
  PaginatedResponse,
} from '@/types';

// Notification-specific types
export interface NotificationPreferences {
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  in_app_enabled: boolean;
  complaint_updates: boolean;
  system_alerts: boolean;
  reminders: boolean;
  announcements: boolean;
  digest_frequency: 'none' | 'daily' | 'weekly';
  quiet_hours_start?: string;
  quiet_hours_end?: string;
}

export interface NotificationFilters {
  is_read?: boolean;
  notification_type?: 'complaint_update' | 'system_alert' | 'reminder' | 'announcement';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
  search?: string;
}

export interface CreateNotificationData {
  recipient_id?: number;
  recipient_type: 'user' | 'officer' | 'admin' | 'all';
  title: string;
  message: string;
  notification_type: 'complaint_update' | 'system_alert' | 'reminder' | 'announcement';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  action_url?: string;
  action_text?: string;
  scheduled_for?: string;
  expires_at?: string;
  metadata?: Record<string, any>;
}

export interface BulkNotificationData {
  recipient_ids?: number[];
  recipient_type?: 'user' | 'officer' | 'admin';
  filters?: NotificationFilters;
  title: string;
  message: string;
  notification_type: 'complaint_update' | 'system_alert' | 'reminder' | 'announcement';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  action_url?: string;
  action_text?: string;
  scheduled_for?: string;
  expires_at?: string;
}

export interface NotificationTemplate {
  id: number;
  name: string;
  subject_template: string;
  body_template: string;
  notification_type: string;
  variables: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationChannel {
  id: number;
  name: string;
  type: 'email' | 'sms' | 'push' | 'in_app';
  is_enabled: boolean;
  configuration: Record<string, any>;
  rate_limit?: {
    max_per_hour: number;
    max_per_day: number;
  };
}

export interface NotificationStats {
  total_sent: number;
  total_delivered: number;
  total_read: number;
  total_failed: number;
  delivery_rate: number;
  read_rate: number;
  stats_by_type: Array<{
    type: string;
    sent: number;
    delivered: number;
    read: number;
    failed: number;
  }>;
  stats_by_channel: Array<{
    channel: string;
    sent: number;
    delivered: number;
    failed: number;
  }>;
}

/**
 * Service class for notification and communication operations
 */
export class NotificationService extends BaseService {
  constructor() {
    super('/notifications');
  }

  /**
   * Get user notifications
   */
  async getNotifications(filters: NotificationFilters = {}): Promise<PaginatedResponse<Notification>> {
    try {
      this.log('getNotifications', filters);
      
      const cacheKey = `notifications_${JSON.stringify(filters)}`;
      const cached = this.getCached<PaginatedResponse<Notification>>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(filters);
      const response = await api.get<PaginatedResponse<Notification>>(`${this.endpoint}/${queryString}`);
      const data = this.transformPaginatedResponse(response);
      
      // Cache for 1 minute (notifications are time-sensitive)
      this.setCached(cacheKey, data, 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get a specific notification
   */
  async getNotification(id: number): Promise<Notification> {
    try {
      this.log('getNotification', { id });
      
      const cacheKey = `notification_${id}`;
      const cached = this.getCached<Notification>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<Notification>(`${this.endpoint}/${id}/`);
      const data = this.transformResponse(response);
      
      // Cache for 5 minutes
      this.setCached(cacheKey, data, 5 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Create a new notification
   */
  async createNotification(data: CreateNotificationData): Promise<Notification> {
    try {
      this.log('createNotification', data);
      
      // Validate required fields
      this.validateRequest(data, ['recipient_type', 'title', 'message', 'notification_type', 'priority']);
      
      const response = await api.post<Notification>(`${this.endpoint}/`, data);
      const newNotification = this.transformResponse(response);
      
      // Clear notifications cache
      this.clearCache('notifications_');
      
      return newNotification;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Send bulk notifications
   */
  async sendBulkNotifications(data: BulkNotificationData): Promise<{
    sent: number;
    failed: number;
    job_id: string;
    message: string;
  }> {
    try {
      this.log('sendBulkNotifications', data);
      
      // Validate required fields
      this.validateRequest(data, ['title', 'message', 'notification_type', 'priority']);
      
      const response = await api.post(`${this.endpoint}/bulk/`, data);
      const result = this.transformResponse(response);
      
      // Clear notifications cache
      this.clearCache('notifications_');
      
      return result;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Mark notification as read
   */
  async markAsRead(id: number): Promise<Notification> {
    try {
      this.log('markAsRead', { id });
      
      const response = await api.post<Notification>(`${this.endpoint}/${id}/read/`);
      const updatedNotification = this.transformResponse(response);
      
      // Clear relevant caches
      this.clearCache('notifications_');
      this.clearCache(`notification_${id}`);
      
      return updatedNotification;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<{ marked_count: number; message: string }> {
    try {
      this.log('markAllAsRead');
      
      const response = await api.post(`${this.endpoint}/mark-all-read/`);
      const result = this.transformResponse(response);
      
      // Clear all notification caches
      this.clearCache('notifications_');
      
      return result;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Delete a notification
   */
  async deleteNotification(id: number): Promise<void> {
    try {
      this.log('deleteNotification', { id });
      
      await api.delete(`${this.endpoint}/${id}/`);
      
      // Clear relevant caches
      this.clearCache('notifications_');
      this.clearCache(`notification_${id}`);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get user notification preferences
   */
  async getNotificationPreferences(): Promise<NotificationPreferences> {
    try {
      this.log('getNotificationPreferences');
      
      const cacheKey = 'notification_preferences';
      const cached = this.getCached<NotificationPreferences>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<NotificationPreferences>(`${this.endpoint}/preferences/`);
      const data = this.transformResponse(response);
      
      // Cache for 10 minutes
      this.setCached(cacheKey, data, 10 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Update notification preferences
   */
  async updateNotificationPreferences(preferences: Partial<NotificationPreferences>): Promise<NotificationPreferences> {
    try {
      this.log('updateNotificationPreferences', preferences);
      
      const response = await api.patch<NotificationPreferences>(`${this.endpoint}/preferences/`, preferences);
      const updatedPreferences = this.transformResponse(response);
      
      // Clear preferences cache
      this.clearCache('notification_preferences');
      
      return updatedPreferences;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get notification templates
   */
  async getTemplates(): Promise<NotificationTemplate[]> {
    try {
      this.log('getTemplates');
      
      const cacheKey = 'notification_templates';
      const cached = this.getCached<NotificationTemplate[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<NotificationTemplate[]>(`${this.endpoint}/templates/`);
      const data = this.transformResponse(response);
      
      // Cache for 15 minutes (templates don't change often)
      this.setCached(cacheKey, data, 15 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Create notification template (admin only)
   */
  async createTemplate(template: Omit<NotificationTemplate, 'id' | 'created_at' | 'updated_at'>): Promise<NotificationTemplate> {
    try {
      this.log('createTemplate', template);
      
      // Validate required fields
      this.validateRequest(template, ['name', 'subject_template', 'body_template', 'notification_type']);
      
      const response = await api.post<NotificationTemplate>(`${this.endpoint}/templates/`, template);
      const newTemplate = this.transformResponse(response);
      
      // Clear templates cache
      this.clearCache('notification_templates');
      
      return newTemplate;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Update notification template (admin only)
   */
  async updateTemplate(id: number, updates: Partial<NotificationTemplate>): Promise<NotificationTemplate> {
    try {
      this.log('updateTemplate', { id, updates });
      
      const response = await api.patch<NotificationTemplate>(`${this.endpoint}/templates/${id}/`, updates);
      const updatedTemplate = this.transformResponse(response);
      
      // Clear templates cache
      this.clearCache('notification_templates');
      
      return updatedTemplate;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Delete notification template (admin only)
   */
  async deleteTemplate(id: number): Promise<void> {
    try {
      this.log('deleteTemplate', { id });
      
      await api.delete(`${this.endpoint}/templates/${id}/`);
      
      // Clear templates cache
      this.clearCache('notification_templates');
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get notification channels
   */
  async getChannels(): Promise<NotificationChannel[]> {
    try {
      this.log('getChannels');
      
      const cacheKey = 'notification_channels';
      const cached = this.getCached<NotificationChannel[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<NotificationChannel[]>(`${this.endpoint}/channels/`);
      const data = this.transformResponse(response);
      
      // Cache for 20 minutes (channels don't change often)
      this.setCached(cacheKey, data, 20 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Update notification channel (admin only)
   */
  async updateChannel(id: number, updates: Partial<NotificationChannel>): Promise<NotificationChannel> {
    try {
      this.log('updateChannel', { id, updates });
      
      const response = await api.patch<NotificationChannel>(`${this.endpoint}/channels/${id}/`, updates);
      const updatedChannel = this.transformResponse(response);
      
      // Clear channels cache
      this.clearCache('notification_channels');
      
      return updatedChannel;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get notification statistics
   */
  async getStats(filters: {
    start_date?: string;
    end_date?: string;
    notification_type?: string;
    channel?: string;
  } = {}): Promise<NotificationStats> {
    try {
      this.log('getStats', filters);
      
      const cacheKey = `notification_stats_${JSON.stringify(filters)}`;
      const cached = this.getCached<NotificationStats>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(filters);
      const response = await api.get<NotificationStats>(`${this.endpoint}/stats/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 5 minutes
      this.setCached(cacheKey, data, 5 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get unread notification count
   */
  async getUnreadCount(): Promise<{ count: number }> {
    try {
      this.log('getUnreadCount');
      
      // Don't cache unread count (real-time data)
      const response = await api.get(`${this.endpoint}/unread-count/`);
      
      return this.transformResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Subscribe to push notifications
   */
  async subscribeToPush(subscription: {
    endpoint: string;
    keys: {
      p256dh: string;
      auth: string;
    };
  }): Promise<{ subscribed: boolean; message: string }> {
    try {
      this.log('subscribeToPush', subscription);
      
      const response = await api.post(`${this.endpoint}/push/subscribe/`, subscription);
      
      return this.transformResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribeFromPush(): Promise<{ unsubscribed: boolean; message: string }> {
    try {
      this.log('unsubscribeFromPush');
      
      const response = await api.post(`${this.endpoint}/push/unsubscribe/`);
      
      return this.transformResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Send test notification
   */
  async sendTestNotification(
    channel: 'email' | 'sms' | 'push' | 'in_app',
    recipient?: string
  ): Promise<{ sent: boolean; message: string }> {
    try {
      this.log('sendTestNotification', { channel, recipient });
      
      const response = await api.post(`${this.endpoint}/test/`, {
        channel,
        recipient,
      });
      
      return this.transformResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Export notification data
   */
  async exportNotifications(
    filters: NotificationFilters = {},
    format: 'csv' | 'excel' | 'json' = 'csv'
  ): Promise<Blob> {
    try {
      this.log('exportNotifications', { filters, format });
      
      const params = {
        ...filters,
        format,
      };
      
      const queryString = this.buildQueryString(params);
      const response = await api.get(`${this.endpoint}/export/${queryString}`, {
        responseType: 'blob',
      });
      
      return response.data;
    } catch (error) {
      this.handleError(error as any);
    }
  }
}

// Export singleton instance
export const notificationService = new NotificationService();
export default notificationService;