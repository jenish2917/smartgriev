import React, { useEffect, Suspense, lazy, useState, useCallback } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, ConfigProvider, Spin } from 'antd';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { getProfileAsync } from '@/store/slices/authSlice';
import { TokenManager } from '@/services/api';
import Navbar from './components/Navbar';

// Layout components
const AppLayout = lazy(() => import('@/components/layout/AppLayout'));
const AuthLayout = lazy(() => import('@/components/layout/AuthLayout'));

// New Blue Theme Pages
const Home = lazy(() => import('./pages/Home'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Complaints = lazy(() => import('@/pages/complaints/Complaints'));
const ComplaintDetail = lazy(() => import('@/pages/complaints/ComplaintDetail'));
const CreateComplaint = lazy(() => import('@/pages/complaints/CreateComplaint'));
const ComplaintTracking = lazy(() => import('@/pages/complaints/ComplaintTracking'));
const Analytics = lazy(() => import('@/pages/analytics/Analytics'));
const PerformanceMetrics = lazy(() => import('@/pages/analytics/PerformanceMetrics'));
const GeospatialAnalytics = lazy(() => import('@/pages/analytics/GeospatialAnalytics'));
const Chatbot = lazy(() => import('@/pages/chatbot/Chatbot'));
const Notifications = lazy(() => import('@/pages/notifications/Notifications'));
const MLModels = lazy(() => import('@/pages/ml-models/MLModels'));
const OfficerDashboard = lazy(() => import('@/pages/officer/OfficerDashboard'));
const OfficerAssignments = lazy(() => import('@/pages/officer/OfficerAssignments'));
const OfficerAnalytics = lazy(() => import('@/pages/officer/OfficerAnalytics'));
const Profile = lazy(() => import('@/pages/profile/Profile'));
const Settings = lazy(() => import('@/pages/settings/Settings'));
const NotFound = lazy(() => import('@/pages/NotFound'));

// AI Classification Test Component
const AIClassifierTest = lazy(() => import('@/components/features/AIComplaintClassifier'));
const LandingPage = lazy(() => import('@/pages/LandingPage'));
const SimpleComplaint = lazy(() => import('@/pages/SimpleComplaint'));

// New Enhanced Complaint Components
const ComplaintSubmissionFlow = lazy(() => import('@/components/complaint/ComplaintSubmissionFlow'));
const ComplaintDashboard = lazy(() => import('@/components/complaint/ComplaintDashboard'));

// Multimodal Complaint Components
const MultimodalComplaintSubmit = lazy(() => import('./components/MultimodalComplaintSubmit'));
const MyComplaintsList = lazy(() => import('./components/MyComplaintsList'));

// Route configuration with types
interface RouteConfig {
  path: string;
  component: React.ComponentType;
  layout: React.ComponentType<{ children: React.ReactNode }>;
  auth: 'public' | 'protected';
}

const routesConfig: RouteConfig[] = [
  { path: '/', component: Home, layout: React.Fragment, auth: 'public' }, // New Home page
  { path: '/login', component: Login, layout: React.Fragment, auth: 'public' },
  { path: '/register', component: Register, layout: React.Fragment, auth: 'public' },
  { path: '/forgot-password', component: ForgotPassword, layout: React.Fragment, auth: 'public' },
  { path: '/dashboard', component: Dashboard, layout: React.Fragment, auth: 'protected' }, // New Dashboard
  { path: '/complaint', component: SimpleComplaint, layout: AuthLayout, auth: 'public' }, // Simple complaint form
  { path: '/complaint-flow', component: ComplaintSubmissionFlow, layout: AuthLayout, auth: 'public' }, // Enhanced complaint flow
  { path: '/complaint-dashboard', component: ComplaintDashboard, layout: AuthLayout, auth: 'public' }, // Complaint dashboard
  { path: '/multimodal-submit', component: MultimodalComplaintSubmit, layout: React.Fragment, auth: 'public' }, // Multimodal complaint submission
  { path: '/my-complaints', component: MyComplaintsList, layout: React.Fragment, auth: 'protected' }, // User's complaints list
  { path: '/ai-test', component: AIClassifierTest, layout: AuthLayout, auth: 'public' }, // Add AI test route
  { path: '/old-dashboard', component: Complaints, layout: AppLayout, auth: 'protected' },
  { path: '/complaints', component: Complaints, layout: AppLayout, auth: 'protected' },
  { path: '/complaints/new', component: CreateComplaint, layout: AppLayout, auth: 'protected' },
  { path: '/complaints/track', component: ComplaintTracking, layout: AppLayout, auth: 'protected' },
  { path: '/complaints/:id', component: ComplaintDetail, layout: AppLayout, auth: 'protected' },
  { path: '/analytics', component: Analytics, layout: AppLayout, auth: 'protected' },
  { path: '/analytics/performance', component: PerformanceMetrics, layout: AppLayout, auth: 'protected' },
  { path: '/analytics/geospatial', component: GeospatialAnalytics, layout: AppLayout, auth: 'protected' },
  { path: '/chatbot', component: Chatbot, layout: React.Fragment, auth: 'public' },
  { path: '/notifications', component: Notifications, layout: AppLayout, auth: 'protected' },
  { path: '/ml-models', component: MLModels, layout: AppLayout, auth: 'protected' },
  { path: '/officer', component: OfficerDashboard, layout: AppLayout, auth: 'protected' },
  { path: '/officer/assignments', component: OfficerAssignments, layout: AppLayout, auth: 'protected' },
  { path: '/officer/analytics', component: OfficerAnalytics, layout: AppLayout, auth: 'protected' },
  { path: '/profile', component: Profile, layout: AppLayout, auth: 'protected' },
  { path: '/settings', component: Settings, layout: AppLayout, auth: 'protected' },
];

const ProtectedRoute: React.FC<{ route: RouteConfig; user: any }> = ({ route, user }) => {
  const { component: Component, layout: Layout, auth, path } = route;
  const isAuthenticated = !!localStorage.getItem('token');

  // Public pages - always accessible
  const publicPaths = ['/', '/login', '/register', '/forgot-password', '/ai-test', '/complaint', '/complaint-flow', '/complaint-dashboard', '/multimodal-submit', '/chatbot'];
  
  if (publicPaths.includes(path)) {
    if (Layout === React.Fragment) {
      return <Component />;
    }
    return (
      <Layout>
        <Component />
      </Layout>
    );
  }

  // Protected pages - require authentication
  if (auth === 'protected' && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Render with layout
  if (Layout === React.Fragment) {
    return <Component />;
  }
  
  return (
    <Layout>
      <Component />
    </Layout>
  );
};

const App = () => {
  const dispatch = useAppDispatch();
  const { user: reduxUser } = useAppSelector((state) => state.auth);
  const [user, setUser] = useState<any>(null);

  // Load user from localStorage
  const loadUser = useCallback(() => {
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    
    if (storedUser && token) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
      } catch (e) {
        console.error('Error parsing user data:', e);
        setUser(null);
        // Clear invalid data
        localStorage.removeItem('user');
      }
    } else {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    // Initial load
    loadUser();

    // Listen for user changes (login/logout events)
    const handleUserChange = (event: Event) => {
      loadUser();
    };

    window.addEventListener('userChange', handleUserChange as EventListener);

    return () => {
      window.removeEventListener('userChange', handleUserChange as EventListener);
    };
  }, [loadUser]);

  useEffect(() => {
    if (TokenManager.isAuthenticated() && !reduxUser) {
      dispatch(getProfileAsync());
    }
  }, [dispatch, reduxUser]);

  return (
    <ConfigProvider>
      <div style={{ minHeight: '100vh', backgroundColor: '#F5F5F5' }}>
        <Navbar user={user} />
        <Suspense fallback={
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            minHeight: '100vh' 
          }}>
            <Spin size="large" />
          </div>
        }>
          <Routes>
            {routesConfig.map((route, index) => (
              <Route
                key={index}
                path={route.path}
                element={<ProtectedRoute route={route} user={user} />}
              />
            ))}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </div>
    </ConfigProvider>
  );
};

export default App;