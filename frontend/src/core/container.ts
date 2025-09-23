/**
 * Dependency Injection Container
 * Implements IoC pattern for clean architecture
 */

import React from 'react';
import { 
  ILogger, 
  IHttpClient, 
  IStorageService, 
  ICacheService,
  IValidationService,
  IErrorHandlingService,
  IAuthRepository,
  IComplaintRepository,
  IAnalyticsRepository,
  IChatbotRepository,
  INotificationRepository
} from '@/types/core';

export interface ServiceContainer {
  // Core services
  logger: ILogger;
  httpClient: IHttpClient;
  storage: IStorageService;
  cache: ICacheService;
  validation: IValidationService;
  errorHandler: IErrorHandlingService;
  
  // Business repositories
  authRepository: IAuthRepository;
  complaintRepository: IComplaintRepository;
  analyticsRepository: IAnalyticsRepository;
  chatbotRepository: IChatbotRepository;
  notificationRepository: INotificationRepository;
}

export type ServiceKey = keyof ServiceContainer;

/**
 * Simple IoC container implementation
 */
class Container {
  private services = new Map<ServiceKey, any>();
  private factories = new Map<ServiceKey, () => any>();
  private singletons = new Set<ServiceKey>();

  /**
   * Register a service instance
   */
  register<T extends ServiceKey>(key: T, instance: ServiceContainer[T]): void {
    this.services.set(key, instance);
  }

  /**
   * Register a service factory
   */
  registerFactory<T extends ServiceKey>(
    key: T, 
    factory: () => ServiceContainer[T], 
    singleton = true
  ): void {
    this.factories.set(key, factory);
    if (singleton) {
      this.singletons.add(key);
    }
  }

  /**
   * Resolve a service
   */
  resolve<T extends ServiceKey>(key: T): ServiceContainer[T] {
    // Check if instance already exists
    if (this.services.has(key)) {
      return this.services.get(key);
    }

    // Check if factory exists
    if (this.factories.has(key)) {
      const factory = this.factories.get(key)!;
      const instance = factory();
      
      // Cache singleton instances
      if (this.singletons.has(key)) {
        this.services.set(key, instance);
      }
      
      return instance;
    }

    throw new Error(`Service '${key}' not registered`);
  }

  /**
   * Check if service is registered
   */
  has(key: ServiceKey): boolean {
    return this.services.has(key) || this.factories.has(key);
  }

  /**
   * Clear all services
   */
  clear(): void {
    this.services.clear();
    this.factories.clear();
    this.singletons.clear();
  }

  /**
   * Get all registered service keys
   */
  getKeys(): ServiceKey[] {
    const serviceKeys = Array.from(this.services.keys());
    const factoryKeys = Array.from(this.factories.keys());
    return [...new Set([...serviceKeys, ...factoryKeys])];
  }
}

// Global container instance
export const container = new Container();

/**
 * React hook for dependency injection
 */
export function useService<T extends ServiceKey>(key: T): ServiceContainer[T] {
  return container.resolve(key);
}

/**
 * Higher-order component for dependency injection
 */
export function withServices<P extends object>(
  serviceKeys: ServiceKey[]
) {
  return function <T extends React.ComponentType<P & Record<string, any>>>(
    Component: T
  ): React.ComponentType<P> {
    return function ServicesInjectedComponent(props: P) {
      const services: Record<string, any> = {};
      
      serviceKeys.forEach(key => {
        services[key] = container.resolve(key);
      });

      return React.createElement(Component, { ...props, ...services } as P & Record<string, any>);
    };
  };
}

/**
 * Service locator pattern for components that can't use hooks
 */
export class ServiceLocator {
  static resolve<T extends ServiceKey>(key: T): ServiceContainer[T] {
    return container.resolve(key);
  }

  static has(key: ServiceKey): boolean {
    return container.has(key);
  }
}

/**
 * Base class with dependency injection support
 */
export abstract class InjectableService {
  protected getService<T extends ServiceKey>(key: T): ServiceContainer[T] {
    return container.resolve(key);
  }
}

export default container;