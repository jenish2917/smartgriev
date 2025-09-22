import api from './api';
import { BaseService, ServiceError } from './BaseService';
import {
  Complaint,
  PaginatedResponse,
  GeospatialCluster,
  HeatmapData,
} from '@/types';

// Geospatial-specific types
export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface BoundingBox {
  north: number;
  south: number;
  east: number;
  west: number;
}

export interface GeospatialComplaint extends Complaint {
  distance?: number; // Distance from query point in meters
  cluster_id?: number;
}

export interface LocationData {
  coordinates: Coordinates;
  address: string;
  landmark?: string;
  accuracy?: number;
  timestamp: string;
}

export interface HeatmapPoint {
  latitude: number;
  longitude: number;
  weight: number;
  complaint_count: number;
  category?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
}

export interface ClusterData {
  cluster_id: number;
  center: Coordinates;
  radius: number;
  complaint_count: number;
  dominant_category: string;
  avg_severity: number;
  complaints: GeospatialComplaint[];
}

export interface GeofenceArea {
  id: number;
  name: string;
  description?: string;
  type: 'circle' | 'polygon';
  center?: Coordinates;
  radius?: number; // for circle type
  boundaries?: Coordinates[]; // for polygon type
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LocationAnalytics {
  total_complaints: number;
  hotspots: Array<{
    id: number;
    name: string;
    latitude: number;
    longitude: number;
    complaint_count: number;
    severity_score: number;
    trend: 'increasing' | 'stable' | 'decreasing';
  }>;
  coverage_areas: Array<{
    area_name: string;
    complaint_density: number;
    avg_response_time: number;
    efficiency_score: number;
  }>;
  spatial_trends: Array<{
    date: string;
    location: Coordinates;
    complaint_count: number;
  }>;
}

export interface GeospatialFilters {
  zoom_level?: number;
  bounds?: BoundingBox;
  cluster_type?: string;
  min_complaints?: number;
  time_range?: string;
  complaint_type?: string;
  category?: string[];
  status?: string[];
  priority?: string[];
  start_date?: string;
  end_date?: string;
  include_clusters?: boolean;
  cluster_radius?: number;
  min_cluster_size?: number;
  page?: number;
  page_size?: number;
}

/**
 * Service class for geospatial and location-based operations
 */
export class GeospatialService extends BaseService {
  constructor() {
    super('/geospatial');
  }

  /**
   * Get complaint clusters
   */
  async getClusters(params: GeospatialFilters = {}): Promise<GeospatialCluster[]> {
    try {
      this.log('getClusters', params);
      
      const cacheKey = `clusters_${JSON.stringify(params)}`;
      const cached = this.getCached<GeospatialCluster[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params);
      const response = await api.get<GeospatialCluster[]>(`${this.endpoint}/clusters/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 10 minutes
      this.setCached(cacheKey, data, 10 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get heatmap data
   */
  async getHeatmapData(params: GeospatialFilters = {}): Promise<HeatmapData[]> {
    try {
      this.log('getHeatmapData', params);
      
      const cacheKey = `heatmap_${JSON.stringify(params)}`;
      const cached = this.getCached<HeatmapData[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params);
      const response = await api.get<HeatmapData[]>(`${this.endpoint}/heatmap/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 15 minutes
      this.setCached(cacheKey, data, 15 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get geographic analytics
   */
  async getGeoAnalytics(params: {
    region_type?: 'city' | 'district' | 'ward';
    start_date?: string;
    end_date?: string;
  } = {}): Promise<LocationAnalytics> {
    try {
      this.log('getGeoAnalytics', params);
      
      const cacheKey = `geo_analytics_${JSON.stringify(params)}`;
      const cached = this.getCached<LocationAnalytics>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params);
      const response = await api.get<LocationAnalytics>(`${this.endpoint}/analytics/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 20 minutes
      this.setCached(cacheKey, data, 20 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get complaints near a specific location
   */
  async getNearbyComplaints(
    coordinates: Coordinates,
    radiusMeters: number = 5000,
    filters: Partial<GeospatialFilters> = {}
  ): Promise<PaginatedResponse<GeospatialComplaint>> {
    try {
      this.log('getNearbyComplaints', { coordinates, radiusMeters, filters });
      
      const params = {
        latitude: coordinates.latitude,
        longitude: coordinates.longitude,
        radius: radiusMeters,
        ...filters,
      };
      
      const cacheKey = `nearby_complaints_${JSON.stringify(params)}`;
      const cached = this.getCached<PaginatedResponse<GeospatialComplaint>>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params);
      const response = await api.get<PaginatedResponse<GeospatialComplaint>>(
        `${this.endpoint}/nearby/${queryString}`
      );
      const data = this.transformPaginatedResponse(response);
      
      // Cache for 5 minutes
      this.setCached(cacheKey, data, 5 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Geocode an address to coordinates
   */
  async geocodeAddress(address: string): Promise<{
    coordinates: Coordinates;
    formatted_address: string;
    accuracy: 'high' | 'medium' | 'low';
    components: {
      street?: string;
      city?: string;
      state?: string;
      postal_code?: string;
      country?: string;
    };
  }> {
    try {
      this.log('geocodeAddress', { address });
      
      if (!address.trim()) {
        throw new ServiceError('Address cannot be empty');
      }

      const cacheKey = `geocode_${address.trim().toLowerCase()}`;
      const cached = this.getCached<any>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.post(`${this.endpoint}/geocode/`, {
        address: address.trim(),
      });
      const data = this.transformResponse(response);
      
      // Cache for 24 hours (addresses don't change)
      this.setCached(cacheKey, data, 24 * 60 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Reverse geocode coordinates to address
   */
  async reverseGeocode(coordinates: Coordinates): Promise<{
    address: string;
    formatted_address: string;
    components: {
      street?: string;
      city?: string;
      state?: string;
      postal_code?: string;
      country?: string;
    };
    accuracy: 'high' | 'medium' | 'low';
  }> {
    try {
      this.log('reverseGeocode', coordinates);
      
      const cacheKey = `reverse_geocode_${coordinates.latitude}_${coordinates.longitude}`;
      const cached = this.getCached<any>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.post(`${this.endpoint}/reverse-geocode/`, coordinates);
      const data = this.transformResponse(response);
      
      // Cache for 24 hours
      this.setCached(cacheKey, data, 24 * 60 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get geofence areas
   */
  async getGeofences(): Promise<GeofenceArea[]> {
    try {
      this.log('getGeofences');
      
      const cacheKey = 'geofences';
      const cached = this.getCached<GeofenceArea[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const response = await api.get<GeofenceArea[]>(`${this.endpoint}/geofences/`);
      const data = this.transformResponse(response);
      
      // Cache for 30 minutes
      this.setCached(cacheKey, data, 30 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Create a geofence area
   */
  async createGeofence(geofence: Omit<GeofenceArea, 'id' | 'created_at' | 'updated_at'>): Promise<GeofenceArea> {
    try {
      this.log('createGeofence', geofence);
      
      // Validate required fields
      this.validateRequest(geofence, ['name', 'type']);
      
      if (geofence.type === 'circle' && (!geofence.center || !geofence.radius)) {
        throw new ServiceError('Circle geofence requires center and radius');
      }
      
      if (geofence.type === 'polygon' && (!geofence.boundaries || geofence.boundaries.length < 3)) {
        throw new ServiceError('Polygon geofence requires at least 3 boundary points');
      }

      const response = await api.post<GeofenceArea>(`${this.endpoint}/geofences/`, geofence);
      const newGeofence = this.transformResponse(response);
      
      // Clear geofences cache
      this.clearCache('geofences');
      
      return newGeofence;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Export geospatial data
   */
  async exportGeospatialData(
    dataType: 'complaints' | 'heatmap' | 'clusters' | 'analytics',
    format: 'geojson' | 'csv' | 'kml',
    filters: GeospatialFilters = {}
  ): Promise<Blob> {
    try {
      this.log('exportGeospatialData', { dataType, format, filters });
      
      const params = {
        type: dataType,
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
   * Get spatial complaint density
   */
  async getComplaintDensity(params: {
    bounds?: BoundingBox;
    grid_size?: number;
    time_range?: string;
  } = {}): Promise<Array<{
    grid_cell: {
      north: number;
      south: number;
      east: number;
      west: number;
    };
    complaint_count: number;
    density_score: number;
    dominant_category?: string;
  }>> {
    try {
      this.log('getComplaintDensity', params);
      
      const cacheKey = `complaint_density_${JSON.stringify(params)}`;
      const cached = this.getCached<any[]>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params);
      const response = await api.get(`${this.endpoint}/density/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 15 minutes
      this.setCached(cacheKey, data, 15 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }

  /**
   * Get spatial analysis insights
   */
  async getSpatialInsights(params: {
    analysis_type?: 'hotspot' | 'clustering' | 'trend' | 'distribution';
    time_period?: 'week' | 'month' | 'quarter' | 'year';
    category_filter?: string[];
  } = {}): Promise<{
    insights: Array<{
      type: string;
      title: string;
      description: string;
      confidence: number;
      location?: Coordinates;
      affected_area?: BoundingBox;
      recommendations: string[];
    }>;
    summary: {
      total_hotspots: number;
      high_risk_areas: number;
      trend_direction: 'increasing' | 'decreasing' | 'stable';
      spatial_distribution: 'clustered' | 'scattered' | 'uniform';
    };
  }> {
    try {
      this.log('getSpatialInsights', params);
      
      const cacheKey = `spatial_insights_${JSON.stringify(params)}`;
      const cached = this.getCached<any>(cacheKey);
      if (cached) {
        return cached;
      }

      const queryString = this.buildQueryString(params);
      const response = await api.get(`${this.endpoint}/insights/${queryString}`);
      const data = this.transformResponse(response);
      
      // Cache for 30 minutes
      this.setCached(cacheKey, data, 30 * 60 * 1000);
      
      return data;
    } catch (error) {
      this.handleError(error as any);
    }
  }
}

// Export singleton instance
export const geospatialService = new GeospatialService();
export default geospatialService;