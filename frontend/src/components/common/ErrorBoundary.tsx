/**
 * React Error Boundary Component
 * Catches and handles React component errors gracefully
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Result, Button, Typography, Card, Space, Alert } from 'antd';
import { BugOutlined, ReloadOutlined, HomeOutlined } from '@ant-design/icons';
import { globalErrorHandler } from '@/core/errorHandling';

const { Paragraph, Text } = Typography;

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  level?: 'page' | 'component' | 'critical';
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
}

/**
 * Enhanced Error Boundary with different fallback UIs based on error level
 */
export class ErrorBoundary extends Component<Props, State> {
  private retryCount = 0;
  private maxRetries = 3;

  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const errorId = globalErrorHandler.handleError(error, 'React Error Boundary').id;
    
    this.setState({
      errorInfo,
      errorId,
    });

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);

    // Log to console in development
    if (import.meta.env.DEV) {
      console.error('React Error Boundary caught an error:', error, errorInfo);
    }
  }

  private handleRetry = () => {
    if (this.retryCount < this.maxRetries) {
      this.retryCount++;
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: null,
      });
    } else {
      // Max retries reached, redirect to home or show contact support
      window.location.href = '/';
    }
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  private renderComponentLevelError = () => (
    <Alert
      message="Component Error"
      description="This section encountered an error and couldn't load properly."
      type="error"
      action={
        <Space>
          <Button size="small" onClick={this.handleRetry}>
            Retry
          </Button>
        </Space>
      }
      showIcon
    />
  );

  private renderPageLevelError = () => (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <Result
        status="error"
        title="Page Error"
        subTitle="Something went wrong while loading this page."
        extra={
          <Space>
            <Button type="primary" icon={<ReloadOutlined />} onClick={this.handleRetry}>
              Try Again
            </Button>
            <Button icon={<HomeOutlined />} onClick={this.handleGoHome}>
              Go Home
            </Button>
          </Space>
        }
      >
        <div className="desc">
          <Paragraph>
            <Text strong>What happened?</Text>
          </Paragraph>
          <Paragraph>
            The page encountered an unexpected error. This could be due to:
          </Paragraph>
          <Paragraph>
            <ul style={{ textAlign: 'left', display: 'inline-block' }}>
              <li>A temporary network issue</li>
              <li>Invalid data from the server</li>
              <li>A bug in the application</li>
            </ul>
          </Paragraph>
          {import.meta.env.DEV && this.state.error && (
            <Card size="small" style={{ textAlign: 'left', marginTop: 16 }}>
              <Typography.Title level={5}>Debug Information</Typography.Title>
              <Paragraph code copyable={{ text: this.state.error.message }}>
                {this.state.error.message}
              </Paragraph>
              {this.state.errorInfo?.componentStack && (
                <Paragraph>
                  <Text strong>Component Stack:</Text>
                  <pre style={{ fontSize: '12px', marginTop: 8 }}>
                    {this.state.errorInfo.componentStack}
                  </pre>
                </Paragraph>
              )}
            </Card>
          )}
        </div>
      </Result>
    </div>
  );

  private renderCriticalError = () => (
    <div style={{ 
      height: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: '#f5f5f5' 
    }}>
      <Card style={{ width: 600, textAlign: 'center' }}>
        <Result
          status="500"
          title="Critical Application Error"
          subTitle="The application has encountered a critical error and needs to restart."
          icon={<BugOutlined style={{ color: '#ff4d4f' }} />}
          extra={
            <Space direction="vertical">
              <Paragraph>
                We're sorry for the inconvenience. The error has been automatically 
                reported to our development team.
              </Paragraph>
              
              {this.state.errorId && (
                <Alert
                  message={`Error ID: ${this.state.errorId}`}
                  description="Please reference this ID when contacting support."
                  type="info"
                  showIcon
                />
              )}
              
              <Space>
                <Button type="primary" icon={<ReloadOutlined />} onClick={this.handleReload}>
                  Reload Application
                </Button>
                <Button onClick={this.handleGoHome}>
                  Go to Dashboard
                </Button>
              </Space>
              
              <Text type="secondary" style={{ fontSize: '12px' }}>
                If the problem persists, please contact support.
              </Text>
            </Space>
          }
        />
      </Card>
    </div>
  );

  render() {
    if (this.state.hasError) {
      // If custom fallback is provided, use it
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Choose appropriate error UI based on level
      switch (this.props.level) {
        case 'component':
          return this.renderComponentLevelError();
        case 'critical':
          return this.renderCriticalError();
        case 'page':
        default:
          return this.renderPageLevelError();
      }
    }

    return this.props.children;
  }
}

/**
 * HOC for wrapping components with error boundary
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) {
  return function ErrorBoundaryWrapper(props: P) {
    return (
      <ErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
}

/**
 * Hook for handling errors in functional components
 */
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);

  const handleError = React.useCallback((error: Error, context?: string) => {
    globalErrorHandler.handleError(error, context);
    setError(error);
  }, []);

  const clearError = React.useCallback(() => {
    setError(null);
  }, []);

  const retryOperation = React.useCallback(async function<T>(
    operation: () => Promise<T>,
    options?: {
      retryable?: boolean;
      userMessage?: string;
      silent?: boolean;
    }
  ): Promise<T | null> {
    try {
      clearError();
      return await globalErrorHandler.handleAsyncError(operation, options);
    } catch (error) {
      handleError(error as Error);
      return null;
    }
  }, [handleError, clearError]);

  return {
    error,
    handleError,
    clearError,
    retryOperation,
  };
}

/**
 * Component-level error boundary for specific sections
 */
export const ComponentErrorBoundary: React.FC<{ children: ReactNode; name?: string }> = ({ 
  children, 
  name 
}) => (
  <ErrorBoundary 
    level="component" 
    onError={(error, errorInfo) => {
      globalErrorHandler.handleError(error, `Component: ${name || 'Unknown'}`);
    }}
  >
    {children}
  </ErrorBoundary>
);

/**
 * Page-level error boundary for route components
 */
export const PageErrorBoundary: React.FC<{ children: ReactNode; pageName?: string }> = ({ 
  children, 
  pageName 
}) => (
  <ErrorBoundary 
    level="page" 
    onError={(error, errorInfo) => {
      globalErrorHandler.handleError(error, `Page: ${pageName || window.location.pathname}`);
    }}
  >
    {children}
  </ErrorBoundary>
);

/**
 * Critical error boundary for the entire app
 */
export const AppErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => (
  <ErrorBoundary 
    level="critical" 
    onError={(error, errorInfo) => {
      globalErrorHandler.handleError(error, 'Application Critical Error');
    }}
  >
    {children}
  </ErrorBoundary>
);

export default ErrorBoundary;