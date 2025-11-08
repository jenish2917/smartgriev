import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import { store } from '@/store';
import { initializeServices, performHealthCheck } from '@/core/bootstrap';
import { AppErrorBoundary } from '@/components/common/ErrorBoundary';
import App from './App';
import './index.css';
import './styles/government-theme.css';
import './styles/enhanced-government-theme.css';
import './styles/components.css';

// Import i18n configuration
import './i18n';

// Initialize services
initializeServices();

// Perform health check
performHealthCheck().then(isHealthy => {
  if (!isHealthy) {
    console.warn('⚠️ Some services are not fully operational');
  }
});

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Indian Government Theme Configuration
const antdTheme = {
  token: {
    // Indian Government Brand Colors
    colorPrimary: '#FF6600', // Saffron
    colorSuccess: '#138808', // Green from flag
    colorWarning: '#FF9500',
    colorError: '#DC2626',
    colorInfo: '#0066CC',
    
    // Typography
    fontFamily: '"Noto Sans", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: 14,
    fontSizeHeading1: 32,
    fontSizeHeading2: 24,
    fontSizeHeading3: 20,
    
    // Layout
    borderRadius: 4,
    controlHeight: 36,
    
    // Official Government Colors
    colorBgContainer: '#FFFFFF',
    colorBgLayout: '#F5F5F5',
    colorBorder: '#D9D9D9',
    
    // Header colors based on Indian Government websites
    colorBgHeader: '#283891', // Deep blue like gov.in
    colorTextHeader: '#FFFFFF',
  },
  components: {
    Layout: {
      headerBg: '#283891', // Official government blue
      headerColor: '#FFFFFF',
      siderBg: '#1F2937', // Dark gray for sidebar
      bodyBg: '#F9FAFB',
      headerHeight: 64,
    },
    Menu: {
      darkItemBg: '#1F2937',
      darkSubMenuItemBg: '#374151',
      darkItemSelectedBg: '#FF6600', // Saffron highlight
      darkItemHoverBg: '#4B5563',
      darkItemColor: '#E5E7EB',
      darkItemSelectedColor: '#FFFFFF',
    },
    Button: {
      primaryColor: '#FFFFFF',
      borderRadius: 4,
      controlHeight: 36,
    },
    Card: {
      borderRadius: 8,
      headerBg: '#F8FAFC',
    },
    Table: {
      headerBg: '#F1F5F9',
      borderColor: '#E2E8F0',
    },
    Input: {
      borderRadius: 4,
      controlHeight: 36,
    },
    Form: {
      labelColor: '#374151',
      labelRequiredMarkColor: '#DC2626',
    },
    Typography: {
      titleMarginBottom: 16,
      titleMarginTop: 0,
    },
  },
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppErrorBoundary>
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <ConfigProvider theme={antdTheme}>
              <App />
            </ConfigProvider>
          </BrowserRouter>
        </QueryClientProvider>
      </Provider>
    </AppErrorBoundary>
  </React.StrictMode>
);

console.log('📡 Backend URL:', import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/complaints/api');
console.log('🔧 Environment:', import.meta.env.MODE);
console.log('🚀 SmartGriev App Started');
