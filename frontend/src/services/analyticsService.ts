import api from './api';
import { BaseService } from './BaseService';
import {
  ChartDataPoint,
  TimeSeriesDataPoint,
  FilterParams,
  DashboardStats,
  RealTimeMetrics,
  UserActivity,
  AlertRule,
  AlertInstance,
  PaginatedResponse,
  SystemHealth,
} from '@/types';

// Analytics-specific types
export interface AnalyticsOverview {
  total_complaints: number;
  pending_complaints: number;
  resolved_complaints: number;
  resolution_rate: number;
  avg_resolution_time: number;
  satisfaction_score?: number;
}

export interface TrendData {
  complaints_by_month: TimeSeriesDataPoint[];
  complaints_by_category: ChartDataPoint[];
  complaints_by_status: ChartDataPoint[];
  complaints_by_priority: ChartDataPoint[];
  resolution_time_trend: TimeSeriesDataPoint[];
}

export interface AnalyticsFilters extends FilterParams {
  date_range?: 'last_7_days' | 'last_30_days' | 'last_3_months' | 'last_year' | 'custom';
  custom_start_date?: string;
  custom_end_date?: string;
  group_by?: 'day' | 'week' | 'month' | 'quarter' | 'year';
  include_resolved?: boolean;
  include_pending?: boolean;
}

/**
 * Service class for analytics and reporting operations
 */
export class AnalyticsService extends BaseService {
  constructor() {
    super('/analytics');
  }

  /**
   * Get dashboard statistics
   */
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      this.log('getDashboardStats');
      
      const cacheKey = 'dashboard_stats';
      const cached = this.getCached<DashboardStats>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<DashboardStats>(`${this.endpoint}/dashboard/stats/`);
      const data = this.transformResponse(response);
      
      // Cache for 2 minutes
      this.setCached(cacheKey, data, 2 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get real-time metrics
   */
  async getRealTimeMetrics(params?: {
    period?: 'hourly' | 'daily' | 'weekly' | 'monthly';
    type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<RealTimeMetrics[]> {
    try {
      this.log('getRealTimeMetrics', params);
      
      const cacheKey = `realtime_metrics_${JSON.stringify(params)}`;
      const cached = this.getCached<RealTimeMetrics[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params || {});
      const response = await api.get<RealTimeMetrics[]>(`${this.endpoint}/metrics/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 30 seconds (real-time data)
      this.setCached(cacheKey, data, 30 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get real-time updates
   */
  async getRealTimeUpdates(last_update?: string): Promise<{
    new_complaints: number;
    status_updates: number;
    new_alerts: number;
    timestamp: string;
  }> {
    try {
      this.log('getRealTimeUpdates', { last_update });
      
      const params = last_update ? { last_update } : {};
      const queryString = this.buildQueryString(params);
      const response = await api.get(`${this.endpoint}/real-time-updates/${queryString}`);
      
      return this.transformResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get user activity data
   */
  async getUserActivity(params?: {
    page?: number;
    page_size?: number;
    user_id?: number;
    activity_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<UserActivity>> {
    try {
      this.log('getUserActivity', params);
      
      const cacheKey = `user_activity_${JSON.stringify(params)}`;
      const cached = this.getCached<PaginatedResponse<UserActivity>>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params || {});
      const response = await api.get<PaginatedResponse<UserActivity>>(`${this.endpoint}/user-activity/${queryString}`);
      const data = this.transformPaginatedResponse(response);
      
      // Cache for 5 minutes
      this.setCached(cacheKey, data, 5 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get performance metrics
   */
  async getPerformanceMetrics(params?: {
    metric_name?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<Array<{
    id: number;
    metric_name: string;
    metric_value: number;
    server_node: string;
    timestamp: string;
  }>> {
    try {
      this.log('getPerformanceMetrics', params);
      
      const cacheKey = `performance_metrics_${JSON.stringify(params)}`;
      const cached = this.getCached<any[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params || {});
      const response = await api.get(`${this.endpoint}/performance/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 2 minutes
      this.setCached(cacheKey, data, 2 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get alert rules
   */
  async getAlertRules(): Promise<AlertRule[]> {
    try {
      this.log('getAlertRules');
      
      const cacheKey = 'alert_rules';
      const cached = this.getCached<AlertRule[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<AlertRule[]>(`${this.endpoint}/alert-rules/`);
      const data = this.transformResponse(response);
      
      // Cache for 10 minutes
      this.setCached(cacheKey, data, 10 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Create alert rule
   */
  async createAlertRule(data: Omit<AlertRule, 'id' | 'created_by' | 'created_at'>): Promise<AlertRule> {
    try {
      this.log('createAlertRule', data);
      
      const response = await api.post<AlertRule>(`${this.endpoint}/alert-rules/`, data);
      const newRule = this.transformResponse(response);
      
      // Clear cache
      this.clearCache('alert_rules');
      
      return newRule;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Update alert rule
   */
  async updateAlertRule(id: number, data: Partial<AlertRule>): Promise<AlertRule> {
    try {
      this.log('updateAlertRule', { id, data });
      
      const response = await api.patch<AlertRule>(`${this.endpoint}/alert-rules/${id}/`, data);
      const updatedRule = this.transformResponse(response);
      
      // Clear cache
      this.clearCache('alert_rules');
      
      return updatedRule;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Delete alert rule
   */
  async deleteAlertRule(id: number): Promise<void> {
    try {
      this.log('deleteAlertRule', { id });
      
      await api.delete(`${this.endpoint}/alert-rules/${id}/`);
      
      // Clear cache
      this.clearCache('alert_rules');
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get alert instances
   */
  async getAlertInstances(params?: {
    is_resolved?: boolean;
    severity?: 'low' | 'medium' | 'high';
    start_date?: string;
    end_date?: string;
  }): Promise<AlertInstance[]> {
    try {
      this.log('getAlertInstances', params);
      
      const cacheKey = `alert_instances_${JSON.stringify(params)}`;
      const cached = this.getCached<AlertInstance[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params || {});
      const response = await api.get<AlertInstance[]>(`${this.endpoint}/alerts/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 1 minute
      this.setCached(cacheKey, data, 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Mark alert as resolved
   */
  async resolveAlert(alert_id: number): Promise<{ message: string }> {
    try {
      this.log('resolveAlert', { alert_id });
      
      const response = await api.post(`${this.endpoint}/alerts/${alert_id}/resolve/`);
      const result = this.transformResponse(response);
      
      // Clear alert instances cache
      this.clearCache('alert_instances_');
      
      return result;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get system health
   */
  async getSystemHealth(): Promise<SystemHealth> {
    try {
      this.log('getSystemHealth');
      
      // Don't cache system health (real-time data)
      const response = await api.get<SystemHealth>(`${this.endpoint}/system-health/`);
      
      return this.transformResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get complaint trends
   */
  async getComplaintTrends(params?: {
    period?: 'daily' | 'weekly' | 'monthly';
    start_date?: string;
    end_date?: string;
    group_by?: 'status' | 'category' | 'department' | 'priority';
  }): Promise<Array<{
    date: string;
    count: number;
    group_value?: string;
  }>> {
    try {
      this.log('getComplaintTrends', params);
      
      const cacheKey = `complaint_trends_${JSON.stringify(params)}`;
      const cached = this.getCached<any[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params || {});
      const response = await api.get(`${this.endpoint}/trends/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 5 minutes
      this.setCached(cacheKey, data, 5 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get department performance
   */
  async getDepartmentPerformance(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<Array<{
    department_id: number;
    department_name: string;
    total_complaints: number;
    resolved_complaints: number;
    avg_resolution_time: number;
    satisfaction_score: number;
  }>> {
    try {
      this.log('getDepartmentPerformance', params);
      
      const cacheKey = `department_performance_${JSON.stringify(params)}`;
      const cached = this.getCached<any[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params || {});
      const response = await api.get(`${this.endpoint}/department-performance/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 10 minutes
      this.setCached(cacheKey, data, 10 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get user engagement metrics
   */
  async getUserEngagement(params?: {
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
  }> {
    try {
      this.log('getUserEngagement', params);
      
      const cacheKey = `user_engagement_${JSON.stringify(params)}`;
      const cached = this.getCached<any>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params || {});
      const response = await api.get(`${this.endpoint}/user-engagement/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 15 minutes
      this.setCached(cacheKey, data, 15 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get sentiment analysis data
   */
  async getSentimentAnalysis(params?: {
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
  }> {
    try {
      this.log('getSentimentAnalysis', params);
      
      const cacheKey = `sentiment_analysis_${JSON.stringify(params)}`;
      const cached = this.getCached<any>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params || {});
      const response = await api.get(`${this.endpoint}/sentiment/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 10 minutes
      this.setCached(cacheKey, data, 10 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Export analytics data
   */
  async exportAnalyticsData(
    data_type: 'complaints' | 'user_activity' | 'performance',
    format: 'csv' | 'json',
    filters?: any
  ): Promise<Blob> {
    try {
      this.log('exportAnalyticsData', { data_type, format, filters });
      
      const params = {
        type: data_type,
        format,
        ...filters,
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

  /**
   * Generate custom report
   */
  async generateReport(reportConfig: {
    type: 'summary' | 'detailed' | 'executive';
    format: 'pdf' | 'excel';
    include_charts: boolean;
    date_range: {
      start: string;
      end: string;
    };
    sections: string[];
  }): Promise<Blob> {
    try {
      this.log('generateReport', reportConfig);
      
      const response = await api.post(`${this.endpoint}/reports/generate/`, reportConfig, {
        responseType: 'blob',
      });
      
      return response.data;
    } catch (error) {
      this.handleError(error as any);
    }
  }
}

// Export singleton instance
export const analyticsService = new AnalyticsService();
export default analyticsService;