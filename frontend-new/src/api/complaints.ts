import { apiClient, handleApiError } from '@/lib/axios';
import type { Complaint, CreateComplaintData, PaginatedResponse } from '@/types';

/**
 * Complaint API calls
 */
export const complaintApi = {
  // Get all complaints (paginated)
  getComplaints: async (page = 1, pageSize = 10): Promise<PaginatedResponse<Complaint>> => {
    try {
      const token = localStorage.getItem('access_token');
      console.log('[API] Fetching complaints with auth token:', token ? 'Present' : 'Missing');
      
      // Decode JWT to see which user it belongs to (just for debugging)
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          console.log('[API] Token belongs to user ID:', payload.user_id);
        } catch (e) {
          console.error('[API] Could not decode token');
        }
      }
      
      const response = await apiClient.get<any>(
        `/complaints/?page=${page}&page_size=${pageSize}`
      );
      console.log('[API] Complaints response:', response.data);
      console.log('[API] Response type:', Array.isArray(response.data) ? 'Array' : 'Object');
      
      // Handle both array and paginated response formats
      if (Array.isArray(response.data)) {
        console.log('[API] Got array format, converting to paginated format');
        return {
          count: response.data.length,
          next: null,
          previous: null,
          results: response.data
        };
      }
      
      console.log('[API] Complaints count:', response.data?.count);
      console.log('[API] Complaints results:', response.data?.results);
      return response.data;
    } catch (error) {
      console.error('[API] Complaints fetch error:', error);
      throw new Error(handleApiError(error));
    }
  },

  // Get single complaint
  getComplaint: async (id: number): Promise<Complaint> => {
    try {
      const response = await apiClient.get<Complaint>(`/complaints/${id}/`);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Create complaint
  createComplaint: async (data: CreateComplaintData): Promise<Complaint> => {
    try {
      const formData = new FormData();
      
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (value instanceof File) {
            formData.append(key, value);
          } else {
            formData.append(key, value.toString());
          }
        }
      });

      const response = await apiClient.post<Complaint>('/complaints/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Update complaint
  updateComplaint: async (id: number, data: Partial<CreateComplaintData>): Promise<Complaint> => {
    try {
      const response = await apiClient.patch<Complaint>(`/complaints/${id}/`, data);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Delete complaint
  deleteComplaint: async (id: number): Promise<void> => {
    try {
      await apiClient.delete(`/complaints/${id}/`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
