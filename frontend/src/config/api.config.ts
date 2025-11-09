/**
 * Centralized API Configuration
 * Single source of truth for all backend API URLs
 */

/**
 * Get the backend API base URL based on environment
 * @returns The base URL for the backend API
 */
export const getApiBaseUrl = (): string => {
  // Check if running in development (localhost)
  const isDevelopment = 
    window.location.hostname === 'localhost' || 
    window.location.hostname === '127.0.0.1';

  if (isDevelopment) {
    // Development: Use localhost backend
    return 'http://127.0.0.1:8000';
  } else {
    // Production: Use same host with port 8000
    return `http://${window.location.hostname}:8000`;
  }
};

/**
 * API Endpoints Configuration
 * All backend endpoints in one place
 */
export const API_ENDPOINTS = {
  // Base URL
  BASE_URL: getApiBaseUrl(),

  // Authentication Endpoints
  AUTH: {
    LOGIN: '/api/auth/login/',
    REGISTER: '/api/auth/register/',
    PROFILE: '/api/auth/profile/',
    CHANGE_PASSWORD: '/api/auth/change-password/',
    FORGOT_PASSWORD: '/api/auth/forgot-password/', // Not implemented yet
    VERIFY_EMAIL: '/api/auth/verify-email/',
    VERIFY_MOBILE: '/api/auth/verify-mobile/',
    RESEND_EMAIL_VERIFICATION: '/api/auth/resend-email-verification/',
    RESEND_MOBILE_OTP: '/api/auth/resend-mobile-otp/',
    PASSWORD_RESET: '/api/auth/password-reset/',
    PASSWORD_RESET_CONFIRM: '/api/auth/password-reset/confirm/',
    TWO_FACTOR_AUTH: '/api/auth/2fa/',
  },

  // Token Endpoints
  TOKEN: {
    OBTAIN: '/api/token/',
    REFRESH: '/api/token/refresh/',
  },

  // Complaint Endpoints
  COMPLAINTS: {
    LIST_CREATE: '/api/complaints/',
    SUBMIT: '/api/complaints/submit/',
    SUBMIT_QUICK: '/api/complaints/submit/quick/',
    MY_COMPLAINTS: '/api/complaints/my-complaints/',
    DETAIL: (id: number) => `/api/complaints/view/${id}/`,
    MEDIA_UPLOAD: (id: number) => `/api/complaints/${id}/media/`,
    CLASSIFY: '/api/complaints/classify/',
    API_PROCESS: '/api/complaints/api/process/',
    API_HEALTH: '/api/complaints/api/health/',
    CATEGORIES: '/api/complaints/categories/',
    DEPARTMENTS_LIST: '/api/complaints/departments-list/',
  },

  // Chatbot Endpoints
  CHATBOT: {
    CHAT: '/api/chatbot/chat/',
    HEALTH: '/api/chatbot/health/',
    // CivicAI Voice Assistant
    VOICE_SUBMIT: '/api/chatbot/voice/submit/',
    VOICE_CHAT: '/api/chatbot/voice/chat/',
    VOICE_LANGUAGES: '/api/chatbot/voice/languages/',
    VOICE_HEALTH: '/api/chatbot/voice/health/',
  },

  // ML Endpoints (if needed)
  ML: {
    BASE: '/api/ml/',
  },
};

/**
 * Build full URL for an endpoint
 * @param endpoint - The endpoint path (e.g., '/api/auth/login/')
 * @returns Full URL (e.g., 'http://127.0.0.1:8000/api/auth/login/')
 */
export const buildApiUrl = (endpoint: string): string => {
  const baseUrl = getApiBaseUrl();
  return `${baseUrl}${endpoint}`;
};

/**
 * Export convenience function for getting full URLs
 */
export const API_URLS = {
  // Auth
  LOGIN: () => buildApiUrl(API_ENDPOINTS.AUTH.LOGIN),
  REGISTER: () => buildApiUrl(API_ENDPOINTS.AUTH.REGISTER),
  PROFILE: () => buildApiUrl(API_ENDPOINTS.AUTH.PROFILE),
  TOKEN_REFRESH: () => buildApiUrl(API_ENDPOINTS.TOKEN.REFRESH),
  VERIFY_EMAIL: buildApiUrl(API_ENDPOINTS.AUTH.VERIFY_EMAIL),
  VERIFY_MOBILE: buildApiUrl(API_ENDPOINTS.AUTH.VERIFY_MOBILE),
  RESEND_EMAIL_VERIFICATION: buildApiUrl(API_ENDPOINTS.AUTH.RESEND_EMAIL_VERIFICATION),
  RESEND_MOBILE_OTP: buildApiUrl(API_ENDPOINTS.AUTH.RESEND_MOBILE_OTP),
  PASSWORD_RESET: buildApiUrl(API_ENDPOINTS.AUTH.PASSWORD_RESET),
  PASSWORD_RESET_CONFIRM: buildApiUrl(API_ENDPOINTS.AUTH.PASSWORD_RESET_CONFIRM),
  TWO_FACTOR_AUTH: buildApiUrl(API_ENDPOINTS.AUTH.TWO_FACTOR_AUTH),
  
  // Complaints
  SUBMIT_COMPLAINT: () => buildApiUrl(API_ENDPOINTS.COMPLAINTS.SUBMIT),
  MY_COMPLAINTS: () => buildApiUrl(API_ENDPOINTS.COMPLAINTS.MY_COMPLAINTS),
  CLASSIFY_COMPLAINT: () => buildApiUrl(API_ENDPOINTS.COMPLAINTS.CLASSIFY),
  COMPLAINT_CATEGORIES: buildApiUrl(API_ENDPOINTS.COMPLAINTS.CATEGORIES),
  COMPLAINT_DEPARTMENTS: buildApiUrl(API_ENDPOINTS.COMPLAINTS.DEPARTMENTS_LIST),
  
  // Chatbot
  CHATBOT_CHAT: () => buildApiUrl(API_ENDPOINTS.CHATBOT.CHAT),
  CHATBOT_HEALTH: () => buildApiUrl(API_ENDPOINTS.CHATBOT.HEALTH),
  
  // CivicAI Voice Assistant
  VOICE_SUBMIT: () => buildApiUrl(API_ENDPOINTS.CHATBOT.VOICE_SUBMIT),
  VOICE_CHAT: () => buildApiUrl(API_ENDPOINTS.CHATBOT.VOICE_CHAT),
  VOICE_LANGUAGES: () => buildApiUrl(API_ENDPOINTS.CHATBOT.VOICE_LANGUAGES),
  VOICE_HEALTH: () => buildApiUrl(API_ENDPOINTS.CHATBOT.VOICE_HEALTH),
};

export default {
  getApiBaseUrl,
  API_ENDPOINTS,
  buildApiUrl,
  API_URLS,
};
