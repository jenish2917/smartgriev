import { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';

import { useAuthStore } from '@/store/authStore';
import { useTokenRefresh } from '@/hooks/useTokenRefresh';
import App from '@/App';

// Lazy load pages for better performance
const LoginPage = lazy(() => import('@/pages/auth/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('@/pages/auth/RegisterPage').then(m => ({ default: m.RegisterPage })));
const ChatbotPage = lazy(() => import('@/pages/chatbot/ChatbotPage').then(m => ({ default: m.ChatbotPage })));
const ComplaintsPage = lazy(() => import('@/pages/complaints/ComplaintsPage').then(m => ({ default: m.ComplaintsPage })));
const ProfilePage = lazy(() => import('@/pages/profile/ProfilePage').then(m => ({ default: m.ProfilePage })));
const SettingsPage = lazy(() => import('@/pages/settings/SettingsPage').then(m => ({ default: m.SettingsPage })));

// Loading fallback component
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
  </div>
);

// Protected Route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  // Automatic token refresh
  useTokenRefresh();

  // Immediate redirect without any render
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Suspense fallback={<PageLoader />}>{children}</Suspense>;
};

// Public Route wrapper (redirect to complaints if already logged in)
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/complaints" replace />;
  }

  return <Suspense fallback={<PageLoader />}>{children}</Suspense>;
};

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
  },
  {
    path: '/login',
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: '/register',
    element: (
      <PublicRoute>
        <RegisterPage />
      </PublicRoute>
    ),
  },
  {
    path: '/dashboard',
    element: <Navigate to="/complaints" replace />,
  },
    {
      path: '/chat',
      element: (
        <ProtectedRoute>
          <ChatbotPage />
        </ProtectedRoute>
      ),
    },
    {
      path: '/complaints',
      element: (
        <ProtectedRoute>
          <ComplaintsPage />
        </ProtectedRoute>
      ),
    },
    {
      path: '/profile',
      element: (
        <ProtectedRoute>
          <ProfilePage />
        </ProtectedRoute>
      ),
    },
    {
      path: '/settings',
      element: (
        <ProtectedRoute>
          <SettingsPage />
        </ProtectedRoute>
      ),
    },
    {
      path: '*',
      element: <Navigate to="/" replace />,
    },
  ]);export const AppRouter = () => {
  return <RouterProvider router={router} />;
};
