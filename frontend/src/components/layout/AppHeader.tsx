import React, { useState } from 'react';
import { 
  Layout, 
  Typography, 
  Menu, 
  Button, 
  Space, 
  Dropdown, 
  Avatar, 
  Badge,
  Drawer,
  Row,
  Col,
  Divider
} from 'antd';
import { 
  HomeOutlined,
  FileTextOutlined,
  DashboardOutlined,
  RobotOutlined,
  LoginOutlined,
  UserOutlined,
  BellOutlined,
  MenuOutlined,
  PhoneOutlined,
  MailOutlined,
  GlobalOutlined,
  SettingOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const { Header } = Layout;
const { Title, Text } = Typography;

interface AppHeaderProps {
  isAuthenticated?: boolean;
  userInfo?: {
    name: string;
    email: string;
    role: string;
  };
  onLogout?: () => void;
}

const AppHeader: React.FC<AppHeaderProps> = ({ isAuthenticated, userInfo, onLogout }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuVisible, setMobileMenuVisible] = useState(false);

  const publicMenuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Home',
      path: '/'
    },
    {
      key: '/complaint-flow',
      icon: <FileTextOutlined />,
      label: 'Submit Complaint',
      path: '/complaint-flow'
    },
    {
      key: '/complaint-dashboard',
      icon: <DashboardOutlined />,
      label: 'Track Complaints',
      path: '/complaint-dashboard'
    },
    {
      key: '/ai-test',
      icon: <RobotOutlined />,
      label: 'AI Assistant',
      path: '/ai-test'
    }
  ];

  const authenticatedMenuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      path: '/dashboard'
    },
    {
      key: '/complaints',
      icon: <FileTextOutlined />,
      label: 'My Complaints',
      path: '/complaints'
    },
    {
      key: '/analytics',
      icon: <RobotOutlined />,
      label: 'Analytics',
      path: '/analytics'
    }
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      onClick: () => navigate('/profile')
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => navigate('/settings')
    },
    {
      key: 'divider',
      type: 'divider'
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: onLogout,
      danger: true
    }
  ];

  const menuItems = isAuthenticated ? authenticatedMenuItems : publicMenuItems;

  return (
    <>
      {/* Top Info Bar */}
      <div style={{ 
        background: '#000080', 
        color: 'white', 
        padding: '4px 0',
        fontSize: 12
      }}>
        <div style={{ 
          maxWidth: 1200, 
          margin: '0 auto', 
          padding: '0 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <Space size="large">
              <span>🇮🇳 Government of India</span>
              <span>•</span>
              <span>Digital India Initiative</span>
            </Space>
          </div>
          <div>
            <Space size="middle">
              <span><PhoneOutlined /> Helpline: 1800-XXX-XXXX</span>
              <span><MailOutlined /> support@smartgriev.gov.in</span>
              <span><GlobalOutlined /> www.smartgriev.gov.in</span>
            </Space>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <Header style={{ 
        background: 'linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%)',
        padding: 0,
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        position: 'sticky',
        top: 0,
        zIndex: 1000
      }}>
        <div style={{ 
          maxWidth: 1200, 
          margin: '0 auto', 
          padding: '0 20px',
          display: 'flex',
          alignItems: 'center',
          height: '100%'
        }}>
          {/* Logo Section */}
          <div style={{ 
            display: 'flex', 
            alignItems: 'center',
            marginRight: 40,
            minWidth: 250
          }}>
            <div style={{ 
              fontSize: 32,
              marginRight: 12,
              background: 'white',
              borderRadius: '50%',
              width: 48,
              height: 48,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}>
              🇮🇳
            </div>
            <div>
              <Title level={3} style={{ 
                margin: 0, 
                color: '#000080',
                fontWeight: 'bold',
                textShadow: '1px 1px 2px rgba(0,0,0,0.1)'
              }}>
                SmartGriev
              </Title>
              <Text style={{ 
                fontSize: 11, 
                color: '#666',
                fontWeight: '500'
              }}>
                AI-Powered Grievance Portal
              </Text>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
            <div className="desktop-only" style={{ display: 'none' }}>
              <Menu
                mode="horizontal"
                selectedKeys={[location.pathname]}
                style={{ 
                  border: 'none',
                  background: 'transparent',
                  fontSize: 14,
                  fontWeight: '600'
                }}
                items={menuItems.map(item => ({
                  key: item.key,
                  icon: item.icon,
                  label: <Link to={item.path} style={{ color: '#333' }}>{item.label}</Link>
                }))}
              />
            </div>
          </div>

          {/* Right Section */}
          <div style={{ 
            display: 'flex', 
            alignItems: 'center',
            gap: 16
          }}>
            {isAuthenticated ? (
              <Space size="middle">
                {/* Notifications */}
                <Badge count={3} size="small">
                  <Button 
                    type="text" 
                    icon={<BellOutlined />} 
                    style={{ 
                      border: '1px solid #d9d9d9',
                      borderRadius: 6
                    }}
                  />
                </Badge>

                {/* User Profile Dropdown */}
                <Dropdown
                  menu={{ 
                    items: userMenuItems.map(item => ({
                      key: item.key,
                      icon: item.icon,
                      label: item.label,
                      onClick: item.onClick,
                      danger: item.danger,
                      type: item.type as any
                    }))
                  }}
                  placement="bottomRight"
                >
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center',
                    cursor: 'pointer',
                    padding: '4px 8px',
                    borderRadius: 6,
                    border: '1px solid #d9d9d9',
                    background: 'white'
                  }}>
                    <Avatar 
                      size="small" 
                      icon={<UserOutlined />} 
                      style={{ marginRight: 8 }}
                    />
                    <div style={{ textAlign: 'left' }}>
                      <div style={{ fontSize: 12, fontWeight: 'bold', color: '#333' }}>
                        {userInfo?.name || 'User'}
                      </div>
                      <div style={{ fontSize: 10, color: '#666' }}>
                        {userInfo?.role || 'Citizen'}
                      </div>
                    </div>
                  </div>
                </Dropdown>
              </Space>
            ) : (
              <Space>
                <Link to="/login">
                  <Button 
                    icon={<LoginOutlined />}
                    style={{ 
                      borderColor: '#000080',
                      color: '#000080',
                      fontWeight: '600'
                    }}
                  >
                    Login
                  </Button>
                </Link>
                <Link to="/register">
                  <Button 
                    type="primary"
                    style={{ 
                      background: '#000080',
                      borderColor: '#000080',
                      fontWeight: '600'
                    }}
                  >
                    Register
                  </Button>
                </Link>
              </Space>
            )}

            {/* Mobile Menu Button */}
            <Button
              className="mobile-only"
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setMobileMenuVisible(true)}
              style={{ 
                display: 'none',
                border: '1px solid #d9d9d9'
              }}
            />
          </div>
        </div>
      </Header>

      {/* Mobile Menu Drawer */}
      <Drawer
        title={
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span style={{ fontSize: 24, marginRight: 12 }}>🇮🇳</span>
            <div>
              <div style={{ fontWeight: 'bold' }}>SmartGriev</div>
              <div style={{ fontSize: 12, color: '#666' }}>Navigation Menu</div>
            </div>
          </div>
        }
        placement="right"
        closable={true}
        onClose={() => setMobileMenuVisible(false)}
        open={mobileMenuVisible}
        width={280}
      >
        <Menu
          mode="vertical"
          selectedKeys={[location.pathname]}
          style={{ border: 'none' }}
          items={menuItems.map(item => ({
            key: item.key,
            icon: item.icon,
            label: <Link to={item.path} onClick={() => setMobileMenuVisible(false)}>{item.label}</Link>
          }))}
        />
        
        <Divider />
        
        {!isAuthenticated && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Link to="/login" onClick={() => setMobileMenuVisible(false)}>
              <Button type="primary" block icon={<LoginOutlined />}>
                Login
              </Button>
            </Link>
            <Link to="/register" onClick={() => setMobileMenuVisible(false)}>
              <Button block>
                Register
              </Button>
            </Link>
          </Space>
        )}
      </Drawer>

      <style>{`
        @media (min-width: 768px) {
          .desktop-only {
            display: block !important;
          }
          .mobile-only {
            display: none !important;
          }
        }
        
        @media (max-width: 767px) {
          .desktop-only {
            display: none !important;
          }
          .mobile-only {
            display: block !important;
          }
        }
      `}</style>
    </>
  );
};

export default AppHeader;