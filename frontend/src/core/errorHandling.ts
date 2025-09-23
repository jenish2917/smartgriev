/**
 * Global Error Handling and Logging
 * Centralized error handling, logging, and monitoring
 */

import { ILogger } from '@/types/core';
import { notification, message } from 'antd';

export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum ErrorCategory {
  NETWORK = 'network',
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  VALIDATION = 'validation',
  BUSINESS_LOGIC = 'business_logic',
  SYSTEM = 'system',
  USER_INPUT = 'user_input'
}

export interface ErrorContext {
  userId?: string;
  sessionId?: string;
  userAgent?: string;
  url?: string;
  timestamp: string;
  stackTrace?: string;
  additionalData?: Record<string, any>;
}

export interface AppError {
  id: string;
  message: string;
  code?: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  context: ErrorContext;
  isRetryable: boolean;
  userMessage?: string;
}

/**
 * Enhanced Logger with error tracking
 */
export class ApplicationLogger implements ILogger {
  private isDevelopment = import.meta.env.DEV;
  private errorBuffer: AppError[] = [];
  private maxBufferSize = 100;

  debug(message: string, ...args: any[]): void {
    if (this.isDevelopment) {
      console.debug(`[DEBUG] ${this.formatMessage(message)}`, ...args);
    }
  }

  info(message: string, ...args: any[]): void {
    console.info(`[INFO] ${this.formatMessage(message)}`, ...args);
    this.logToRemote('info', message, args);
  }

  warn(message: string, ...args: any[]): void {
    console.warn(`[WARN] ${this.formatMessage(message)}`, ...args);
    this.logToRemote('warn', message, args);
  }

  error(message: string, error?: Error, ...args: any[]): void {
    console.error(`[ERROR] ${this.formatMessage(message)}`, error, ...args);
    
    const appError = this.createAppError(message, error, args);
    this.addToBuffer(appError);
    this.logToRemote('error', message, { error, args });
    
    // Send critical errors immediately
    if (appError.severity === ErrorSeverity.CRITICAL) {
      this.sendErrorsToRemote([appError]);
    }
  }

  private formatMessage(message: string): string {
    const timestamp = new Date().toISOString();
    return `${timestamp} - ${message}`;
  }

  private createAppError(message: string, error?: Error, additionalData?: any[]): AppError {
    return {
      id: this.generateErrorId(),
      message,
      code: (error as any)?.code,
      category: this.categorizeError(error, message),
      severity: this.determineSeverity(error, message),
      context: this.createErrorContext(error),
      isRetryable: this.isRetryableError(error),
      userMessage: this.generateUserMessage(error, message),
    };
  }

  private generateErrorId(): string {
    return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private categorizeError(error?: Error, message?: string): ErrorCategory {
    if (!error) return ErrorCategory.SYSTEM;
    
    const errorMessage = error.message.toLowerCase();
    const code = (error as any).code;
    const status = (error as any).status;

    if (status === 401 || errorMessage.includes('unauthorized')) {
      return ErrorCategory.AUTHENTICATION;
    }
    
    if (status === 403 || errorMessage.includes('forbidden')) {
      return ErrorCategory.AUTHORIZATION;
    }
    
    if (status >= 400 && status < 500 || errorMessage.includes('validation')) {
      return ErrorCategory.VALIDATION;
    }
    
    if (code === 'NETWORK_ERROR' || errorMessage.includes('network')) {
      return ErrorCategory.NETWORK;
    }
    
    if (message?.toLowerCase().includes('business') || message?.toLowerCase().includes('logic')) {
      return ErrorCategory.BUSINESS_LOGIC;
    }
    
    return ErrorCategory.SYSTEM;
  }

  private determineSeverity(error?: Error, message?: string): ErrorSeverity {
    if (!error) return ErrorSeverity.LOW;
    
    const status = (error as any).status;
    const errorMessage = error.message.toLowerCase();

    if (errorMessage.includes('critical') || errorMessage.includes('fatal')) {
      return ErrorSeverity.CRITICAL;
    }
    
    if (status >= 500 || errorMessage.includes('server error')) {
      return ErrorSeverity.HIGH;
    }
    
    if (status === 401 || status === 403 || errorMessage.includes('auth')) {
      return ErrorSeverity.MEDIUM;
    }
    
    return ErrorSeverity.LOW;
  }

  private createErrorContext(error?: Error): ErrorContext {
    return {
      userId: this.getCurrentUserId(),
      sessionId: this.getSessionId(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      stackTrace: error?.stack,
      additionalData: {
        viewport: `${window.innerWidth}x${window.innerHeight}`,
        language: navigator.language,
        platform: navigator.platform,
      }
    };
  }

  private isRetryableError(error?: Error): boolean {
    if (!error) return false;
    
    const status = (error as any).status;
    const code = (error as any).code;
    
    // Network errors and 5xx errors are usually retryable
    return code === 'NETWORK_ERROR' || (status >= 500 && status < 600);
  }

  private generateUserMessage(error?: Error, originalMessage?: string): string {
    if (!error) return originalMessage || 'An unexpected error occurred';
    
    const category = this.categorizeError(error, originalMessage);
    
    const userMessages = {
      [ErrorCategory.NETWORK]: 'Please check your internet connection and try again.',
      [ErrorCategory.AUTHENTICATION]: 'Please log in again to continue.',
      [ErrorCategory.AUTHORIZATION]: 'You don\'t have permission to perform this action.',
      [ErrorCategory.VALIDATION]: 'Please check your input and try again.',
      [ErrorCategory.BUSINESS_LOGIC]: 'Unable to complete the operation. Please try again.',
      [ErrorCategory.SYSTEM]: 'A system error occurred. Our team has been notified.',
      [ErrorCategory.USER_INPUT]: 'Please check your input and try again.',
    };
    
    return userMessages[category] || 'An unexpected error occurred. Please try again.';
  }

  private getCurrentUserId(): string | undefined {
    // This would integrate with your auth system
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      return user.id;
    } catch {
      return undefined;
    }
  }

  private getSessionId(): string {
    let sessionId = sessionStorage.getItem('session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('session_id', sessionId);
    }
    return sessionId;
  }

  private addToBuffer(error: AppError): void {
    this.errorBuffer.push(error);
    
    if (this.errorBuffer.length > this.maxBufferSize) {
      this.errorBuffer.shift(); // Remove oldest error
    }
    
    // Send buffer periodically
    if (this.errorBuffer.length >= 10) {
      this.flushErrorBuffer();
    }
  }

  private flushErrorBuffer(): void {
    if (this.errorBuffer.length === 0) return;
    
    const errorsToSend = [...this.errorBuffer];
    this.errorBuffer = [];
    
    this.sendErrorsToRemote(errorsToSend);
  }

  private async sendErrorsToRemote(errors: AppError[]): Promise<void> {
    try {
      // In production, send to error monitoring service
      if (import.meta.env.PROD) {
        await fetch('/api/errors/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ errors }),
        });
      }
    } catch (error) {
      console.warn('Failed to send errors to remote service:', error);
    }
  }

  private async logToRemote(level: string, message: string, data?: any): Promise<void> {
    // Send logs to remote service in production
    if (import.meta.env.PROD) {
      try {
        await fetch('/api/logs/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            level,
            message,
            data,
            timestamp: new Date().toISOString(),
            context: this.createErrorContext(),
          }),
        });
      } catch (error) {
        // Silently fail - don't create infinite loops
      }
    }
  }

  // Public methods for manual error reporting
  public reportError(error: AppError): void {
    this.addToBuffer(error);
  }

  public getErrorBuffer(): AppError[] {
    return [...this.errorBuffer];
  }

  public clearErrorBuffer(): void {
    this.errorBuffer = [];
  }
}

/**
 * Global Error Handler for React
 */
export class GlobalErrorHandler {
  private logger: ApplicationLogger;
  private retryAttempts = new Map<string, number>();
  private maxRetries = 3;

  constructor(logger: ApplicationLogger) {
    this.logger = logger;
    this.setupGlobalHandlers();
  }

  private setupGlobalHandlers(): void {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError(event.reason, 'Unhandled Promise Rejection');
      event.preventDefault();
    });

    // Handle global JavaScript errors
    window.addEventListener('error', (event) => {
      this.handleError(event.error, 'Global JavaScript Error');
    });

    // Handle React error boundary errors
    window.addEventListener('react-error', (event: any) => {
      this.handleError(event.detail.error, 'React Error Boundary');
    });
  }

  public handleError(error: any, context?: string): AppError {
    const appError = this.createAppError(error, context);
    this.logger.reportError(appError);
    
    // Show user notification based on severity
    this.showUserNotification(appError);
    
    return appError;
  }

  public handleAsyncError<T>(
    operation: () => Promise<T>,
    options?: {
      retryable?: boolean;
      userMessage?: string;
      silent?: boolean;
    }
  ): Promise<T> {
    const operationId = this.generateOperationId();
    
    return this.executeWithRetry(operation, operationId, options);
  }

  private async executeWithRetry<T>(
    operation: () => Promise<T>,
    operationId: string,
    options?: {
      retryable?: boolean;
      userMessage?: string;
      silent?: boolean;
    }
  ): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      const appError = this.handleError(error, 'Async Operation');
      
      // Check if we should retry
      if (options?.retryable !== false && appError.isRetryable) {
        const attempts = this.retryAttempts.get(operationId) || 0;
        
        if (attempts < this.maxRetries) {
          this.retryAttempts.set(operationId, attempts + 1);
          
          // Exponential backoff
          const delay = Math.pow(2, attempts) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
          
          this.logger.info(`Retrying operation ${operationId}, attempt ${attempts + 1}`);
          return this.executeWithRetry(operation, operationId, options);
        } else {
          this.retryAttempts.delete(operationId);
        }
      }
      
      throw error;
    }
  }

  private createAppError(error: any, context?: string): AppError {
    const message = error?.message || 'Unknown error occurred';
    const fullMessage = context ? `${context}: ${message}` : message;
    
    return {
      id: this.generateErrorId(),
      message: fullMessage,
      code: error?.code,
      category: this.categorizeError(error),
      severity: this.determineSeverity(error),
      context: this.createErrorContext(error, context),
      isRetryable: this.isRetryableError(error),
      userMessage: this.generateUserMessage(error),
    };
  }

  private categorizeError(error: any): ErrorCategory {
    // Similar logic as in ApplicationLogger
    if (!error) return ErrorCategory.SYSTEM;
    
    const status = error.status;
    const code = error.code;
    const message = error.message?.toLowerCase() || '';

    if (status === 401) return ErrorCategory.AUTHENTICATION;
    if (status === 403) return ErrorCategory.AUTHORIZATION;
    if (status >= 400 && status < 500) return ErrorCategory.VALIDATION;
    if (code === 'NETWORK_ERROR') return ErrorCategory.NETWORK;
    
    return ErrorCategory.SYSTEM;
  }

  private determineSeverity(error: any): ErrorSeverity {
    const status = error?.status;
    const message = error?.message?.toLowerCase() || '';

    if (message.includes('critical') || status >= 500) {
      return ErrorSeverity.CRITICAL;
    }
    if (status === 401 || status === 403) {
      return ErrorSeverity.MEDIUM;
    }
    return ErrorSeverity.LOW;
  }

  private createErrorContext(error: any, context?: string): ErrorContext {
    return {
      userId: this.getCurrentUserId(),
      sessionId: this.getSessionId(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      stackTrace: error?.stack,
      additionalData: {
        context,
        errorType: error?.constructor?.name,
        viewport: `${window.innerWidth}x${window.innerHeight}`,
      }
    };
  }

  private isRetryableError(error: any): boolean {
    const status = error?.status;
    const code = error?.code;
    
    return code === 'NETWORK_ERROR' || (status >= 500 && status < 600);
  }

  private generateUserMessage(error: any): string {
    const category = this.categorizeError(error);
    
    const messages = {
      [ErrorCategory.NETWORK]: 'Connection issue detected. Please check your internet connection.',
      [ErrorCategory.AUTHENTICATION]: 'Please log in again to continue.',
      [ErrorCategory.AUTHORIZATION]: 'Access denied. You may not have permission for this action.',
      [ErrorCategory.VALIDATION]: 'Please check your input and try again.',
      [ErrorCategory.BUSINESS_LOGIC]: 'Operation failed. Please try again.',
      [ErrorCategory.SYSTEM]: 'A system error occurred. Our team has been notified.',
      [ErrorCategory.USER_INPUT]: 'Invalid input detected. Please correct and try again.',
    };
    
    return messages[category] || 'An unexpected error occurred.';
  }

  private showUserNotification(error: AppError): void {
    const userMessage = error.userMessage || error.message;
    
    switch (error.severity) {
      case ErrorSeverity.CRITICAL:
        notification.error({
          message: 'Critical Error',
          description: userMessage,
          duration: 0, // Don't auto-close
          key: error.id,
        });
        break;
        
      case ErrorSeverity.HIGH:
        notification.error({
          message: 'Error',
          description: userMessage,
          duration: 6,
          key: error.id,
        });
        break;
        
      case ErrorSeverity.MEDIUM:
        notification.warning({
          message: 'Warning',
          description: userMessage,
          duration: 4,
          key: error.id,
        });
        break;
        
      case ErrorSeverity.LOW:
        message.warning(userMessage);
        break;
    }
  }

  private generateErrorId(): string {
    return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateOperationId(): string {
    return `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getCurrentUserId(): string | undefined {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      return user.id;
    } catch {
      return undefined;
    }
  }

  private getSessionId(): string {
    let sessionId = sessionStorage.getItem('session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('session_id', sessionId);
    }
    return sessionId;
  }
}

// Global instance
export const globalErrorHandler = new GlobalErrorHandler(new ApplicationLogger());

// Utility functions for components
export const handleAsyncError = <T>(
  operation: () => Promise<T>,
  options?: {
    retryable?: boolean;
    userMessage?: string;
    silent?: boolean;
  }
): Promise<T> => {
  return globalErrorHandler.handleAsyncError(operation, options);
};

export const reportError = (error: any, context?: string): void => {
  globalErrorHandler.handleError(error, context);
};

export default {
  ApplicationLogger,
  GlobalErrorHandler,
  globalErrorHandler,
  handleAsyncError,
  reportError,
};