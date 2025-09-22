import api from './api';
import { BaseService, ServiceError } from './BaseService';
import {
  Complaint,
  CreateComplaintData,
  PaginatedResponse,
  ComplaintStatus,
  ComplaintPriority,
  Department,
  FilterParams,
} from '@/types';

// Additional types for the service
export interface UpdateComplaintData extends Partial<CreateComplaintData> {
  status?: ComplaintStatus;
  priority?: ComplaintPriority;
  notes?: string;
}

export interface ComplaintFilters extends FilterParams {
  page?: number;
  page_size?: number;
  user?: number;
  assigned_officer?: number;
}

export interface ComplaintComment {
  id: number;
  user: number;
  user_name: string;
  comment: string;
  created_at: string;
}

/**
 * Service class for complaint-related API operations
 */
export class ComplaintService extends BaseService {
  constructor() {
    super('/complaints');
  }

  /**
   * Get paginated list of complaints with optional filters
   */
  async getComplaints(filters: ComplaintFilters = {}): Promise<PaginatedResponse<Complaint>> {
    try {
      this.log('getComplaints', filters);
      
      const cacheKey = `complaints_${JSON.stringify(filters)}`;
      const cached = this.getCached<PaginatedResponse<Complaint>>(cacheKey);
      if (cached) {
        this.log('Returning cached complaints');
        return cached;
      }

      const queryString = this.buildQueryString(filters);
      const response = await api.get<PaginatedResponse<Complaint>>(`${this.endpoint}/${queryString}`);
      const data = this.transformPaginatedResponse(response);
      
      // Cache for 2 minutes
      this.setCached(cacheKey, data, 2 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get a specific complaint by ID
   */
  async getComplaint(id: number): Promise<Complaint> {
    try {
      this.log('getComplaint', { id });
      
      const cacheKey = `complaint_${id}`;
      const cached = this.getCached<Complaint>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<Complaint>(`${this.endpoint}/${id}/`);
      const data = this.transformResponse(response);
      
      // Cache for 5 minutes
      this.setCached(cacheKey, data, 5 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Create a new complaint
   */
  async createComplaint(data: CreateComplaintData): Promise<Complaint> {
    try {
      this.log('createComplaint', data);
      
      // Validate required fields
      this.validateRequest(data, ['title', 'description', 'category']);
      
      let requestData: FormData | CreateComplaintData;
      
      // Handle file uploads
      if (data.media) {
        requestData = this.createFormData(data);
      } else {
        requestData = data;
      }

      const response = await api.post<Complaint>(`${this.endpoint}/`, requestData, {
        headers: {
          'Content-Type': data.media ? 'multipart/form-data' : 'application/json',
        },
      });
      
      const newComplaint = this.transformResponse(response);
      
      // Clear complaints cache since we added a new complaint
      this.clearCache('complaints_');
      
      return newComplaint;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Update an existing complaint
   */
  async updateComplaint(id: number, data: UpdateComplaintData): Promise<Complaint> {
    try {
      this.log('updateComplaint', { id, data });
      
      let requestData: FormData | UpdateComplaintData;
      
      // Handle file uploads
      if (data.media) {
        requestData = this.createFormData(data);
      } else {
        requestData = data;
      }

      const response = await api.patch<Complaint>(`${this.endpoint}/${id}/`, requestData, {
        headers: {
          'Content-Type': data.media ? 'multipart/form-data' : 'application/json',
        },
      });
      
      const updatedComplaint = this.transformResponse(response);
      
      // Clear relevant caches
      this.clearCache('complaints_');
      this.clearCache(`complaint_${id}`);
      
      return updatedComplaint;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Delete a complaint (soft delete)
   */
  async deleteComplaint(id: number): Promise<void> {
    try {
      this.log('deleteComplaint', { id });
      
      await api.delete(`${this.endpoint}/${id}/`);
      
      // Clear relevant caches
      this.clearCache('complaints_');
      this.clearCache(`complaint_${id}`);
      this.clearCache(`complaint_comments_${id}`);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get user's complaints
   */
  async getUserComplaints(params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<PaginatedResponse<Complaint>> {
    try {
      this.log('getUserComplaints', params);
      
      const cacheKey = `user_complaints_${JSON.stringify(params)}`;
      const cached = this.getCached<PaginatedResponse<Complaint>>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params || {});
      const response = await api.get<PaginatedResponse<Complaint>>(`${this.endpoint}/my/${queryString}`);
      const data = this.transformPaginatedResponse(response);
      
      // Cache for 1 minute
      this.setCached(cacheKey, data, 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get complaint statistics
   */
  async getComplaintStats(): Promise<{
    total: number;
    pending: number;
    resolved: number;
    by_category: Array<{ category: string; count: number }>;
    by_status: Array<{ status: string; count: number }>;
  }> {
    try {
      this.log('getComplaintStats');
      
      const cacheKey = 'complaint_stats';
      const cached = this.getCached<any>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get(`${this.endpoint}/stats/`);
      const stats = this.transformResponse(response);
      
      // Cache for 5 minutes
      this.setCached(cacheKey, stats, 5 * 60 * 1000);
      
      return stats;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Update complaint status (for officers)
   */
  async updateComplaintStatus(id: number, status: string, notes?: string): Promise<Complaint> {
    try {
      this.log('updateComplaintStatus', { id, status, notes });
      
      const response = await api.patch<Complaint>(`${this.endpoint}/${id}/status/`, {
        status,
        notes,
      });
      const updatedComplaint = this.transformResponse(response);
      
      // Clear relevant caches
      this.clearCache('complaints_');
      this.clearCache(`complaint_${id}`);
      
      return updatedComplaint;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Assign complaint to an officer
   */
  async assignComplaint(id: number, officer_id: number): Promise<Complaint> {
    try {
      this.log('assignComplaint', { id, officer_id });
      
      const response = await api.patch<Complaint>(`${this.endpoint}/${id}/assign/`, {
        officer_id,
      });
      const updatedComplaint = this.transformResponse(response);
      
      // Clear relevant caches
      this.clearCache('complaints_');
      this.clearCache(`complaint_${id}`);
      
      return updatedComplaint;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Add comment to complaint
   */
  async addComment(complaint_id: number, comment: string): Promise<{ id: number; comment: string; created_at: string }> {
    try {
      this.log('addComment', { complaint_id, comment });
      
      if (!comment.trim()) {
        throw new ServiceError('Comment cannot be empty');
      }

      const response = await api.post(`${this.endpoint}/${complaint_id}/comments/`, {
        comment: comment.trim(),
      });
      
      const newComment = this.transformResponse(response);
      
      // Clear comments cache
      this.clearCache(`complaint_comments_${complaint_id}`);
      
      return newComment;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get complaint comments
   */
  async getComments(complaint_id: number): Promise<Array<{
    id: number;
    user: number;
    user_name: string;
    comment: string;
    created_at: string;
  }>> {
    try {
      this.log('getComments', { complaint_id });
      
      const cacheKey = `complaint_comments_${complaint_id}`;
      const cached = this.getCached<any[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get(`${this.endpoint}/${complaint_id}/comments/`);
      const comments = this.transformResponse(response);
      
      // Cache for 1 minute
      this.setCached(cacheKey, comments, 60 * 1000);
      
      return comments;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get departments
   */
  async getDepartments(): Promise<Department[]> {
    try {
      this.log('getDepartments');
      
      const cacheKey = 'departments';
      const cached = this.getCached<Department[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<Department[]>(`${this.endpoint}/departments/`);
      const departments = this.transformResponse(response);
      
      // Cache for 10 minutes (departments don't change often)
      this.setCached(cacheKey, departments, 10 * 60 * 1000);
      
      return departments;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get complaint categories
   */
  async getCategories(): Promise<string[]> {
    try {
      this.log('getCategories');
      
      const cacheKey = 'categories';
      const cached = this.getCached<string[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<string[]>(`${this.endpoint}/categories/`);
      const categories = this.transformResponse(response);
      
      // Cache for 10 minutes (categories don't change often)
      this.setCached(cacheKey, categories, 10 * 60 * 1000);
      
      return categories;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Search complaints by text
   */
  async searchComplaints(query: string, filters?: FilterParams): Promise<Complaint[]> {
    try {
      this.log('searchComplaints', { query, filters });
      
      if (!query.trim()) {
        return [];
      }

      const searchParams = {
        q: query.trim(),
        ...filters,
      };
      
      const queryString = this.buildQueryString(searchParams);
      const response = await api.get<Complaint[]>(`${this.endpoint}/search/${queryString}`);
      
      return this.transformResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Export complaints data
   */
  async exportComplaints(format: 'csv' | 'excel', filters?: FilterParams): Promise<Blob> {
    try {
      this.log('exportComplaints', { format, filters });
      
      const params = {
        format,
        ...filters,
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

  /**
   * Get nearby complaints (geospatial)
   */
  async getNearbyComplaints(
    latitude: number,
    longitude: number,
    radius: number = 5000 // meters
  ): Promise<Complaint[]> {
    try {
      this.log('getNearbyComplaints', { latitude, longitude, radius });
      
      const queryString = this.buildQueryString({
        lat: latitude,
        lon: longitude,
        radius,
      });
      const response = await api.get<Complaint[]>(`${this.endpoint}/nearby/${queryString}`);
      
      return this.transformResponse(response) as Complaint[];
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Report complaint (for inappropriate content)
   */
  async reportComplaint(id: number, reason: string): Promise<{ message: string }> {
    try {
      this.log('reportComplaint', { id, reason });
      
      if (!reason.trim()) {
        throw new ServiceError('Report reason cannot be empty');
      }
      
      const response = await api.post(`${this.endpoint}/${id}/report/`, { 
        reason: reason.trim() 
      });
      
      return this.transformResponse(response);
    } catch (error) {
      this.handleError(error as any);
    }
  }
}

// Export singleton instance
export const complaintService = new ComplaintService();
export default complaintService;
