import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';

import { useAuthStore } from '@/store/authStore';
import { useTokenRefresh } from '@/hooks/useTokenRefresh';
import App from '@/App';
import { LoginPage } from '@/pages/auth/LoginPage';
import { RegisterPage } from '@/pages/auth/RegisterPage';
import { ChatbotPage } from '@/pages/chatbot/ChatbotPage';
import { ComplaintsPage } from '@/pages/complaints/ComplaintsPage';
import { ProfilePage } from '@/pages/profile/ProfilePage';
import { SettingsPage } from '@/pages/settings/SettingsPage';

// Protected Route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  // Automatic token refresh
  useTokenRefresh();

  // Immediate redirect without any render
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public Route wrapper (redirect to complaints if already logged in)
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/complaints" replace />;
  }

  return <>{children}</>;
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
