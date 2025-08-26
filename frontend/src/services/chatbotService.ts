import { apiService } from './api';
import {
  ChatMessage,
  ChatRequest,
  ChatStats,
  PaginatedResponse,
} from '@/types';

export const chatbotService = {
  // Send message to chatbot
  sendMessage: async (data: ChatRequest): Promise<{
    response: string;
    intent?: string;
    confidence?: number;
    suggestions?: string[];
    escalate_to_human?: boolean;
  }> => {
    return apiService.post('/chatbot/chat/', data);
  },

  // Get chat history
  getChatHistory: async (params?: {
    page?: number;
    page_size?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<PaginatedResponse<ChatMessage>> => {
    return apiService.get<PaginatedResponse<ChatMessage>>('/chatbot/history/', params);
  },

  // Get chat statistics
  getChatStats: async (): Promise<ChatStats> => {
    return apiService.get<ChatStats>('/chatbot/stats/');
  },

  // Provide feedback on chat response
  provideFeedback: async (
    chat_id: number,
    feedback: {
      rating: number; // 1-5
      is_helpful: boolean;
      comment?: string;
    }
  ): Promise<{ message: string }> => {
    return apiService.post(`/chatbot/feedback/${chat_id}/`, feedback);
  },

  // Get suggested responses (for officers)
  getSuggestedResponses: async (complaint_id: number): Promise<{
    suggestions: Array<{
      response: string;
      confidence: number;
      category: string;
    }>;
  }> => {
    return apiService.get(`/chatbot/suggestions/${complaint_id}/`);
  },

  // Escalate chat to human agent
  escalateToHuman: async (
    chat_id: number,
    reason?: string
  ): Promise<{ message: string; ticket_id?: number }> => {
    return apiService.post(`/chatbot/escalate/${chat_id}/`, { reason });
  },

  // Get chatbot configuration (for admins)
  getConfiguration: async (): Promise<{
    enabled_features: string[];
    confidence_threshold: number;
    max_conversation_length: number;
    available_intents: string[];
    fallback_responses: string[];
  }> => {
    return apiService.get('/chatbot/config/');
  },

  // Update chatbot configuration (for admins)
  updateConfiguration: async (config: {
    enabled_features?: string[];
    confidence_threshold?: number;
    max_conversation_length?: number;
    fallback_responses?: string[];
  }): Promise<{ message: string }> => {
    return apiService.patch('/chatbot/config/', config);
  },

  // Get training data for chatbot (for admins)
  getTrainingData: async (params?: {
    intent?: string;
    confidence_min?: number;
    confidence_max?: number;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<{
    id: number;
    message: string;
    intent: string;
    confidence: number;
    training_set: boolean;
    created_at: string;
  }>> => {
    return apiService.get('/chatbot/training-data/', params);
  },

  // Add training data (for admins)
  addTrainingData: async (data: {
    message: string;
    intent: string;
    examples?: string[];
  }): Promise<{ message: string }> => {
    return apiService.post('/chatbot/training-data/', data);
  },

  // Retrain chatbot model (for admins)
  retrainModel: async (): Promise<{
    message: string;
    task_id: string;
    estimated_completion: string;
  }> => {
    return apiService.post('/chatbot/retrain/');
  },

  // Get model performance metrics
  getModelPerformance: async (): Promise<{
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    intent_performance: Array<{
      intent: string;
      accuracy: number;
      sample_count: number;
    }>;
    last_updated: string;
  }> => {
    return apiService.get('/chatbot/performance/');
  },

  // Get conversation analytics
  getConversationAnalytics: async (params?: {
    start_date?: string;
    end_date?: string;
    group_by?: 'day' | 'week' | 'month';
  }): Promise<{
    total_conversations: number;
    avg_conversation_length: number;
    resolution_rate: number;
    escalation_rate: number;
    top_intents: Array<{
      intent: string;
      count: number;
      avg_confidence: number;
    }>;
    user_satisfaction: {
      avg_rating: number;
      rating_distribution: Array<{
        rating: number;
        count: number;
      }>;
    };
    conversation_trends: Array<{
      date: string;
      count: number;
      avg_confidence: number;
    }>;
  }> => {
    return apiService.get('/chatbot/analytics/', params);
  },

  // Clear chat history for current user
  clearChatHistory: async (): Promise<{ message: string }> => {
    return apiService.delete('/chatbot/history/clear/');
  },

  // Get chatbot health status
  getHealthStatus: async (): Promise<{
    status: 'healthy' | 'degraded' | 'down';
    model_loaded: boolean;
    response_time_avg: number;
    error_rate: number;
    last_check: string;
  }> => {
    return apiService.get('/chatbot/health/');
  },
};
