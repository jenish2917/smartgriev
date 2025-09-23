/**
 * Custom Hooks for Clean Architecture
 * Business logic hooks that use repositories and services
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useService } from '@/core/container';
import {
  User,
  LoginCredentials,
  RegisterData,
  Complaint,
  ComplaintQueryParams,
  CreateComplaintData,
  UpdateComplaintData,
  PaginatedResponse,
  DashboardMetrics,
  ChatMessage,
  ChatResponse,
  Notification,
  NotificationParams,
  TrendParams,
  TrendData
} from '@/types/core';

// Generic hook for async operations
interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

function useAsyncOperation<T>(): [
  AsyncState<T>,
  (operation: () => Promise<T>) => Promise<void>,
  () => void
] {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (operation: () => Promise<T>) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const result = await operation();
      setState({ data: result, loading: false, error: null });
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error instanceof Error ? error.message : 'An error occurred' 
      }));
    }
  }, []);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return [state, execute, reset];
}

// Authentication hooks
export function useAuth() {
  const authRepository = useService('authRepository');
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const [loginState, executeLogin] = useAsyncOperation<User>();
  const [registerState, executeRegister] = useAsyncOperation<User>();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = useCallback(async () => {
    try {
      const currentUser = await authRepository.getCurrentUser();
      setUser(currentUser);
      setIsAuthenticated(true);
    } catch (error) {
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }, [authRepository]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    await executeLogin(async () => {
      const response = await authRepository.login(credentials);
      setUser(response.user);
      setIsAuthenticated(true);
      return response.user;
    });
  }, [authRepository, executeLogin]);

  const register = useCallback(async (userData: RegisterData) => {
    await executeRegister(async () => {
      const response = await authRepository.register(userData);
      setUser(response.user);
      setIsAuthenticated(true);
      return response.user;
    });
  }, [authRepository, executeRegister]);

  const logout = useCallback(async () => {
    try {
      await authRepository.logout();
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  }, [authRepository]);

  const updateProfile = useCallback(async (data: any) => {
    const updatedUser = await authRepository.updateProfile(data);
    setUser(updatedUser);
    return updatedUser;
  }, [authRepository]);

  return {
    user,
    isAuthenticated,
    isLoading,
    login: {
      execute: login,
      loading: loginState.loading,
      error: loginState.error,
    },
    register: {
      execute: register,
      loading: registerState.loading,
      error: registerState.error,
    },
    logout,
    updateProfile,
    checkAuthStatus,
  };
}

// Complaints hooks
export function useComplaints(params?: ComplaintQueryParams) {
  const complaintRepository = useService('complaintRepository');
  const [complaints, setComplaints] = useState<PaginatedResponse<Complaint> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComplaints = useCallback(async (queryParams?: ComplaintQueryParams) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await complaintRepository.getComplaints(queryParams || params || {});
      setComplaints(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch complaints');
    } finally {
      setLoading(false);
    }
  }, [complaintRepository, params]);

  useEffect(() => {
    fetchComplaints();
  }, [fetchComplaints]);

  const refresh = useCallback(() => {
    fetchComplaints(params);
  }, [fetchComplaints, params]);

  return {
    complaints,
    loading,
    error,
    refresh,
    fetchComplaints,
  };
}

export function useComplaint(id?: string) {
  const complaintRepository = useService('complaintRepository');
  const [complaint, setComplaint] = useState<Complaint | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComplaint = useCallback(async (complaintId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await complaintRepository.getComplaintById(complaintId);
      setComplaint(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch complaint');
    } finally {
      setLoading(false);
    }
  }, [complaintRepository]);

  useEffect(() => {
    if (id) {
      fetchComplaint(id);
    }
  }, [id, fetchComplaint]);

  const createComplaint = useCallback(async (data: CreateComplaintData) => {
    const newComplaint = await complaintRepository.createComplaint(data);
    return newComplaint;
  }, [complaintRepository]);

  const updateComplaint = useCallback(async (complaintId: string, data: UpdateComplaintData) => {
    const updatedComplaint = await complaintRepository.updateComplaint(complaintId, data);
    if (complaintId === id) {
      setComplaint(updatedComplaint);
    }
    return updatedComplaint;
  }, [complaintRepository, id]);

  const deleteComplaint = useCallback(async (complaintId: string) => {
    await complaintRepository.deleteComplaint(complaintId);
    if (complaintId === id) {
      setComplaint(null);
    }
  }, [complaintRepository, id]);

  return {
    complaint,
    loading,
    error,
    createComplaint,
    updateComplaint,
    deleteComplaint,
    refresh: () => id && fetchComplaint(id),
  };
}

// Analytics hooks
export function useDashboard() {
  const analyticsRepository = useService('analyticsRepository');
  const [dashboardState, executeFetch] = useAsyncOperation<DashboardMetrics>();

  const fetchDashboard = useCallback(() => {
    executeFetch(() => analyticsRepository.getDashboardMetrics());
  }, [analyticsRepository, executeFetch]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return {
    ...dashboardState,
    refresh: fetchDashboard,
  };
}

export function useTrends(params: TrendParams) {
  const analyticsRepository = useService('analyticsRepository');
  const [trendsState, executeFetch] = useAsyncOperation<TrendData>();

  const fetchTrends = useCallback(() => {
    executeFetch(() => analyticsRepository.getComplaintTrends(params));
  }, [analyticsRepository, executeFetch, params]);

  useEffect(() => {
    fetchTrends();
  }, [fetchTrends]);

  return {
    ...trendsState,
    refresh: fetchTrends,
  };
}

// Chatbot hooks
export function useChatbot() {
  const chatbotRepository = useService('chatbotRepository');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random()}`);
  const [isTyping, setIsTyping] = useState(false);

  const sendMessage = useCallback(async (message: string) => {
    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      message,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await chatbotRepository.sendMessage(message, {
        sessionId,
        userId: 'current_user', // Should come from auth context
        conversationHistory: messages,
        metadata: {},
      });

      const botMessage: ChatMessage = {
        id: `msg_${Date.now()}_bot`,
        message: response.message,
        sender: 'bot',
        timestamp: new Date().toISOString(),
        intent: response.intent,
        confidence: response.confidence,
        quickReplies: response.quickReplies,
        metadata: response.metadata,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: `msg_${Date.now()}_error`,
        message: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [chatbotRepository, sessionId, messages]);

  const clearConversation = useCallback(async () => {
    try {
      await chatbotRepository.clearConversation(sessionId);
      setMessages([]);
    } catch (error) {
      console.error('Failed to clear conversation:', error);
    }
  }, [chatbotRepository, sessionId]);

  return {
    messages,
    isTyping,
    sendMessage,
    clearConversation,
  };
}

// Notifications hooks
export function useNotifications(params?: NotificationParams) {
  const notificationRepository = useService('notificationRepository');
  const [notifications, setNotifications] = useState<PaginatedResponse<Notification> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await notificationRepository.getNotifications(params || {});
      setNotifications(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch notifications');
    } finally {
      setLoading(false);
    }
  }, [notificationRepository, params]);

  const markAsRead = useCallback(async (id: string) => {
    await notificationRepository.markAsRead(id);
    await fetchNotifications(); // Refresh
  }, [notificationRepository, fetchNotifications]);

  const markAllAsRead = useCallback(async () => {
    await notificationRepository.markAllAsRead();
    await fetchNotifications(); // Refresh
  }, [notificationRepository, fetchNotifications]);

  const deleteNotification = useCallback(async (id: string) => {
    await notificationRepository.deleteNotification(id);
    await fetchNotifications(); // Refresh
  }, [notificationRepository, fetchNotifications]);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const unreadCount = useMemo(() => {
    return notifications?.results.filter(n => !n.isRead).length || 0;
  }, [notifications]);

  return {
    notifications,
    loading,
    error,
    unreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    refresh: fetchNotifications,
  };
}

// Form hooks
export function useForm<T>(initialValues: T, validationRules?: any) {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});

  const setValue = useCallback((field: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  }, [errors]);

  const setFieldTouched = useCallback((field: keyof T) => {
    setTouched(prev => ({ ...prev, [field]: true }));
  }, []);

  const validate = useCallback(() => {
    if (!validationRules) return true;
    
    const newErrors: Partial<Record<keyof T, string>> = {};
    let isValid = true;

    Object.keys(validationRules).forEach(field => {
      const fieldKey = field as keyof T;
      const rules = validationRules[field];
      const value = values[fieldKey];

      if (rules.required && (!value || value === '')) {
        newErrors[fieldKey] = `${String(field)} is required`;
        isValid = false;
      }
      
      if (value && rules.minLength && String(value).length < rules.minLength) {
        newErrors[fieldKey] = `${String(field)} must be at least ${rules.minLength} characters`;
        isValid = false;
      }
      
      if (value && rules.pattern && !rules.pattern.test(String(value))) {
        newErrors[fieldKey] = rules.message || `${String(field)} format is invalid`;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  }, [values, validationRules]);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  const isValid = useMemo(() => {
    return Object.keys(errors).length === 0;
  }, [errors]);

  return {
    values,
    errors,
    touched,
    isValid,
    setValue,
    setFieldTouched,
    validate,
    reset,
  };
}

// Pagination hook
export function usePagination(initialPage = 1, initialPageSize = 10) {
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);

  const goToPage = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  const nextPage = useCallback(() => {
    setPage(prev => prev + 1);
  }, []);

  const prevPage = useCallback(() => {
    setPage(prev => Math.max(1, prev - 1));
  }, []);

  const changePageSize = useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(1); // Reset to first page when changing page size
  }, []);

  const reset = useCallback(() => {
    setPage(initialPage);
    setPageSize(initialPageSize);
  }, [initialPage, initialPageSize]);

  return {
    page,
    pageSize,
    goToPage,
    nextPage,
    prevPage,
    changePageSize,
    reset,
  };
}