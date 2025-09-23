import React, { ReactNode, useState, useCallback } from 'react';
import { Spin, Alert, message } from 'antd';

/**
 * Base Component Props interface
 */
export interface BaseComponentProps {
  loading?: boolean;
  error?: string | null;
  className?: string;
  style?: React.CSSProperties;
  children?: ReactNode;
}

/**
 * Base Component Hook - provides common functionality
 */
export const useBaseComponent = () => {
  const [internalLoading, setInternalLoading] = useState(false);
  const [internalError, setInternalError] = useState<string | null>(null);

  const showLoading = useCallback(() => setInternalLoading(true), []);
  const hideLoading = useCallback(() => setInternalLoading(false), []);
  
  const handleError = useCallback((error: string, originalError?: Error) => {
    console.error('Component Error:', error, originalError);
    setInternalError(error);
    setInternalLoading(false);
    message.error(error);
  }, []);

  const clearError = useCallback(() => setInternalError(null), []);

  const executeAsync = useCallback(async (
    operation: () => Promise<any>,
    options: {
      showLoading?: boolean;
      errorMessage?: string;
      successMessage?: string;
    } = {}
  ): Promise<any> => {
    const { showLoading: shouldShowLoading = true, errorMessage, successMessage } = options;

    try {
      if (shouldShowLoading) showLoading();
      clearError();

      const result = await operation();

      if (successMessage) {
        message.success(successMessage);
      }

      return result;
    } catch (error: any) {
      const errorMsg = errorMessage || error.message || 'An error occurred';
      handleError(errorMsg, error);
      return null;
    } finally {
      if (shouldShowLoading) hideLoading();
    }
  }, [showLoading, hideLoading, clearError, handleError]);

  return {
    internalLoading,
    internalError,
    showLoading,
    hideLoading,
    handleError,
    clearError,
    executeAsync,
  };
};

/**
 * Base Component HOC with common error/loading handling
 */
export const withBaseComponent = <P extends BaseComponentProps>(
  WrappedComponent: React.ComponentType<P>
) => {
  return React.forwardRef<any, P>((props, ref) => {
    const { loading, error, className, style, children, ...restProps } = props;

    const renderLoading = () => (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );

    const renderError = () => {
      if (!error) return null;
      return (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      );
    };

    if (loading) {
      return (
        <div className={className} style={style}>
          {renderLoading()}
        </div>
      );
    }

    return (
      <div className={className} style={style}>
        {renderError()}
        <WrappedComponent {...(props as any)} ref={ref} />
      </div>
    );
  });
};

/**
 * Base Page Component with common layout patterns
 */
export interface BasePageProps extends BaseComponentProps {
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  breadcrumbs?: Array<{ title: string; path?: string }>;
}

export const BasePage: React.FC<BasePageProps> = ({
  title,
  subtitle,
  actions,
  breadcrumbs,
  loading,
  error,
  className,
  style,
  children,
}) => {
  const { internalLoading, internalError } = useBaseComponent();

  const isLoading = loading || internalLoading;
  const hasError = error || internalError;

  if (isLoading) {
    return (
      <div className={className} style={style}>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}>
          <Spin size="large" />
        </div>
      </div>
    );
  }

  return (
    <div className={className} style={style}>
      {hasError && (
        <Alert
          message="Error"
          description={hasError}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      {(title || subtitle || actions) && (
        <div className="page-header" style={{ marginBottom: 24 }}>
          {title && (
            <h2 style={{ margin: 0, fontSize: '24px', fontWeight: 600 }}>
              {title}
            </h2>
          )}
          {subtitle && (
            <p style={{ margin: '8px 0 0', color: '#666', fontSize: '14px' }}>
              {subtitle}
            </p>
          )}
          {actions && (
            <div style={{ marginTop: 16 }}>
              {actions}
            </div>
          )}
        </div>
      )}
      
      {children}
    </div>
  );
};

export default BasePage;