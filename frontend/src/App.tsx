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

// Route configuration with types
interface RouteConfig {
  path: string;
  component: React.ComponentType;
  layout: React.ComponentType<{ children: React.ReactNode }>;
  auth: 'public' | 'protected';
}

const routesConfig: RouteConfig[] = [
  { path: '/login', component: Login, layout: AuthLayout, auth: 'public' },
  { path: '/register', component: Register, layout: AuthLayout, auth: 'public' },
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

const RouteWrapper: React.FC<RouteConfig> = ({ component: Component, layout: Layout, auth }) => {
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  if (auth === 'protected' && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (auth === 'public' && isAuthenticated) {
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
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            {routesConfig.map((route, index) => (
              <Route
                key={index}
                path={route.path}
                element={<RouteWrapper {...route} />}
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