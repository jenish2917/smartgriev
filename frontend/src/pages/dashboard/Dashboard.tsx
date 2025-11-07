import React, { useEffect, useState } from 'react';
import {
  Row,
  Col,
  Card,
  Statistic,
  Progress,
  List,
  Typography,
  Space,
  Badge,
  Button,
  Spin,
} from 'antd';
import {
  ArrowUpOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;

// Mock data - replace with real API calls
const mockDashboardData = {
  stats: {
    totalComplaints: 1247,
    pendingComplaints: 89,
    resolvedComplaints: 1158,
    resolutionRate: 92.9,
    avgResolutionTime: 4.2,
    satisfactionScore: 4.3,
  },
  trends: [
    { date: '2024-01', complaints: 67, resolved: 62 },
    { date: '2024-02', complaints: 89, resolved: 84 },
    { date: '2024-03', complaints: 103, resolved: 98 },
    { date: '2024-04', complaints: 156, resolved: 142 },
    { date: '2024-05', complaints: 178, resolved: 165 },
    { date: '2024-06', complaints: 134, resolved: 128 },
  ],
  categoryDistribution: [
    { name: 'Infrastructure', value: 35, color: '#1890ff' },
    { name: 'Public Services', value: 28, color: '#52c41a' },
    { name: 'Health', value: 18, color: '#faad14' },
    { name: 'Environment', value: 12, color: '#f5222d' },
    { name: 'Others', value: 7, color: '#722ed1' },
  ],
  recentComplaints: [
    { id: 1, title: 'Broken streetlight on Main Road', status: 'pending', priority: 'high', time: '2 hours ago' },
    { id: 2, title: 'Water supply disruption in Block A', status: 'in_progress', priority: 'urgent', time: '4 hours ago' },
    { id: 3, title: 'Garbage collection missed', status: 'resolved', priority: 'medium', time: '6 hours ago' },
    { id: 4, title: 'Park maintenance required', status: 'pending', priority: 'low', time: '8 hours ago' },
    { id: 5, title: 'Traffic signal malfunction', status: 'in_progress', priority: 'high', time: '10 hours ago' },
  ],
};

const Dashboard: React.FC = () => {
  const { t } = useTranslation('dashboard');
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(mockDashboardData);

  useEffect(() => {
    // Simulate API call
    const fetchDashboardData = async () => {
      setLoading(true);
      // Replace with actual API call
      setTimeout(() => {
        setData(mockDashboardData);
        setLoading(false);
      }, 1000);
    };

    fetchDashboardData();
  }, []);

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { color: 'orange', text: t('citizen.pending') },
      in_progress: { color: 'blue', text: t('citizen.inProgress') },
      resolved: { color: 'green', text: t('citizen.resolved') },
      rejected: { color: 'red', text: 'Rejected' },
    };
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    return <Badge color={config.color} text={config.text} />;
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      low: '#52c41a',
      medium: '#faad14',
      high: '#f5222d',
      urgent: '#722ed1',
    };
    return colors[priority as keyof typeof colors] || colors.medium;
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>{t('overview')}</Title>
        <Text type="secondary">{t('welcome', { name: 'User' })}</Text>
      </div>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card">
            <Statistic
              title={t('citizen.totalComplaints')}
              value={data.stats.totalComplaints}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card">
            <Statistic
              title={t('citizen.pending')}
              value={data.stats.pendingComplaints}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card">
            <Statistic
              title={t('citizen.resolved')}
              value={data.stats.resolvedComplaints}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card">
            <Statistic
              title={t('resolutionRate')}
              value={data.stats.resolutionRate}
              suffix="%"
              prefix={<ArrowUpOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Progress Indicators */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} md={12}>
          <Card title={t('performanceMetrics')}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text>{t('resolutionRate')}</Text>
                <Progress
                  percent={data.stats.resolutionRate}
                  status="active"
                  strokeColor="#52c41a"
                />
              </div>
              <div>
                <Text>{t('averageResolutionTime')}: {data.stats.avgResolutionTime} {t('timeframe.today')}</Text>
                <Progress
                  percent={75}
                  status="active"
                  strokeColor="#1890ff"
                />
              </div>
              <div>
                <Text>{t('satisfactionScore')}: {data.stats.satisfactionScore}/5.0</Text>
                <Progress
                  percent={(data.stats.satisfactionScore / 5) * 100}
                  status="active"
                  strokeColor="#faad14"
                />
              </div>
            </Space>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title={t('complaintsByCategory')}>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={data.categoryDistribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }: { name: string; percent: number }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {data.categoryDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Charts and Recent Activity */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <Card title={t('trendingIssues')} extra={<Button type="link">{t('citizen.viewMyComplaints')}</Button>}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="complaints"
                  stroke="#1890ff"
                  strokeWidth={2}
                  name={t('citizen.totalComplaints')}
                />
                <Line
                  type="monotone"
                  dataKey="resolved"
                  stroke="#52c41a"
                  strokeWidth={2}
                  name={t('citizen.resolved')}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card
            title={t('recentComplaints')}
            extra={<Button type="link">{t('recentActivity')}</Button>}
          >
            <List
              dataSource={data.recentComplaints}
              renderItem={(item: any) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <div
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          backgroundColor: getPriorityColor(item.priority),
                        }}
                      />
                    }
                    title={
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Text strong>{item.title}</Text>
                        {getStatusBadge(item.status)}
                      </div>
                    }
                    description={
                      <Space>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {item.time}
                        </Text>
                        <Text
                          style={{
                            fontSize: '12px',
                            color: getPriorityColor(item.priority),
                            textTransform: 'capitalize',
                          }}
                        >
                          {item.priority}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
