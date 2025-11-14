/**
 * User types
 */
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  mobile_number?: string;
  address?: string;
  role: 'citizen' | 'official' | 'admin';
  is_email_verified: boolean;
  is_mobile_verified: boolean;
  language_preference: string;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  confirm_password: string;  // Changed from password_confirm to match backend
  first_name: string;
  last_name: string;
  mobile_number?: string;
  address?: string;
  language_preference: string;
  terms_accepted: boolean;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

/**
 * Complaint types
 */
export interface Complaint {
  id: number;
  title: string;
  description: string;
  category: string;
  department: string | { id: number; name: string; zone: string; officer?: any };
  urgency: 'low' | 'medium' | 'high' | 'critical';
  status: 'submitted' | 'pending' | 'in_progress' | 'resolved' | 'closed' | 'rejected';
  latitude?: number;
  longitude?: number;
  address?: string;
  landmark?: string;
  audio_file?: string;
  image?: string;
  citizen: number;
  assigned_official?: number;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
}

export interface CreateComplaintData {
  title: string;
  description: string;
  category: string;
  department?: string;
  urgency?: string;
  latitude?: number;
  longitude?: number;
  address?: string;
  landmark?: string;
  audio_file?: File;
  image?: File;
}

/**
 * Chatbot types
 */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isLoading?: boolean;
}

export interface VoiceInputOptions {
  language?: string;
  continuous?: boolean;
  interimResults?: boolean;
}

/**
 * API response types
 */
export interface ApiError {
  detail?: string;
  message?: string;
  [key: string]: any;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/**
 * Language types
 */
export type LanguageCode =
  | 'en'
  | 'hi'
  | 'bn'
  | 'te'
  | 'mr'
  | 'ta'
  | 'gu'
  | 'kn'
  | 'ml'
  | 'or'
  | 'pa'
  | 'ur';

export interface Language {
  code: LanguageCode;
  name: string;
  nativeName: string;
}
