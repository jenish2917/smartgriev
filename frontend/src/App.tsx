import React, { useEffect, Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, ConfigProvider, Spin } from 'antd';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { getProfileAsync } from '@/store/slices/authSlice';
import { TokenManager } from '@/services/api';

// Layout components
const AppLayout = lazy(() => import('@/components/layout/AppLayout'));
const AuthLayout = lazy(() => import('@/components/layout/AuthLayout'));

// Page components (lazy loaded)
const Login = lazy(() => import('@/pages/auth/Login'));
const Register = lazy(() => import('@/pages/auth/Register'));
const Dashboard = lazy(() => import('@/pages/dashboard/Dashboard'));
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

// Route configuration with types
interface RouteConfig {
  path: string;
  component: React.ComponentType;
  layout: React.ComponentType<{ children: React.ReactNode }>;
  auth: 'public' | 'protected';
}

const routesConfig: RouteConfig[] = [
  { path: '/', component: LandingPage, layout: AuthLayout, auth: 'public' }, // Landing page - always accessible
  { path: '/complaint', component: SimpleComplaint, layout: AuthLayout, auth: 'public' }, // Simple complaint form
  { path: '/complaint-flow', component: ComplaintSubmissionFlow, layout: AuthLayout, auth: 'public' }, // Enhanced complaint flow
  { path: '/complaint-dashboard', component: ComplaintDashboard, layout: AuthLayout, auth: 'public' }, // Complaint dashboard
  { path: '/login', component: Login, layout: AuthLayout, auth: 'public' },
  { path: '/register', component: Register, layout: AuthLayout, auth: 'public' },
  { path: '/ai-test', component: AIClassifierTest, layout: AuthLayout, auth: 'public' }, // Add AI test route
  { path: '/dashboard', component: Dashboard, layout: AppLayout, auth: 'protected' },
  { path: '/complaints', component: Complaints, layout: AppLayout, auth: 'protected' },
  { path: '/complaints/new', component: CreateComplaint, layout: AppLayout, auth: 'protected' },
  { path: '/complaints/track', component: ComplaintTracking, layout: AppLayout, auth: 'protected' },
  { path: '/complaints/:id', component: ComplaintDetail, layout: AppLayout, auth: 'protected' },
  { path: '/analytics', component: Analytics, layout: AppLayout, auth: 'protected' },
  { path: '/analytics/performance', component: PerformanceMetrics, layout: AppLayout, auth: 'protected' },
  { path: '/analytics/geospatial', component: GeospatialAnalytics, layout: AppLayout, auth: 'protected' },
  { path: '/chatbot', component: Chatbot, layout: AppLayout, auth: 'protected' },
  { path: '/notifications', component: Notifications, layout: AppLayout, auth: 'protected' },
  { path: '/ml-models', component: MLModels, layout: AppLayout, auth: 'protected' },
  { path: '/officer', component: OfficerDashboard, layout: AppLayout, auth: 'protected' },
  { path: '/officer/assignments', component: OfficerAssignments, layout: AppLayout, auth: 'protected' },
  { path: '/officer/analytics', component: OfficerAnalytics, layout: AppLayout, auth: 'protected' },
  { path: '/profile', component: Profile, layout: AppLayout, auth: 'protected' },
  { path: '/settings', component: Settings, layout: AppLayout, auth: 'protected' },
];

const ProtectedRoute: React.FC<{ route: RouteConfig }> = ({ route }) => {
  const { isAuthenticated } = useAppSelector((state) => state.auth);
  const { component: Component, layout: Layout, auth, path } = route;

  // Special handling for public pages - always allow access
  if (path === '/' || path === '/ai-test' || path === '/complaint' || path === '/complaint-flow' || path === '/complaint-dashboard') {
    return (
      <Layout>
        <Component />
      </Layout>
    );
  }

  if (auth === 'protected' && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (auth === 'public' && isAuthenticated && path !== '/ai-test' && path !== '/' && path !== '/complaint' && path !== '/complaint-flow' && path !== '/complaint-dashboard') {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <Layout>
      <Component />
    </Layout>
  );
};

const App = () => {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);

  useEffect(() => {
    if (TokenManager.isAuthenticated() && !user) {
      dispatch(getProfileAsync());
    }
  }, [dispatch, user]);

  return (
    <ConfigProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Suspense fallback={<Spin size="large" style={{ margin: 'auto' }} />}>
          <Routes>
            {routesConfig.map((route, index) => (
              <Route
                key={index}
                path={route.path}
                element={<ProtectedRoute route={route} />}
              />
            ))}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </Layout>
    </ConfigProvider>
  );
};

export default App;