import { apiService } from './api';
import {
  GeospatialCluster,
  HeatmapData,
} from '@/types';

export const geospatialService = {
  // Get complaint clusters
  getClusters: async (params?: {
    zoom_level?: number;
    bounds?: {
      north: number;
      south: number;
      east: number;
      west: number;
    };
    cluster_type?: string;
    min_complaints?: number;
  }): Promise<GeospatialCluster[]> => {
    return apiService.get<GeospatialCluster[]>('/geospatial/clusters/', params);
  },

  // Get heatmap data
  getHeatmapData: async (params?: {
    bounds?: {
      north: number;
      south: number;
      east: number;
      west: number;
    };
    time_range?: string;
    complaint_type?: string;
  }): Promise<HeatmapData[]> => {
    return apiService.get<HeatmapData[]>('/geospatial/heatmap/', params);
  },

  // Get geographic analytics
  getGeoAnalytics: async (params?: {
    region_type?: 'city' | 'district' | 'ward';
    start_date?: string;
    end_date?: string;
  }): Promise<{
    hotspots: Array<{
      id: number;
      name: string;
      latitude: number;
      longitude: number;
      complaint_count: number;
      severity_score: number;
      trend: 'increasing' | 'stable' | 'decreasing';
    }>;
    regional_stats: Array<{
      region_name: string;
      total_complaints: number;
      resolved_rate: number;
      avg_response_time: number;
    }>;
    coverage_analysis: {
      total_area_covered: number;
      service_gaps: Array<{
        latitude: number;
        longitude: number;
        gap_score: number;
      }>;
    };
  }> => {
    return apiService.get('/geospatial/analytics/', params);
  },

  // Get route optimization
  getOptimizedRoute: async (data: {
    start_location: {
      latitude: number;
      longitude: number;
    };
    waypoints: Array<{
      latitude: number;
      longitude: number;
      priority?: number;
      complaint_id?: number;
    }>;
    vehicle_type?: 'car' | 'bike' | 'walking';
    optimize_for?: 'time' | 'distance' | 'priority';
  }): Promise<{
    optimized_route: Array<{
      latitude: number;
      longitude: number;
      order: number;
      estimated_arrival: string;
    }>;
    total_distance: number;
    total_time: number;
    route_geometry: string; // GeoJSON string
  }> => {
    return apiService.post('/geospatial/route-optimization/', data);
  },

  // Get location intelligence
  getLocationIntelligence: async (
    latitude: number,
    longitude: number,
    radius: number = 1000
  ): Promise<{
    location_info: {
      address: string;
      area_type: string;
      population_density: number;
      socioeconomic_index: number;
    };
    nearby_services: Array<{
      type: string;
      name: string;
      distance: number;
      latitude: number;
      longitude: number;
    }>;
    historical_complaints: {
      total_count: number;
      by_category: Array<{
        category: string;
        count: number;
      }>;
      trend_analysis: {
        direction: 'increasing' | 'stable' | 'decreasing';
        change_percentage: number;
      };
    };
    risk_assessment: {
      risk_level: 'low' | 'medium' | 'high';
      risk_factors: string[];
      recommendations: string[];
    };
  }> => {
    return apiService.get('/geospatial/location-intelligence/', {
      lat: latitude,
      lon: longitude,
      radius,
    });
  },

  // Geocode address
  geocodeAddress: async (address: string): Promise<{
    latitude: number;
    longitude: number;
    formatted_address: string;
    components: {
      street_number?: string;
      route?: string;
      locality?: string;
      administrative_area?: string;
      postal_code?: string;
      country?: string;
    };
    confidence: number;
  }> => {
    return apiService.get('/geospatial/geocode/', { address });
  },

  // Reverse geocode coordinates
  reverseGeocode: async (
    latitude: number,
    longitude: number
  ): Promise<{
    formatted_address: string;
    components: {
      street_number?: string;
      route?: string;
      locality?: string;
      administrative_area?: string;
      postal_code?: string;
      country?: string;
    };
  }> => {
    return apiService.get('/geospatial/reverse-geocode/', {
      lat: latitude,
      lon: longitude,
    });
  },

  // Get nearby points of interest
  getNearbyPOI: async (
    latitude: number,
    longitude: number,
    radius: number = 1000,
    types?: string[]
  ): Promise<Array<{
    id: string;
    name: string;
    type: string;
    latitude: number;
    longitude: number;
    distance: number;
    rating?: number;
    address?: string;
  }>> => {
    return apiService.get('/geospatial/nearby-poi/', {
      lat: latitude,
      lon: longitude,
      radius,
      types: types?.join(','),
    });
  },

  // Get administrative boundaries
  getAdministrativeBoundaries: async (params?: {
    level?: 'country' | 'state' | 'district' | 'city' | 'ward';
    bounds?: {
      north: number;
      south: number;
      east: number;
      west: number;
    };
  }): Promise<Array<{
    id: string;
    name: string;
    level: string;
    geometry: string; // GeoJSON string
    properties: Record<string, any>;
  }>> => {
    return apiService.get('/geospatial/boundaries/', params);
  },

  // Get complaint density by area
  getComplaintDensity: async (params?: {
    grid_size?: number;
    bounds?: {
      north: number;
      south: number;
      east: number;
      west: number;
    };
    start_date?: string;
    end_date?: string;
  }): Promise<Array<{
    grid_id: string;
    center_latitude: number;
    center_longitude: number;
    complaint_count: number;
    density_score: number;
    geometry: string; // GeoJSON string
  }>> => {
    return apiService.get('/geospatial/density/', params);
  },

  // Create custom geographic area
  createCustomArea: async (data: {
    name: string;
    geometry: string; // GeoJSON string
    area_type: string;
    properties?: Record<string, any>;
  }): Promise<{
    id: number;
    message: string;
  }> => {
    return apiService.post('/geospatial/custom-areas/', data);
  },

  // Get complaints within custom area
  getComplaintsInArea: async (
    area_id: number,
    params?: {
      start_date?: string;
      end_date?: string;
      status?: string[];
    }
  ): Promise<{
    total_complaints: number;
    complaints: Array<{
      id: number;
      title: string;
      status: string;
      latitude: number;
      longitude: number;
      created_at: string;
    }>;
    statistics: {
      by_status: Array<{ status: string; count: number }>;
      by_category: Array<{ category: string; count: number }>;
      trend_analysis: {
        current_period: number;
        previous_period: number;
        change_percentage: number;
      };
    };
  }> => {
    return apiService.get(`/geospatial/custom-areas/${area_id}/complaints/`, params);
  },
};
