import { apiClient, handleApiError } from '@/lib/axios';
import type { ChatMessage } from '@/types';

/**
 * Chatbot API calls
 */
export const chatbotApi = {
  // Send message to chatbot with optional location
  sendMessage: async (
    message: string, 
    language = 'en',
    location?: { latitude: number; longitude: number } | null,
    sessionId?: string
  ): Promise<{ response: string; session_id?: string }> => {
    try {
      const payload: { 
        message: string; 
        language: string; 
        latitude?: number; 
        longitude?: number;
        session_id?: string;
      } = {
        message,
        language,
      };
      
      if (location) {
        payload.latitude = location.latitude;
        payload.longitude = location.longitude;
      }
      
      if (sessionId) {
        payload.session_id = sessionId;
      }
      
      const response = await apiClient.post<{ response: string; session_id?: string }>('/chatbot/chat/', payload);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Send voice message
  sendVoiceMessage: async (audioFile: File, language = 'en'): Promise<{ response: string; transcription: string }> => {
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('language', language);

      const response = await apiClient.post<{ response: string; transcription: string }>(
        '/chatbot/voice/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Send image for vision processing with optional location
  sendImage: async (
    imageFile: File, 
    message?: string,
    location?: { latitude: number; longitude: number } | null,
    language = 'en'
  ): Promise<{ response: string; description: string }> => {
    try {
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('language', language);
      if (message) formData.append('message', message);
      if (location) {
        formData.append('latitude', location.latitude.toString());
        formData.append('longitude', location.longitude.toString());
      }

      const response = await apiClient.post<{ response: string; description: string }>(
        '/chatbot/vision/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Get chat history
  getChatHistory: async (): Promise<ChatMessage[]> => {
    try {
      const response = await apiClient.get<ChatMessage[]>('/chatbot/history/');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
