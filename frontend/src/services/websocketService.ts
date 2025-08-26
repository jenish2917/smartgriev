// @ts-ignore - socket.io-client type resolution issues
import { io } from 'socket.io-client';
import {
  WebSocketMessage,
  DashboardUpdate,
  MetricUpdate,
  AlertNotification,
  ComplaintUpdate,
} from '@/types';

class WebSocketService {
  private socket: any | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 5000;
  private isConnecting = false;

  // Event listeners
  private eventListeners: Map<string, Array<(data: any) => void>> = new Map();

  constructor() {
    this.initializeConnection();
  }

  private initializeConnection(): void {
    if (this.isConnecting || this.socket?.connected) {
      return;
    }

    this.isConnecting = true;

    try {
      // Initialize Socket.IO connection
      this.socket = io('ws://localhost:8000', {
        transports: ['websocket'],
        upgrade: true,
        autoConnect: true,
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectInterval,
        timeout: 20000,
        forceNew: true,
      });

      this.setupEventHandlers();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.isConnecting = false;
    }
  }

  private setupEventHandlers(): void {
    if (!this.socket) return;

    // Connection events
    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.emit('connection', { status: 'connected' });
    });

    this.socket.on('disconnect', (reason: any) => {
      console.log('❌ WebSocket disconnected:', reason);
      this.emit('connection', { status: 'disconnected', reason });
    });

    this.socket.on('connect_error', (error: any) => {
      console.error('🔥 WebSocket connection error:', error);
      this.isConnecting = false;
      this.emit('connection', { status: 'error', error: error.message });
    });

    // Custom event handlers
    this.socket.on('dashboard_update', (data: DashboardUpdate) => {
      this.emit('dashboard_update', data);
    });

    this.socket.on('metric_update', (data: MetricUpdate) => {
      this.emit('metric_update', data);
    });

    this.socket.on('alert_notification', (data: AlertNotification) => {
      this.emit('alert_notification', data);
    });

    this.socket.on('complaint_update', (data: ComplaintUpdate) => {
      this.emit('complaint_update', data);
    });

    this.socket.on('notification', (data: any) => {
      this.emit('notification', data);
    });

    // Generic message handler
    this.socket.on('message', (message: WebSocketMessage) => {
      this.emit('message', message);
      
      // Also emit specific event type
      if (message.type) {
        this.emit(message.type, message.data);
      }
    });
  }

  // Connect to WebSocket
  connect(): void {
    if (this.socket?.connected) {
      return;
    }

    if (!this.socket) {
      this.initializeConnection();
    } else {
      this.socket.connect();
    }
  }

  // Disconnect from WebSocket
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.eventListeners.clear();
  }

  // Check connection status
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  // Send message to server
  send(type: string, data?: any): void {
    if (this.socket?.connected) {
      this.socket.emit(type, data);
    } else {
      console.warn('Cannot send message: WebSocket not connected');
    }
  }

  // Subscribe to dashboard updates
  subscribeToDashboard(): void {
    this.send('subscribe_dashboard');
  }

  // Subscribe to specific metrics
  subscribeToMetrics(metrics: string[]): void {
    this.send('subscribe_metrics', { metrics });
  }

  // Subscribe to notifications
  subscribeToNotifications(): void {
    this.send('subscribe_notifications');
  }

  // Subscribe to complaint updates
  subscribeToComplaints(complaint_ids?: number[]): void {
    this.send('subscribe_complaints', { complaint_ids });
  }

  // Request dashboard data update
  requestDashboardUpdate(): void {
    this.send('request_update', { type: 'dashboard' });
  }

  // Add event listener
  on<T = any>(event: string, callback: (data: T) => void): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  // Remove event listener
  off(event: string, callback?: (data: any) => void): void {
    if (!this.eventListeners.has(event)) {
      return;
    }

    if (callback) {
      const listeners = this.eventListeners.get(event)!;
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    } else {
      this.eventListeners.delete(event);
    }
  }

  // Emit event to all listeners
  private emit(event: string, data: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error);
        }
      });
    }
  }

  // Remove all listeners
  removeAllListeners(): void {
    this.eventListeners.clear();
  }

  // Get connection state
  getConnectionState(): {
    connected: boolean;
    reconnectAttempts: number;
    isConnecting: boolean;
  } {
    return {
      connected: this.isConnected(),
      reconnectAttempts: this.reconnectAttempts,
      isConnecting: this.isConnecting,
    };
  }
}

// Create singleton instance
const webSocketService = new WebSocketService();

// Hook for React components to use WebSocket
export const useWebSocket = () => {
  return {
    connect: () => webSocketService.connect(),
    disconnect: () => webSocketService.disconnect(),
    isConnected: () => webSocketService.isConnected(),
    send: (type: string, data?: any) => webSocketService.send(type, data),
    on: <T = any>(event: string, callback: (data: T) => void) => webSocketService.on(event, callback),
    off: (event: string, callback?: (data: any) => void) => webSocketService.off(event, callback),
    subscribeToDashboard: () => webSocketService.subscribeToDashboard(),
    subscribeToMetrics: (metrics: string[]) => webSocketService.subscribeToMetrics(metrics),
    subscribeToNotifications: () => webSocketService.subscribeToNotifications(),
    subscribeToComplaints: (complaint_ids?: number[]) => webSocketService.subscribeToComplaints(complaint_ids),
    requestDashboardUpdate: () => webSocketService.requestDashboardUpdate(),
    getConnectionState: () => webSocketService.getConnectionState(),
  };
};

export default webSocketService;
