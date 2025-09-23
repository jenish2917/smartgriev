import React from 'react';
import { Card, Row, Col, Button, Typography, Space, Divider, Tag, Menu } from 'antd';
import { 
  RobotOutlined, 
  DashboardOutlined, 
  CommentOutlined, 
  BarChartOutlined,
  UserOutlined,
  SettingOutlined,
  FileTextOutlined,
  GlobalOutlined,
  LoginOutlined,
  HomeOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;

const LandingPage: React.FC = () => {
  const location = useLocation();

  const topMenuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Home',
    },
    {
      key: '/complaint-flow',
      icon: <FileTextOutlined />,
      label: 'Submit Complaint',
    },
    {
      key: '/complaint-dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/ai-test',
      icon: <RobotOutlined />,
      label: 'AI Test',
    },
    {
      key: '/login',
      icon: <LoginOutlined />,
      label: 'Login',
    },
  ];
  const features = [
    {
      title: 'Enhanced Complaint Submission',
      description: 'Step-by-step guided complaint submission with comprehensive categorization and AI assistance',
      icon: <FileTextOutlined style={{ fontSize: 32, color: '#FF9933' }} />,
      link: '/complaint-flow',
      status: 'New!',
      color: 'orange'
    },
    {
      title: 'Smart Complaint Dashboard',
      description: 'Advanced complaint tracking dashboard with real-time status updates and analytics',
      icon: <DashboardOutlined style={{ fontSize: 32, color: '#138808' }} />,
      link: '/complaint-dashboard',
      status: 'New!',
      color: 'green'
    },
    {
      title: 'AI Complaint Classification',
      description: 'Automatically classify complaints into appropriate departments using Groq AI with Llama3 model',
      icon: <RobotOutlined style={{ fontSize: 32, color: '#000080' }} />,
      link: '/ai-test',
      status: 'Live',
      color: 'blue'
    },
    {
      title: 'Legacy Complaint Form',
      description: 'Simple complaint submission form with AI classification integration',
      icon: <CommentOutlined style={{ fontSize: 32, color: '#666666' }} />,
      link: '/complaint',
      status: 'Legacy',
      color: 'default'
    },
    {
      title: 'Analytics & Reports',
      description: 'Advanced analytics with performance metrics and geospatial data visualization',
      icon: <BarChartOutlined style={{ fontSize: 32, color: '#138808' }} />,
      link: '/analytics',
      status: 'Available',
      color: 'green'
    },
    {
      title: 'Geospatial Analytics',
      description: 'Location-based complaint analysis with interactive maps and heat maps',
      icon: <GlobalOutlined style={{ fontSize: 32, color: '#000080' }} />,
      link: '/analytics/geospatial',
      status: 'Available',
      color: 'blue'
    }
  ];

  return (
    <div>
      {/* Government Header */}
      <div className="gov-header">
        <div className="gov-logo">
          🇮🇳
        </div>
        <Typography.Title level={2} style={{ color: 'white', margin: '0 0 8px 0' }}>
          SmartGriev
        </Typography.Title>
        <Typography.Text style={{ color: 'white', fontSize: 16 }}>
          Digital India Initiative - AI-Powered Grievance Redressal System
        </Typography.Text>
      </div>

      {/* Top Navigation */}
      <div style={{ 
        background: 'white', 
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)', 
        padding: '0 20px'
      }}>
        <Menu
          mode="horizontal"
          selectedKeys={[location.pathname]}
          style={{ 
            border: 'none', 
            fontSize: 16,
            background: 'linear-gradient(90deg, #FF9933 0%, #138808 100%)',
            borderRadius: '0 0 8px 8px'
          }}
        >
          {topMenuItems.map(item => (
            <Menu.Item key={item.key} icon={item.icon} style={{ color: 'white', fontWeight: '600' }}>
              <Link to={item.key} style={{ color: 'white' }}>{item.label}</Link>
            </Menu.Item>
          ))}
        </Menu>
      </div>

      <div style={{ padding: '40px 20px', maxWidth: 1200, margin: '0 auto', background: '#F5F5F5' }}>
      <div style={{ textAlign: 'center', marginBottom: 40, background: 'white', padding: '40px 20px', borderRadius: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <Title level={1} style={{ color: '#333333', marginBottom: 16 }} className="national-emblem">
          🚀 AI-Powered Grievance Management System
        </Title>
        <Paragraph style={{ fontSize: 18, color: '#666', maxWidth: 700, margin: '0 auto' }}>
          Empowering citizens with intelligent complaint resolution through advanced AI classification, 
          seamless tracking, and transparent governance - A <Text strong style={{ color: '#FF9933' }}>Digital India</Text> initiative
        </Paragraph>
        
        <Space size="large" style={{ marginTop: 20 }}>
          <Tag className="success-state" style={{ padding: '6px 12px', fontSize: 14, fontWeight: '600' }}>
            ✅ Backend Ready (Django 5.2.4)
          </Tag>
          <Tag className="info-state" style={{ padding: '6px 12px', fontSize: 14, fontWeight: '600' }}>
            ✅ Frontend Active (React 18)
          </Tag>
          <Tag className="warning-state" style={{ padding: '6px 12px', fontSize: 14, fontWeight: '600' }}>
            🤖 AI Classification Live
          </Tag>
        </Space>

        {/* Main Action Buttons */}
        <div style={{ marginTop: 32 }}>
          <Space size="large" wrap>
            <Link to="/complaint-flow">
              <Button 
                type="primary"
                size="large"
                icon={<FileTextOutlined />}
                className="primary-button"
                style={{
                  height: 60,
                  fontSize: 18,
                  fontWeight: 'bold',
                  borderRadius: 12,
                  paddingLeft: 30,
                  paddingRight: 30,
                  background: 'linear-gradient(90deg, #FF9933 0%, #138808 100%)',
                  border: '3px solid #000080',
                  boxShadow: '0 6px 20px rgba(255,153,51,0.4)'
                }}
              >
                � Enhanced Complaint System
              </Button>
            </Link>
            
            <Link to="/complaint-dashboard">
              <Button 
                size="large"
                icon={<DashboardOutlined />}
                style={{
                  height: 60,
                  fontSize: 18,
                  fontWeight: 'bold',
                  borderRadius: 12,
                  paddingLeft: 30,
                  paddingRight: 30,
                  borderColor: '#138808',
                  color: '#138808',
                  background: 'white'
                }}
              >
                📊 View Dashboard
              </Button>
            </Link>
          </Space>
        </div>
      </div>

      <Divider />

      <Row gutter={[24, 24]}>
        {features.map((feature, index) => (
          <Col xs={24} sm={12} lg={8} key={index}>
            <Card
              className="feature-card"
              hoverable
              style={{ 
                height: '100%',
                borderRadius: 12,
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                border: '2px solid #FF9933',
                transition: 'all 0.3s ease'
              }}
              bodyStyle={{ padding: 24 }}
            >
              <div style={{ textAlign: 'center', marginBottom: 16 }}>
                {feature.icon}
                <Title level={4} style={{ marginTop: 12, marginBottom: 8, color: '#333' }}>
                  {feature.title}
                </Title>
                <Tag 
                  className={feature.color === 'orange' ? 'warning-state' : feature.color === 'green' ? 'success-state' : 'info-state'}
                  style={{ fontWeight: 'bold' }}
                >
                  {feature.status}
                </Tag>
              </div>
              
              <Paragraph style={{ 
                textAlign: 'center', 
                color: '#666', 
                minHeight: 60,
                marginBottom: 20 
              }}>
                {feature.description}
              </Paragraph>
              
              <div style={{ textAlign: 'center' }}>
                <Link to={feature.link}>
                  <Button 
                    className="primary-button"
                    type="primary" 
                    style={{ 
                      width: '100%',
                      height: 40,
                      fontWeight: 'bold',
                      borderRadius: 6
                    }}
                  >
                    Launch Feature
                  </Button>
                </Link>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Divider />

      <Card 
        style={{ 
          marginTop: 40, 
          background: 'linear-gradient(135deg, #FF9933 0%, #138808 100%)',
          border: '2px solid #000080',
          borderRadius: 12,
          boxShadow: '0 8px 24px rgba(255,153,51,0.3)'
        }}
        bodyStyle={{ padding: 40 }}
      >
        <Row align="middle">
          <Col xs={24} lg={16}>
            <Title level={2} style={{ color: 'white', marginBottom: 16, textShadow: '2px 2px 4px rgba(0,0,0,0.3)' }}>
              🎯 Test AI Classification Now!
            </Title>
            <Paragraph style={{ color: 'white', fontSize: 16, marginBottom: 20, textShadow: '1px 1px 2px rgba(0,0,0,0.3)' }}>
              Experience the power of AI-driven complaint classification. Our system automatically 
              routes complaints to the right department using advanced natural language processing 
              for efficient governance and citizen service.
            </Paragraph>
            <Space>
              <Text style={{ color: 'white', fontWeight: 'bold' }}>Powered by:</Text>
              <Tag className="warning-state" style={{ fontWeight: 'bold' }}>🤖 Groq API</Tag>
              <Tag className="success-state" style={{ fontWeight: 'bold' }}>🦾 Llama3 Model</Tag>
              <Tag className="info-state" style={{ fontWeight: 'bold' }}>⚡ Django + React</Tag>
            </Space>
          </Col>
          <Col xs={24} lg={8} style={{ textAlign: 'center' }}>
            <Link to="/ai-test">
              <Button 
                type="primary" 
                size="large" 
                icon={<RobotOutlined />}
                className="primary-button"
                style={{ 
                  height: 60,
                  fontSize: 18,
                  fontWeight: 'bold',
                  background: 'white',
                  color: '#FF9933',
                  border: '2px solid #000080',
                  borderRadius: 8,
                  boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
                  width: '100%'
                }}
              >
                Test AI Classification
              </Button>
            </Link>
          </Col>
        </Row>
      </Card>

      <div style={{ textAlign: 'center', marginTop: 40, padding: 20 }}>
        <Title level={3}>🏆 Architecture Highlights</Title>
        <Row gutter={[16, 16]} style={{ marginTop: 20 }}>
          <Col xs={12} md={6}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <Text strong>Clean Architecture</Text>
              <br />
              <Text type="secondary">SOLID Principles</Text>
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <Text strong>Dependency Injection</Text>
              <br />
              <Text type="secondary">IoC Container</Text>
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <Text strong>Error Boundaries</Text>
              <br />
              <Text type="secondary">Global Handling</Text>
            </Card>
          </Col>
          <Col xs={12} md={6}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <Text strong>Type Safety</Text>
              <br />
              <Text type="secondary">100% TypeScript</Text>
            </Card>
          </Col>
        </Row>
      </div>
      </div>
    </div>
  );
};

export default LandingPage;