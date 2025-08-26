import { apiService } from './api';
import {
  Complaint,
  CreateComplaintData,
  Department,
  PaginatedResponse,
  FilterParams,
} from '@/types';

export const complaintService = {
  // Get paginated complaints
  getComplaints: async (params?: FilterParams & {
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Complaint>> => {
    return apiService.get<PaginatedResponse<Complaint>>('/complaints/', params);
  },

  // Get single complaint by ID
  getComplaint: async (id: number): Promise<Complaint> => {
    return apiService.get<Complaint>(`/complaints/${id}/`);
  },

  // Create new complaint
  createComplaint: async (data: CreateComplaintData): Promise<Complaint> => {
    // If there's a media file, use FormData
    if (data.media) {
      const formData = new FormData();
      
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (key === 'media' && value instanceof File) {
            formData.append(key, value);
          } else {
            formData.append(key, String(value));
          }
        }
      });

      return apiService.upload<Complaint>('/complaints/', formData);
    } else {
      return apiService.post<Complaint>('/complaints/', data);
    }
  },

  // Update complaint
  updateComplaint: async (id: number, data: Partial<CreateComplaintData>): Promise<Complaint> => {
    return apiService.patch<Complaint>(`/complaints/${id}/`, data);
  },

  // Delete complaint
  deleteComplaint: async (id: number): Promise<void> => {
    return apiService.delete(`/complaints/${id}/`);
  },

  // Get user's complaints
  getUserComplaints: async (params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<PaginatedResponse<Complaint>> => {
    return apiService.get<PaginatedResponse<Complaint>>('/complaints/my/', params);
  },

  // Get complaint statistics
  getComplaintStats: async (): Promise<{
    total: number;
    pending: number;
    resolved: number;
    by_category: Array<{ category: string; count: number }>;
    by_status: Array<{ status: string; count: number }>;
  }> => {
    return apiService.get('/complaints/stats/');
  },

  // Update complaint status (for officers)
  updateComplaintStatus: async (
    id: number,
    status: string,
    notes?: string
  ): Promise<Complaint> => {
    return apiService.patch<Complaint>(`/complaints/${id}/status/`, {
      status,
      notes,
    });
  },

  // Assign complaint to officer
  assignComplaint: async (id: number, officer_id: number): Promise<Complaint> => {
    return apiService.patch<Complaint>(`/complaints/${id}/assign/`, {
      officer_id,
    });
  },

  // Add comment to complaint
  addComment: async (
    complaint_id: number,
    comment: string
  ): Promise<{ id: number; comment: string; created_at: string }> => {
    return apiService.post(`/complaints/${complaint_id}/comments/`, {
      comment,
    });
  },

  // Get complaint comments
  getComments: async (complaint_id: number): Promise<Array<{
    id: number;
    user: number;
    user_name: string;
    comment: string;
    created_at: string;
  }>> => {
    return apiService.get(`/complaints/${complaint_id}/comments/`);
  },

  // Get departments
  getDepartments: async (): Promise<Department[]> => {
    return apiService.get<Department[]>('/complaints/departments/');
  },

  // Get complaint categories
  getCategories: async (): Promise<string[]> => {
    return apiService.get<string[]>('/complaints/categories/');
  },

  // Search complaints
  searchComplaints: async (query: string, filters?: FilterParams): Promise<Complaint[]> => {
    return apiService.get<Complaint[]>('/complaints/search/', {
      q: query,
      ...filters,
    });
  },

  // Export complaints data
  exportComplaints: async (format: 'csv' | 'excel', filters?: FilterParams): Promise<void> => {
    const params = new URLSearchParams({
      format,
      ...filters,
    } as any);
    
    return apiService.download(`/complaints/export/?${params.toString()}`, 
      `complaints_${new Date().toISOString().split('T')[0]}.${format}`);
  },

  // Get nearby complaints (geospatial)
  getNearbyComplaints: async (
    latitude: number,
    longitude: number,
    radius: number = 5000 // meters
  ): Promise<Complaint[]> => {
    return apiService.get<Complaint[]>('/complaints/nearby/', {
      lat: latitude,
      lon: longitude,
      radius,
    });
  },

  // Report complaint (for inappropriate content)
  reportComplaint: async (
    id: number,
    reason: string
  ): Promise<{ message: string }> => {
    return apiService.post(`/complaints/${id}/report/`, { reason });
  },
};
