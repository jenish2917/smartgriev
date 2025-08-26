import React from 'react';
import { Layout, Typography } from 'antd';

const { Content } = Layout;
const { Title } = Typography;

interface AuthLayoutProps {
  children: React.ReactNode;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Content
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '20px',
        }}
      >
        <div
          style={{
            maxWidth: 400,
            width: '100%',
            background: 'white',
            borderRadius: '12px',
            padding: '40px',
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
          }}
        >
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <Title level={2} style={{ color: '#1890ff', marginBottom: '8px' }}>
              SmartGriev
            </Title>
            <Typography.Text type="secondary">
              Enterprise Grievance Management Platform
            </Typography.Text>
          </div>
          {children}
        </div>
      </Content>
    </Layout>
  );
};

export default AuthLayout;
