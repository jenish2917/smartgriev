import React from 'react';
import { Layout } from 'antd';
import AppHeader from './AppHeader';
import AppFooter from './AppFooter';

const { Content } = Layout;

interface AuthLayoutProps {
  children: React.ReactNode;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <AppHeader />
      <Content style={{ flex: 1 }}>
        {children}
      </Content>
      <AppFooter />
    </Layout>
  );
};

export default AuthLayout;
