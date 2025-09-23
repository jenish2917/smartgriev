/**
 * Example Component using Clean Architecture
 * Demonstrates proper separation of concerns and dependency injection
 */

import React, { useEffect } from 'react';
import { Card, Button, Spin, Alert, List, Typography, Space, Tag } from 'antd';
import { ReloadOutlined, PlusOutlined } from '@ant-design/icons';
import { useComplaints, useAuth, useDashboard } from '@/hooks';
import { ComplaintStatus, Priority } from '@/types/core';

const { Title, Text } = Typography;

/**
 * Dashboard component showcasing clean architecture patterns
 */
export const CleanArchitectureDashboard: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const { data: metrics, loading: metricsLoading, error: metricsError, refresh: refreshMetrics } = useDashboard();
  const { 
    complaints, 
    loading: complaintsLoading, 
    error: complaintsError, 
    refresh: refreshComplaints 
  } = useComplaints({ limit: 5 });

  useEffect(() => {
    // Component automatically loads data through hooks
    // No direct service calls or complex state management needed
  }, []);

  const getPriorityColor = (priority: Priority): string => {
    const colors = {
      [Priority.LOW]: 'green',
      [Priority.MEDIUM]: 'orange',
      [Priority.HIGH]: 'red',
      [Priority.CRITICAL]: 'purple',
    };
    return colors[priority] || 'default';
  };

  const getStatusColor = (status: ComplaintStatus): string => {
    const colors = {
      [ComplaintStatus.DRAFT]: 'default',
      [ComplaintStatus.SUBMITTED]: 'blue',
      [ComplaintStatus.ACKNOWLEDGED]: 'cyan',
      [ComplaintStatus.IN_PROGRESS]: 'orange',
      [ComplaintStatus.RESOLVED]: 'green',
      [ComplaintStatus.CLOSED]: 'gray',
      [ComplaintStatus.REJECTED]: 'red',
    };
    return colors[status] || 'default';
  };

  if (!isAuthenticated) {
    return (
      <Card>
        <Alert 
          message="Authentication Required" 
          description="Please log in to view the dashboard" 
          type="warning" 
          showIcon 
        />
      </Card>
    );
  }

  return (
    <div className="clean-architecture-dashboard">
      <Title level={2}>
        Welcome back, {user?.firstName} {user?.lastName}!
      </Title>
      
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Metrics Section */}
        <Card 
          title="Dashboard Metrics" 
          extra={
            <Button 
              icon={<ReloadOutlined />} 
              onClick={refreshMetrics}
              loading={metricsLoading}
            >
              Refresh
            </Button>
          }
        >
          {metricsLoading ? (
            <Spin tip="Loading metrics..." />
          ) : metricsError ? (
            <Alert 
              message="Failed to load metrics" 
              description={metricsError} 
              type="error" 
              showIcon 
            />
          ) : metrics ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <Card size="small">
                <Text type="secondary">Total Complaints</Text>
                <Title level={3} style={{ margin: 0 }}>{metrics.totalComplaints}</Title>
              </Card>
              <Card size="small">
                <Text type="secondary">Pending</Text>
                <Title level={3} style={{ margin: 0, color: '#fa8c16' }}>{metrics.pendingComplaints}</Title>
              </Card>
              <Card size="small">
                <Text type="secondary">Resolved</Text>
                <Title level={3} style={{ margin: 0, color: '#52c41a' }}>{metrics.resolvedComplaints}</Title>
              </Card>
              <Card size="small">
                <Text type="secondary">Avg Resolution Time</Text>
                <Title level={3} style={{ margin: 0 }}>{metrics.averageResolutionTime}h</Title>
              </Card>
            </div>
          ) : null}
        </Card>

        {/* Recent Complaints Section */}
        <Card
          title="Recent Complaints"
          extra={
            <Space>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={refreshComplaints}
                loading={complaintsLoading}
              >
                Refresh
              </Button>
              <Button 
                type="primary" 
                icon={<PlusOutlined />}
                href="/complaints/new"
              >
                New Complaint
              </Button>
            </Space>
          }
        >
          {complaintsLoading ? (
            <Spin tip="Loading complaints..." />
          ) : complaintsError ? (
            <Alert 
              message="Failed to load complaints" 
              description={complaintsError} 
              type="error" 
              showIcon 
            />
          ) : complaints?.results ? (
            <List
              itemLayout="horizontal"
              dataSource={complaints.results}
              renderItem={(complaint) => (
                <List.Item
                  actions={[
                    <Button type="link" href={`/complaints/${complaint.id}`}>
                      View Details
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <Space>
                        <Text strong>{complaint.title}</Text>
                        <Tag color={getPriorityColor(complaint.priority)}>
                          {complaint.priority.toUpperCase()}
                        </Tag>
                        <Tag color={getStatusColor(complaint.status)}>
                          {complaint.status.replace('_', ' ').toUpperCase()}
                        </Tag>
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size="small">
                        <Text type="secondary">
                          {complaint.description.substring(0, 100)}
                          {complaint.description.length > 100 ? '...' : ''}
                        </Text>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          Created: {new Date(complaint.createdAt).toLocaleDateString()}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          ) : (
            <Alert 
              message="No complaints found" 
              description="You haven't submitted any complaints yet" 
              type="info" 
              showIcon 
            />
          )}
        </Card>
      </Space>
    </div>
  );
};

export default CleanArchitectureDashboard;