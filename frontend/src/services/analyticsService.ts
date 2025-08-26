import { apiService } from './api';
import {
  DashboardStats,
  RealTimeMetrics,
  UserActivity,
  AlertRule,
  AlertInstance,
  PaginatedResponse,
  SystemHealth,
} from '@/types';

export const analyticsService = {
  // Get dashboard statistics
  getDashboardStats: async (): Promise<DashboardStats> => {
    return apiService.get<DashboardStats>('/analytics/dashboard/stats/');
  },

  // Get real-time metrics
  getRealTimeMetrics: async (params?: {
    period?: 'hourly' | 'daily' | 'weekly' | 'monthly';
    type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<RealTimeMetrics[]> => {
    return apiService.get<RealTimeMetrics[]>('/analytics/metrics/', params);
  },

  // Get real-time updates
  getRealTimeUpdates: async (last_update?: string): Promise<{
    new_complaints: number;
    status_updates: number;
    new_alerts: number;
    timestamp: string;
  }> => {
    return apiService.get('/analytics/real-time-updates/', {
      last_update,
    });
  },

  // Get user activity
  getUserActivity: async (params?: {
    page?: number;
    page_size?: number;
    user_id?: number;
    activity_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<UserActivity>> => {
    return apiService.get<PaginatedResponse<UserActivity>>('/analytics/user-activity/', params);
  },

  // Get performance metrics
  getPerformanceMetrics: async (params?: {
    metric_name?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<Array<{
    id: number;
    metric_name: string;
    metric_value: number;
    server_node: string;
    timestamp: string;
  }>> => {
    return apiService.get('/analytics/performance/', params);
  },

  // Get alert rules
  getAlertRules: async (): Promise<AlertRule[]> => {
    return apiService.get<AlertRule[]>('/analytics/alert-rules/');
  },

  // Create alert rule
  createAlertRule: async (data: Omit<AlertRule, 'id' | 'created_by' | 'created_at'>): Promise<AlertRule> => {
    return apiService.post<AlertRule>('/analytics/alert-rules/', data);
  },

  // Update alert rule
  updateAlertRule: async (id: number, data: Partial<AlertRule>): Promise<AlertRule> => {
    return apiService.patch<AlertRule>(`/analytics/alert-rules/${id}/`, data);
  },

  // Delete alert rule
  deleteAlertRule: async (id: number): Promise<void> => {
    return apiService.delete(`/analytics/alert-rules/${id}/`);
  },

  // Get alert instances
  getAlertInstances: async (params?: {
    is_resolved?: boolean;
    severity?: 'low' | 'medium' | 'high';
    start_date?: string;
    end_date?: string;
  }): Promise<AlertInstance[]> => {
    return apiService.get<AlertInstance[]>('/analytics/alerts/', params);
  },

  // Mark alert as resolved
  resolveAlert: async (alert_id: number): Promise<{ message: string }> => {
    return apiService.post(`/analytics/alerts/${alert_id}/resolve/`);
  },

  // Export analytics data
  exportAnalyticsData: async (
    data_type: 'complaints' | 'user_activity' | 'performance',
    format: 'csv' | 'json',
    filters?: {
      start_date?: string;
      end_date?: string;
      [key: string]: any;
    }
  ): Promise<void> => {
    const params = new URLSearchParams({
      type: data_type,
      format,
      ...filters,
    } as any);

    return apiService.download(
      `/analytics/export/?${params.toString()}`,
      `analytics_${data_type}_${new Date().toISOString().split('T')[0]}.${format}`
    );
  },

  // Get system health
  getSystemHealth: async (): Promise<SystemHealth> => {
    return apiService.get<SystemHealth>('/analytics/system-health/');
  },

  // Get complaint trends
  getComplaintTrends: async (params?: {
    period?: 'daily' | 'weekly' | 'monthly';
    start_date?: string;
    end_date?: string;
    group_by?: 'status' | 'category' | 'department' | 'priority';
  }): Promise<Array<{
    date: string;
    count: number;
    group_value?: string;
  }>> => {
    return apiService.get('/analytics/trends/', params);
  },

  // Get department performance
  getDepartmentPerformance: async (params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<Array<{
    department_id: number;
    department_name: string;
    total_complaints: number;
    resolved_complaints: number;
    avg_resolution_time: number;
    satisfaction_score: number;
  }>> => {
    return apiService.get('/analytics/department-performance/', params);
  },

  // Get user engagement metrics
  getUserEngagement: async (params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<{
    active_users: number;
    new_registrations: number;
    user_retention_rate: number;
    avg_session_duration: number;
    top_features_used: Array<{
      feature: string;
      usage_count: number;
    }>;
  }> => {
    return apiService.get('/analytics/user-engagement/', params);
  },

  // Get sentiment analysis data
  getSentimentAnalysis: async (params?: {
    start_date?: string;
    end_date?: string;
    group_by?: 'department' | 'category' | 'status';
  }): Promise<{
    overall_sentiment: number;
    sentiment_distribution: {
      positive: number;
      neutral: number;
      negative: number;
    };
    sentiment_trends: Array<{
      date: string;
      avg_sentiment: number;
    }>;
    sentiment_by_group?: Array<{
      group_value: string;
      avg_sentiment: number;
      count: number;
    }>;
  }> => {
    return apiService.get('/analytics/sentiment/', params);
  },
};
