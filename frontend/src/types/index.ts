// Core API Response Types
export interface ApiResponse<T = any> {
  data: T;
  status: number;
  message?: string;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

// User Types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  mobile: string;
  address: string;
  language: string;
  is_officer: boolean;
  is_superuser: boolean;
  is_staff: boolean;
  date_joined: string;
  last_login: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  mobile: string;
  address: string;
  language?: string;
}

// Department Types
export interface Department {
  id: number;
  name: string;
  zone: string;
  officer: number | null;
}

// Complaint Types
export type ComplaintStatus = 'pending' | 'in_progress' | 'resolved' | 'rejected';
export type ComplaintPriority = 'low' | 'medium' | 'high' | 'urgent';
export type LocationMethod = 'gps' | 'manual' | 'address';
export type AreaType = 'residential' | 'commercial' | 'industrial' | 'rural';

export interface Complaint {
  id: number;
  user: number;
  title: string;
  description: string;
  media?: string;
  category: string;
  sentiment?: number;
  department: number;
  department_name?: string;
  status: ComplaintStatus;
  priority: ComplaintPriority;
  
  // Location fields
  incident_latitude?: number;
  incident_longitude?: number;
  incident_address?: string;
  incident_landmark?: string;
  gps_accuracy?: number;
  location_method: LocationMethod;
  area_type?: AreaType;
  
  created_at: string;
  updated_at: string;
}

export interface CreateComplaintData {
  title: string;
  description: string;
  category: string;
  department: number;
  media?: File;
  incident_latitude?: number;
  incident_longitude?: number;
  incident_address?: string;
  incident_landmark?: string;
  location_method?: LocationMethod;
  area_type?: AreaType;
}

// Chatbot Types
export interface ChatMessage {
  id: number;
  user: number;
  message: string;
  response: string;
  intent?: string;
  confidence?: number;
  escalated_to_human: boolean;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatStats {
  total_chats: number;
  intent_distribution: Array<{
    intent: string;
    count: number;
  }>;
  average_confidence: number;
  feedback_stats: {
    avg_rating: number;
    helpful_count: number;
    total_feedback: number;
  };
}

// Analytics Types
export interface DashboardStats {
  total_complaints: number;
  pending_complaints: number;
  resolved_complaints: number;
  resolution_rate: number;
  avg_resolution_time: number;
  satisfaction_score: number;
  sentiment_distribution: {
    positive: number;
    neutral: number;
    negative: number;
  };
  department_performance: Array<{
    name: string;
    total_complaints: number;
    resolved_complaints: number;
    avg_resolution_time: number;
  }>;
  recent_activity: Array<{
    id: number;
    title: string;
    status: string;
    priority: string;
    created_at: string;
  }>;
  geographic_hotspots: Array<{
    location_lat: number;
    location_lon: number;
    complaint_count: number;
  }>;
  daily_trends: Array<{
    date: string;
    count: number;
    resolved: number;
  }>;
  chatbot_stats: {
    total_interactions: number;
    escalated_count: number;
    avg_confidence: number;
    effectiveness_rate: number;
  };
}

export interface RealTimeMetrics {
  id: number;
  metric_type: string;
  metric_value: number;
  time_period: 'hourly' | 'daily' | 'weekly' | 'monthly';
  department?: number;
  timestamp: string;
}

export interface UserActivity {
  id: number;
  user: number;
  activity_type: string;
  endpoint: string;
  response_code: number;
  duration?: number;
  timestamp: string;
}

export interface AlertRule {
  id: number;
  name: string;
  metric_type: string;
  operator: '>' | '<' | '>=' | '<=' | '=' | '!=';
  threshold_value: number;
  severity: 'low' | 'medium' | 'high';
  notification_channels: string[];
  is_active: boolean;
  created_by: number;
  created_at: string;
}

export interface AlertInstance {
  id: number;
  rule: AlertRule;
  triggered_value: number;
  severity: 'low' | 'medium' | 'high';
  message: string;
  is_resolved: boolean;
  triggered_at: string;
  resolved_at?: string;
}

// Geospatial Types
export interface GeospatialCluster {
  id: number;
  cluster_type: string;
  center_latitude: number;
  center_longitude: number;
  radius: number;
  complaint_count: number;
  severity_score: number;
  created_at: string;
}

export interface HeatmapData {
  id: number;
  latitude: number;
  longitude: number;
  intensity: number;
  complaint_type: string;
  timestamp: string;
}

// Notification Types
export interface NotificationTemplate {
  id: number;
  name: string;
  template_type: 'email' | 'sms' | 'push' | 'in_app';
  subject?: string;
  content: string;
  variables: string[];
  is_active: boolean;
}

export interface Notification {
  id: number;
  user: number;
  title: string;
  message: string;
  notification_type: 'email' | 'sms' | 'push' | 'in_app';
  is_read: boolean;
  sent_at: string;
  read_at?: string;
}

// WebSocket Message Types
export interface WebSocketMessage<T = any> {
  type: string;
  data?: T;
  timestamp?: string;
}

export interface DashboardUpdate {
  type: 'dashboard_update';
  data: Partial<DashboardStats>;
  timestamp: string;
}

export interface MetricUpdate {
  type: 'metric_update';
  metric_type: string;
  value: number;
  timestamp: string;
}

export interface AlertNotification {
  type: 'alert';
  alert_id: number;
  message: string;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
}

export interface ComplaintUpdate {
  type: 'complaint_update';
  complaint_id: number;
  status: ComplaintStatus;
  timestamp: string;
}

// Form Types
export interface FilterParams {
  status?: ComplaintStatus[];
  priority?: ComplaintPriority[];
  category?: string[];
  department?: number[];
  date_from?: string;
  date_to?: string;
  search?: string;
}

// Chart Data Types
export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

export interface TimeSeriesDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface MapMarker {
  id: number;
  latitude: number;
  longitude: number;
  title: string;
  description?: string;
  type: 'complaint' | 'cluster' | 'hotspot';
  severity?: 'low' | 'medium' | 'high';
}

// ML Model Types
export interface MLModel {
  id: number;
  name: string;
  model_type: string;
  version: string;
  accuracy: number;
  is_active: boolean;
  created_at: string;
}

export interface ModelPrediction {
  prediction: string;
  confidence: number;
  explanation?: string;
}

// System Health Types
export interface SystemHealth {
  database: string;
  cache: string;
  error_rate: number;
  recent_requests: number;
  timestamp: string;
}
