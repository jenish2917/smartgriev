/**
 * Clean Architecture Core Interfaces
 * Defines the contract for all service implementations
 */

export interface ILogger {
  debug(message: string, ...args: any[]): void;
  info(message: string, ...args: any[]): void;
  warn(message: string, ...args: any[]): void;
  error(message: string, error?: Error, ...args: any[]): void;
}

export interface IHttpClient {
  get<T>(url: string, config?: any): Promise<T>;
  post<T>(url: string, data?: any, config?: any): Promise<T>;
  put<T>(url: string, data?: any, config?: any): Promise<T>;
  patch<T>(url: string, data?: any, config?: any): Promise<T>;
  delete<T>(url: string, config?: any): Promise<T>;
}

export interface IStorageService {
  getItem<T>(key: string): T | null;
  setItem<T>(key: string, value: T): void;
  removeItem(key: string): void;
  clear(): void;
}

export interface ICacheService {
  get<T>(key: string): T | null;
  set<T>(key: string, value: T, ttlMs?: number): void;
  delete(key: string): void;
  clear(pattern?: string): void;
}

export interface IValidationService {
  validate<T>(data: T, schema: any): Promise<T>;
  validateRequired<T>(data: T, fields: (keyof T)[]): void;
}

export interface IErrorHandlingService {
  handleError(error: any): never;
  createError(message: string, code?: string, status?: number): Error;
  isNetworkError(error: any): boolean;
  isAuthenticationError(error: any): boolean;
}

// Business Logic Interfaces
export interface IAuthRepository {
  login(credentials: LoginCredentials): Promise<AuthResponse>;
  register(userData: RegisterData): Promise<AuthResponse>;
  logout(): Promise<void>;
  refreshToken(): Promise<AuthResponse>;
  getCurrentUser(): Promise<User>;
  updateProfile(data: ProfileUpdateData): Promise<User>;
}

export interface IComplaintRepository {
  getComplaints(params: ComplaintQueryParams): Promise<PaginatedResponse<Complaint>>;
  getComplaintById(id: string): Promise<Complaint>;
  createComplaint(data: CreateComplaintData): Promise<Complaint>;
  updateComplaint(id: string, data: UpdateComplaintData): Promise<Complaint>;
  deleteComplaint(id: string): Promise<void>;
  getComplaintHistory(id: string): Promise<ComplaintHistory[]>;
}

export interface IAnalyticsRepository {
  getDashboardMetrics(): Promise<DashboardMetrics>;
  getComplaintTrends(params: TrendParams): Promise<TrendData>;
  getPerformanceMetrics(params: PerformanceParams): Promise<PerformanceData>;
  getGeospatialData(params: GeospatialParams): Promise<GeospatialData>;
}

export interface IChatbotRepository {
  sendMessage(message: string, context?: ChatContext): Promise<ChatResponse>;
  getConversationHistory(sessionId: string): Promise<ChatMessage[]>;
  clearConversation(sessionId: string): Promise<void>;
  getQuickReplies(intent: string): Promise<QuickReply[]>;
}

export interface INotificationRepository {
  getNotifications(params: NotificationParams): Promise<PaginatedResponse<Notification>>;
  markAsRead(id: string): Promise<void>;
  markAllAsRead(): Promise<void>;
  deleteNotification(id: string): Promise<void>;
  getNotificationSettings(): Promise<NotificationSettings>;
  updateNotificationSettings(settings: NotificationSettings): Promise<NotificationSettings>;
}

// Domain Models
export interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  isActive: boolean;
  profilePicture?: string;
  phoneNumber?: string;
  address?: Address;
  preferences: UserPreferences;
  createdAt: string;
  updatedAt: string;
}

export interface Complaint {
  id: string;
  title: string;
  description: string;
  category: ComplaintCategory;
  priority: Priority;
  status: ComplaintStatus;
  submittedBy: User;
  assignedTo?: User;
  location: Location;
  attachments: Attachment[];
  tags: string[];
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
  resolvedAt?: string;
  estimatedResolutionTime?: string;
}

export interface ChatMessage {
  id: string;
  message: string;
  sender: 'user' | 'bot';
  timestamp: string;
  intent?: string;
  confidence?: number;
  quickReplies?: QuickReply[];
  metadata?: Record<string, any>;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  priority: Priority;
  isRead: boolean;
  actionUrl?: string;
  metadata: Record<string, any>;
  createdAt: string;
  expiresAt?: string;
}

// Value Objects and Enums
export enum UserRole {
  CITIZEN = 'citizen',
  OFFICER = 'officer',
  ADMIN = 'admin',
  SUPERVISOR = 'supervisor'
}

export enum ComplaintCategory {
  INFRASTRUCTURE = 'infrastructure',
  ENVIRONMENT = 'environment',
  TRANSPORTATION = 'transportation',
  HEALTH = 'health',
  EDUCATION = 'education',
  PUBLIC_SERVICES = 'public_services'
}

export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum ComplaintStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  ACKNOWLEDGED = 'acknowledged',
  IN_PROGRESS = 'in_progress',
  RESOLVED = 'resolved',
  CLOSED = 'closed',
  REJECTED = 'rejected'
}

export enum NotificationType {
  INFO = 'info',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
  SYSTEM = 'system'
}

// Request/Response Types
export interface LoginCredentials {
  username: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phoneNumber?: string;
  role?: UserRole;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
  expiresIn: number;
}

export interface CreateComplaintData {
  title: string;
  description: string;
  category: ComplaintCategory;
  priority: Priority;
  location: Location;
  attachments?: File[];
  tags?: string[];
  isAnonymous?: boolean;
}

export interface UpdateComplaintData {
  title?: string;
  description?: string;
  priority?: Priority;
  status?: ComplaintStatus;
  assignedTo?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface Location {
  latitude: number;
  longitude: number;
  address: string;
  city: string;
  state: string;
  country: string;
  postalCode: string;
}

export interface Address {
  street: string;
  city: string;
  state: string;
  country: string;
  postalCode: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  notifications: NotificationPreferences;
  privacy: PrivacySettings;
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  sms: boolean;
  inApp: boolean;
  frequency: 'immediate' | 'daily' | 'weekly';
}

export interface PrivacySettings {
  profileVisibility: 'public' | 'private';
  showEmail: boolean;
  showPhone: boolean;
  allowAnalytics: boolean;
}

export interface Attachment {
  id: string;
  filename: string;
  url: string;
  mimeType: string;
  size: number;
  uploadedAt: string;
}

export interface QuickReply {
  id: string;
  text: string;
  payload: string;
  icon?: string;
}

export interface ChatContext {
  sessionId: string;
  userId: string;
  conversationHistory: ChatMessage[];
  metadata: Record<string, any>;
}

export interface ChatResponse {
  message: string;
  intent: string;
  confidence: number;
  quickReplies: QuickReply[];
  needsEscalation: boolean;
  metadata: Record<string, any>;
}

// Query Parameters
export interface ComplaintQueryParams {
  page?: number;
  limit?: number;
  category?: ComplaintCategory;
  status?: ComplaintStatus;
  priority?: Priority;
  assignedTo?: string;
  submittedBy?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface NotificationParams {
  page?: number;
  limit?: number;
  type?: NotificationType;
  isRead?: boolean;
  dateFrom?: string;
  dateTo?: string;
}

export interface TrendParams {
  period: 'week' | 'month' | 'quarter' | 'year';
  category?: ComplaintCategory;
  location?: string;
}

export interface PerformanceParams {
  period: 'week' | 'month' | 'quarter' | 'year';
  department?: string;
  officer?: string;
}

export interface GeospatialParams {
  bounds?: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  category?: ComplaintCategory;
  dateFrom?: string;
  dateTo?: string;
}

// Pagination and API Response
export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
  pageSize: number;
  currentPage: number;
  totalPages: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
  timestamp: string;
}

// Analytics Types
export interface DashboardMetrics {
  totalComplaints: number;
  pendingComplaints: number;
  resolvedComplaints: number;
  averageResolutionTime: number;
  satisfactionRating: number;
  trendsData: TrendData;
  categoryBreakdown: CategoryMetrics[];
  recentActivity: ActivityItem[];
}

export interface TrendData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
  }[];
}

export interface PerformanceData {
  metrics: PerformanceMetric[];
  comparisons: ComparisonData[];
  insights: Insight[];
}

export interface GeospatialData {
  features: GeoFeature[];
  clusters: ClusterData[];
  heatmapData: HeatmapPoint[];
}

export interface CategoryMetrics {
  category: ComplaintCategory;
  count: number;
  percentage: number;
  trend: number;
}

export interface ActivityItem {
  id: string;
  type: 'complaint_created' | 'complaint_resolved' | 'assignment_changed';
  description: string;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface PerformanceMetric {
  name: string;
  value: number;
  target: number;
  unit: string;
  trend: number;
}

export interface ComparisonData {
  period: string;
  value: number;
  change: number;
}

export interface Insight {
  type: 'positive' | 'negative' | 'neutral';
  title: string;
  description: string;
  recommendation?: string;
}

export interface GeoFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number];
  };
  properties: {
    complaintId: string;
    category: ComplaintCategory;
    status: ComplaintStatus;
    title: string;
  };
}

export interface ClusterData {
  center: [number, number];
  count: number;
  category: ComplaintCategory;
}

export interface HeatmapPoint {
  lat: number;
  lng: number;
  weight: number;
}

export interface ComplaintHistory {
  id: string;
  action: string;
  description: string;
  performedBy: User;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface ProfileUpdateData {
  firstName?: string;
  lastName?: string;
  email?: string;
  phoneNumber?: string;
  address?: Address;
  preferences?: UserPreferences;
  profilePicture?: File;
}

export interface NotificationSettings {
  email: NotificationChannelSettings;
  push: NotificationChannelSettings;
  sms: NotificationChannelSettings;
  inApp: NotificationChannelSettings;
}

export interface NotificationChannelSettings {
  enabled: boolean;
  complaintUpdates: boolean;
  systemAlerts: boolean;
  newsletter: boolean;
  marketing: boolean;
}