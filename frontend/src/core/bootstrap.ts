/**
 * Application Bootstrap and Service Registration
 * Sets up dependency injection container and initializes all services
 */

import { container } from '@/core/container';
import { 
  CoreServiceFactory 
} from '@/core/services';
import {
  AuthRepository,
  ComplaintRepository,
  AnalyticsRepository,
  ChatbotRepository,
  NotificationRepository
} from '@/repositories';

/**
 * Initialize and register all application services
 */
export function initializeServices(): void {
  // Register core infrastructure services
  container.registerFactory('logger', () => CoreServiceFactory.createLogger());
  container.registerFactory('httpClient', () => CoreServiceFactory.createHttpClient());
  container.registerFactory('storage', () => CoreServiceFactory.createStorageService());
  container.registerFactory('cache', () => CoreServiceFactory.createCacheService());
  container.registerFactory('validation', () => CoreServiceFactory.createValidationService());
  container.registerFactory('errorHandler', () => CoreServiceFactory.createErrorHandlingService());

  // Register business repositories
  container.registerFactory('authRepository', () => new AuthRepository());
  container.registerFactory('complaintRepository', () => new ComplaintRepository());
  container.registerFactory('analyticsRepository', () => new AnalyticsRepository());
  container.registerFactory('chatbotRepository', () => new ChatbotRepository());
  container.registerFactory('notificationRepository', () => new NotificationRepository());

  console.log('✅ All services initialized successfully');
}

/**
 * Cleanup services on application shutdown
 */
export function cleanupServices(): void {
  const cache = container.resolve('cache');
  cache.clear();
  
  container.clear();
  console.log('🧹 Services cleaned up');
}

/**
 * Health check for all critical services
 */
export async function performHealthCheck(): Promise<boolean> {
  try {
    const logger = container.resolve('logger');
    const httpClient = container.resolve('httpClient');
    
    logger.info('Performing health check...');

    // Test HTTP client connectivity
    try {
      await httpClient.get('/health/');
      logger.info('✅ Backend connectivity OK');
    } catch (error) {
      logger.warn('⚠️ Backend connectivity issue:', error);
      // Don't fail health check for backend issues in development
      if (import.meta.env.PROD) {
        return false;
      }
    }

    // Test storage access
    try {
      const storage = container.resolve('storage');
      storage.setItem('health_check', 'test');
      const retrieved = storage.getItem('health_check');
      storage.removeItem('health_check');
      
      if (retrieved === 'test') {
        logger.info('✅ Storage access OK');
      } else {
        logger.error('❌ Storage access failed');
        return false;
      }
    } catch (error) {
      logger.error('❌ Storage access error:', error as Error);
      return false;
    }

    logger.info('✅ Health check completed successfully');
    return true;
  } catch (error) {
    console.error('❌ Health check failed:', error);
    return false;
  }
}

/**
 * Get service status for debugging
 */
export function getServiceStatus(): Record<string, boolean> {
  const registeredServices = container.getKeys();
  const status: Record<string, boolean> = {};

  registeredServices.forEach(key => {
    try {
      container.resolve(key);
      status[key] = true;
    } catch (error) {
      status[key] = false;
    }
  });

  return status;
}

// Export for use in main.tsx
export { container };
export default { 
  initializeServices, 
  cleanupServices, 
  performHealthCheck, 
  getServiceStatus 
};