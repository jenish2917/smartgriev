import api from './api';
import { BaseService, ServiceError } from './BaseService';
import {
  ChatMessage,
  ChatRequest,
  ChatStats,
  PaginatedResponse,
} from '@/types';

// Chatbot-specific types
export interface ChatSession {
  id: string;
  user_id: number;
  title: string;
  started_at: string;
  last_activity: string;
  message_count: number;
  status: 'active' | 'completed' | 'escalated';
  escalated_to_human?: boolean;
  assigned_agent?: number;
}

export interface ChatResponse {
  response: string;
  intent?: string;
  confidence?: number;
  suggestions?: string[];
  escalate_to_human?: boolean;
}

export interface ChatContext {
  user_id: number;
  session_id?: string;
  conversation_history?: ChatMessage[];
  user_profile?: {
    language: string;
    location?: string;
    complaint_history?: any[];
  };
}

export interface ChatFilters {
  page?: number;
  page_size?: number;
  start_date?: string;
  end_date?: string;
  session_id?: string;
  user_id?: number;
  intent?: string;
  escalated?: boolean;
}

/**
 * Service class for chatbot and AI assistant operations
 */
export class ChatbotService extends BaseService {
  constructor() {
    super('/chatbot');
  }

  /**
   * Send message to chatbot
   */
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    try {
      this.log('sendMessage', data);
      
      // Validate required fields
      this.validateRequest(data, ['message']);
      
      const response = await api.post<ChatResponse>(`${this.endpoint}/chat/`, data);
      
      return this.transformResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get chat history
   */
  async getChatHistory(params: ChatFilters = {}): Promise<PaginatedResponse<ChatMessage>> {
    try {
      this.log('getChatHistory', params);
      
      const cacheKey = `chat_history_${JSON.stringify(params)}`;
      const cached = this.getCached<PaginatedResponse<ChatMessage>>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params);
      const response = await api.get<PaginatedResponse<ChatMessage>>(`${this.endpoint}/history/${queryString}`);
      const data = this.transformPaginatedResponse(response);
      
      // Cache for 2 minutes
      this.setCached(cacheKey, data, 2 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get chat statistics
   */
  async getChatStats(): Promise<ChatStats> {
    try {
      this.log('getChatStats');
      
      const cacheKey = 'chat_stats';
      const cached = this.getCached<ChatStats>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<ChatStats>(`${this.endpoint}/stats/`);
      const data = this.transformResponse(response);
      
      // Cache for 5 minutes
      this.setCached(cacheKey, data, 5 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Provide feedback on chat response
   */
  async provideFeedback(
    chat_id: number,
    feedback: {
      rating: number; // 1-5
      is_helpful: boolean;
      comment?: string;
    }
  ): Promise<{ message: string }> {
    try {
      this.log('provideFeedback', { chat_id, feedback });
      
      // Validate rating range
      if (feedback.rating < 1 || feedback.rating > 5) {
        throw new ServiceError('Rating must be between 1 and 5');
      }

      const response = await api.post(`${this.endpoint}/feedback/${chat_id}/`, feedback);
      
      return this.transformResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get suggested responses (for officers)
   */
  async getSuggestedResponses(complaint_id: number): Promise<{
    suggestions: Array<{
      text: string;
      confidence: number;
      template_id?: number;
    }>;
    templates: Array<{
      id: number;
      title: string;
      content: string;
      category: string;
    }>;
  }> {
    try {
      this.log('getSuggestedResponses', { complaint_id });
      
      const cacheKey = `suggested_responses_${complaint_id}`;
      const cached = this.getCached<any>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get(`${this.endpoint}/suggestions/${complaint_id}/`);
      const data = this.transformResponse(response);
      
      // Cache for 10 minutes
      this.setCached(cacheKey, data, 10 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Start a new chat session
   */
  async startSession(context: Partial<ChatContext> = {}): Promise<ChatSession> {
    try {
      this.log('startSession', context);
      
      const response = await api.post<ChatSession>(`${this.endpoint}/sessions/`, context);
      const session = this.transformResponse(response);
      
      // Cache the session
      this.setCached(`chat_session_${session.id}`, session, 30 * 60 * 1000); // 30 minutes
      
      return session;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get an existing chat session
   */
  async getSession(sessionId: string): Promise<ChatSession> {
    try {
      this.log('getSession', { sessionId });
      
      const cacheKey = `chat_session_${sessionId}`;
      const cached = this.getCached<ChatSession>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<ChatSession>(`${this.endpoint}/sessions/${sessionId}/`);
      const session = this.transformResponse(response);
      
      // Cache for 10 minutes
      this.setCached(cacheKey, session, 10 * 60 * 1000);
      
      return session;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * End a chat session
   */
  async endSession(
    sessionId: string,
    feedback?: {
      rating: number;
      comment?: string;
      helpful: boolean;
    }
  ): Promise<{
    ended: boolean;
    session_summary: {
      duration: number;
      message_count: number;
      resolved: boolean;
      escalated: boolean;
    };
  }> {
    try {
      this.log('endSession', { sessionId, feedback });
      
      const requestData = feedback ? { feedback } : {};
      
      const response = await api.post(`${this.endpoint}/sessions/${sessionId}/end/`, requestData);
      const result = this.transformResponse(response);
      
      // Clear all caches for this session
      this.clearCache(`chat_session_${sessionId}`);
      
      return result;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Escalate session to human agent
   */
  async escalateToHuman(
    sessionId: string,
    reason: string,
    priority: 'low' | 'medium' | 'high' = 'medium'
  ): Promise<{
    escalated: boolean;
    ticket_id: string;
    estimated_wait_time?: number;
    message: string;
  }> {
    try {
      this.log('escalateToHuman', { sessionId, reason, priority });
      
      if (!reason.trim()) {
        throw new ServiceError('Escalation reason cannot be empty');
      }

      const response = await api.post(`${this.endpoint}/sessions/${sessionId}/escalate/`, {
        reason: reason.trim(),
        priority,
      });
      
      const result = this.transformResponse(response);
      
      // Clear session cache
      this.clearCache(`chat_session_${sessionId}`);
      
      return result;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get chatbot analytics
   */
  async getAnalytics(filters: {
    start_date?: string;
    end_date?: string;
    group_by?: 'day' | 'week' | 'month';
  } = {}): Promise<{
    total_sessions: number;
    total_messages: number;
    avg_session_duration: number;
    escalation_rate: number;
    resolution_rate: number;
    user_satisfaction: number;
    top_intents: Array<{
      intent: string;
      count: number;
      avg_confidence: number;
    }>;
    session_trends: Array<{
      date: string;
      sessions: number;
      messages: number;
      escalations: number;
    }>;
  }> {
    try {
      this.log('getAnalytics', filters);
      
      const cacheKey = `chatbot_analytics_${JSON.stringify(filters)}`;
      const cached = this.getCached<any>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(filters);
      const response = await api.get(`${this.endpoint}/analytics/${queryString}`);
      const analytics = this.transformResponse(response);
      
      // Cache for 10 minutes
      this.setCached(cacheKey, analytics, 10 * 60 * 1000);
      
      return analytics;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get user's chat sessions
   */
  async getUserSessions(
    userId?: number,
    filters: {
      page?: number;
      page_size?: number;
      status?: 'active' | 'completed' | 'escalated';
      start_date?: string;
      end_date?: string;
    } = {}
  ): Promise<PaginatedResponse<ChatSession>> {
    try {
      this.log('getUserSessions', { userId, filters });
      
      const endpoint = userId 
        ? `${this.endpoint}/users/${userId}/sessions/`
        : `${this.endpoint}/my-sessions/`;
      
      const queryString = this.buildQueryString(filters);
      const response = await api.get<PaginatedResponse<ChatSession>>(`${endpoint}${queryString}`);
      
      return this.transformPaginatedResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Export chat data
   */
  async exportChatData(
    filters: {
      start_date?: string;
      end_date?: string;
      user_id?: number;
      session_id?: string;
      include_messages?: boolean;
    },
    format: 'csv' | 'json' | 'excel' = 'csv'
  ): Promise<Blob> {
    try {
      this.log('exportChatData', { filters, format });
      
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
export const chatbotService = new ChatbotService();
export default chatbotService;