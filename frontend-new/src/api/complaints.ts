import { apiClient, handleApiError } from '@/lib/axios';
import type { Complaint, CreateComplaintData, PaginatedResponse } from '@/types';

/**
 * Complaint API calls
 */
export const complaintApi = {
  // Get all complaints (paginated)
  getComplaints: async (page = 1, pageSize = 10): Promise<PaginatedResponse<Complaint>> => {
    try {
      const response = await apiClient.get<PaginatedResponse<Complaint>>(
        `/api/complaints/?page=${page}&page_size=${pageSize}`
      );
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Get single complaint
  getComplaint: async (id: number): Promise<Complaint> => {
    try {
      const response = await apiClient.get<Complaint>(`/api/complaints/${id}/`);
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

      const response = await apiClient.post<Complaint>('/api/complaints/', formData, {
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
      const response = await apiClient.patch<Complaint>(`/api/complaints/${id}/`, data);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // Delete complaint
  deleteComplaint: async (id: number): Promise<void> => {
    try {
      await apiClient.delete(`/api/complaints/${id}/`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
