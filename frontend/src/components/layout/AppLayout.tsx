import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import {
  Layout,
  Menu,
  Button,
  Avatar,
  Dropdown,
  Badge,
  Typography,
  Space,
  Tooltip,
  Flex,
  theme,
} from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  MessageOutlined,
  BarChartOutlined,
  UserOutlined,
  BellOutlined,
  LogoutOutlined,
  SettingOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  PlusOutlined,
  HomeOutlined,
  TeamOutlined,
  SafetyOutlined,
  GlobalOutlined,
  ExperimentOutlined,
  AppstoreOutlined,
} from '@ant-design/icons';
import { RootState } from '@/store';
import { useNavigate } from 'react-router-dom';
import { logout } from '@/store/slices/authSlice';
import AppHeader from './AppHeader';
import AppFooter from './AppFooter';

const { Sider, Content } = Layout;
const { Text, Title } = Typography;

interface MenuItem {
  key: string;
  icon: React.ReactNode;
  label: string;
  path: string;
  children?: MenuItem[];
}

const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const [collapsed, setCollapsed] = useState(false);
  const { user } = useSelector((state: RootState) => state.auth);
  const { token } = theme.useToken();

  // Enhanced menu items matching backend functionality
  const menuItems: MenuItem[] = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      path: '/dashboard',
    },
    {
      key: 'complaints',
      icon: <FileTextOutlined />,
      label: 'Grievance Management',
      path: '/complaints',
      children: [
        {
          key: 'complaints-list',
          icon: <AppstoreOutlined />,
          label: 'All Complaints',
          path: '/complaints',
        },
        {
          key: 'complaints-new',
          icon: <PlusOutlined />,
          label: 'Lodge Complaint',
          path: '/complaints/new',
        },
        {
          key: 'complaints-tracking',
          icon: <GlobalOutlined />,
          label: 'Track Complaints',
          path: '/complaints/track',
        },
      ],
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: 'Analytics & Reports',
      path: '/analytics',
      children: [
        {
          key: 'analytics-dashboard',
          icon: <DashboardOutlined />,
          label: 'Real-time Analytics',
          path: '/analytics',
        },
        {
          key: 'analytics-performance',
          icon: <ExperimentOutlined />,
          label: 'Performance Metrics',
          path: '/analytics/performance',
        },
        {
          key: 'analytics-geospatial',
          icon: <GlobalOutlined />,
          label: 'Geographic Analysis',
          path: '/analytics/geospatial',
        },
      ],
    },
    {
      key: 'chatbot',
      icon: <MessageOutlined />,
      label: 'AI Assistant',
      path: '/chatbot',
    },
    {
      key: 'notifications',
      icon: <BellOutlined />,
      label: 'Notifications',
      path: '/notifications',
    },
    {
      key: 'ml-models',
      icon: <ExperimentOutlined />,
      label: 'ML Models',
      path: '/ml-models',
    },
  ];

  // Officer-specific menu items
  if (user?.is_officer) {
    menuItems.push({
      key: 'officer',
      icon: <TeamOutlined />,
      label: 'Officer Panel',
      path: '/officer',
      children: [
        {
          key: 'officer-assignments',
          icon: <FileTextOutlined />,
          label: 'Assigned Complaints',
          path: '/officer/assignments',
        },
        {
          key: 'officer-analytics',
          icon: <BarChartOutlined />,
          label: 'Department Analytics',
          path: '/officer/analytics',
        },
      ],
    });
  }

  // User dropdown menu
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'My Profile',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
      onClick: () => {
        dispatch(logout());
        navigate('/login');
      },
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    // Find the menu item (including nested items)
    const findMenuItem = (items: MenuItem[], targetKey: string): MenuItem | null => {
      for (const item of items) {
        if (item.key === targetKey) return item;
        if (item.children) {
          const found = findMenuItem(item.children, targetKey);
          if (found) return found;
        }
      }
      return null;
    };

    const item = findMenuItem(menuItems, key);
    if (item) {
      navigate(item.path);
    }
  };

  // Get current selected keys
  const getSelectedKeys = () => {
    const path = location.pathname;
    if (path.startsWith('/complaints/new')) return ['complaints-new'];
    if (path.startsWith('/complaints/track')) return ['complaints-tracking'];
    if (path.startsWith('/complaints')) return ['complaints-list'];
    if (path.startsWith('/analytics/performance')) return ['analytics-performance'];
    if (path.startsWith('/analytics/geospatial')) return ['analytics-geospatial'];
    if (path.startsWith('/analytics')) return ['analytics-dashboard'];
    if (path.startsWith('/officer/assignments')) return ['officer-assignments'];
    if (path.startsWith('/officer/analytics')) return ['officer-analytics'];
    if (path.startsWith('/officer')) return ['officer'];
    if (path.startsWith('/chatbot')) return ['chatbot'];
    if (path.startsWith('/notifications')) return ['notifications'];
    if (path.startsWith('/ml-models')) return ['ml-models'];
    return ['dashboard'];
  };

  const getOpenKeys = () => {
    const path = location.pathname;
    const openKeys = [];
    if (path.startsWith('/complaints')) openKeys.push('complaints');
    if (path.startsWith('/analytics')) openKeys.push('analytics');
    if (path.startsWith('/officer')) openKeys.push('officer');
    return openKeys;
  };

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <AppHeader 
        isAuthenticated={true}
        userInfo={{
          name: user?.first_name || user?.username || 'User',
          email: user?.email || '',
          role: user?.is_officer ? 'Officer' : 'Citizen'
        }}
        onLogout={handleLogout}
      />

      <Layout style={{ marginTop: 0 }}>
        {/* Sidebar */}
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsed}
          width={280}
          style={{
            background: '#1F2937',
            position: 'fixed',
            height: 'calc(100vh - 120px)', // Adjust for header height
            left: 0,
            top: 120, // Account for header + top bar
            bottom: 0,
            zIndex: 100,
            overflow: 'auto',
          }}
        >
          <div style={{ padding: '16px', borderBottom: '1px solid #374151' }}>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ 
                color: 'white', 
                width: '100%',
                height: 40,
                marginBottom: 8,
              }}
            />
            
            {!collapsed && (
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/complaints/new')}
                style={{ 
                  width: '100%',
                  background: '#FF6600',
                  borderColor: '#FF6600',
                  height: 40,
                }}
              >
                Lodge Complaint
              </Button>
            )}
          </div>

          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={getSelectedKeys()}
            defaultOpenKeys={getOpenKeys()}
            onClick={handleMenuClick}
            style={{ background: 'transparent', border: 'none' }}
            items={menuItems.map(item => ({
              key: item.key,
              icon: item.icon,
              label: item.label,
              children: item.children?.map(child => ({
                key: child.key,
                icon: child.icon,
                label: child.label,
              })),
            }))}
          />
        </Sider>

        {/* Main Content */}
        <Layout style={{ 
          marginLeft: collapsed ? 80 : 280, 
          transition: 'margin-left 0.2s',
          background: '#F9FAFB',
          minHeight: 'calc(100vh - 120px)' // Account for header
        }}>
          <Content
            style={{
              margin: '24px',
              padding: '24px',
              background: '#FFFFFF',
              borderRadius: '8px',
              minHeight: 'calc(100vh - 170px)', // Account for margins and header
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            }}
          >
            <Outlet />
          </Content>
        </Layout>
      </Layout>
      
      <AppFooter />
    </Layout>
  );
};

export default AppLayout;
