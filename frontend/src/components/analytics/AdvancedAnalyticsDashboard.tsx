// Advanced Analytics Dashboard for SmartGriev
// Provides comprehensive system analytics and insights

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Select,
  DatePicker,
  Table,
  Progress,
  Tag,
  Space,
  Typography,
  Alert,
  Spin,
  Tooltip,
} from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  FileTextOutlined,
  UserOutlined,
  BankOutlined,
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { apiService } from '@/services/api';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface AnalyticsData {
  overview: {
    totalComplaints: number;
    pendingComplaints: number;
    resolvedComplaints: number;
    averageResolutionTime: number;
    userSatisfactionRate: number;
    monthlyGrowth: number;
  };
  trends: {
    date: string;
    complaints: number;
    resolved: number;
    pending: number;
  }[];
  departmentStats: {
    department: string;
    complaints: number;
    resolved: number;
    avgResolution: number;
    satisfaction: number;
  }[];
  complaintTypes: {
    type: string;
    count: number;
    percentage: number;
  }[];
  geographicData: {
    state: string;
    complaints: number;
    resolved: number;
  }[];
  performanceMetrics: {
    apiResponseTime: number;
    systemUptime: number;
    errorRate: number;
    activeUsers: number;
  };
}

const AdvancedAnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(30, 'days'),
    dayjs(),
  ]);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');

  useEffect(() => {
    fetchAnalyticsData();
  }, [dateRange, selectedDepartment]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/analytics/dashboard/', {
        params: {
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
          department: selectedDepartment !== 'all' ? selectedDepartment : undefined,
        },
      });
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>Loading analytics...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <Alert
        message="No Data Available"
        description="Unable to load analytics data. Please try again later."
        type="warning"
        showIcon
      />
    );
  }

  const { overview, trends, departmentStats, complaintTypes, geographicData, performanceMetrics } = data;

  // Color schemes for charts
  const COLORS = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#fa8c16'];
  const DEPARTMENT_COLORS = ['#001529', '#1890ff', '#52c41a', '#faad14', '#f5222d'];

  const departmentColumns = [
    {
      title: 'Department',
      dataIndex: 'department',
      key: 'department',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Total Complaints',
      dataIndex: 'complaints',
      key: 'complaints',
      sorter: (a: any, b: any) => a.complaints - b.complaints,
    },
    {
      title: 'Resolved',
      dataIndex: 'resolved',
      key: 'resolved',
      render: (resolved: number, record: any) => (
        <Space>
          <Text>{resolved}</Text>
          <Progress
            percent={Math.round((resolved / record.complaints) * 100)}
            size="small"
            status={resolved / record.complaints > 0.8 ? 'success' : 'normal'}
          />
        </Space>
      ),
    },
    {
      title: 'Avg Resolution (Days)',
      dataIndex: 'avgResolution',
      key: 'avgResolution',
      render: (days: number) => (
        <Tag color={days <= 7 ? 'green' : days <= 15 ? 'orange' : 'red'}>
          {days.toFixed(1)} days
        </Tag>
      ),
    },
    {
      title: 'Satisfaction',
      dataIndex: 'satisfaction',
      key: 'satisfaction',
      render: (rate: number) => (
        <Progress
          percent={Math.round(rate)}
          size="small"
          status={rate >= 80 ? 'success' : rate >= 60 ? 'normal' : 'exception'}
        />
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <Row justify="space-between" align="middle" style={{ marginBottom: '24px' }}>
        <Col>
          <Title level={2}>Analytics Dashboard</Title>
          <Text type="secondary">Comprehensive insights into SmartGriev system performance</Text>
        </Col>
        <Col>
          <Space>
            <Select
              value={selectedDepartment}
              onChange={setSelectedDepartment}
              style={{ width: 200 }}
            >
              <Option value="all">All Departments</Option>
              {departmentStats.map(dept => (
                <Option key={dept.department} value={dept.department}>
                  {dept.department}
                </Option>
              ))}
            </Select>
            <RangePicker
              value={dateRange}
              onChange={(dates) => dates && setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
              format="YYYY-MM-DD"
            />
          </Space>
        </Col>
      </Row>

      {/* Overview Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Complaints"
              value={overview.totalComplaints}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Pending"
              value={overview.pendingComplaints}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Resolved"
              value={overview.resolvedComplaints}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Satisfaction Rate"
              value={overview.userSatisfactionRate}
              suffix="%"
              prefix={
                overview.userSatisfactionRate >= 80 ? (
                  <ArrowUpOutlined style={{ color: '#52c41a' }} />
                ) : (
                  <ArrowDownOutlined style={{ color: '#f5222d' }} />
                )
              }
              valueStyle={{
                color: overview.userSatisfactionRate >= 80 ? '#52c41a' : '#f5222d',
              }}
            />
          </Card>
        </Col>
      </Row>

      {/* Performance Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={6}>
          <Card title="System Performance" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text type="secondary">API Response Time</Text>
                <div>
                  <Text strong>{performanceMetrics.apiResponseTime}ms</Text>
                  <Progress
                    percent={Math.min(100, (200 - performanceMetrics.apiResponseTime) / 2)}
                    size="small"
                    showInfo={false}
                    status={performanceMetrics.apiResponseTime <= 100 ? 'success' : 'normal'}
                  />
                </div>
              </div>
              <div>
                <Text type="secondary">System Uptime</Text>
                <div>
                  <Text strong>{performanceMetrics.systemUptime}%</Text>
                  <Progress
                    percent={performanceMetrics.systemUptime}
                    size="small"
                    showInfo={false}
                    status={performanceMetrics.systemUptime >= 99 ? 'success' : 'normal'}
                  />
                </div>
              </div>
              <div>
                <Text type="secondary">Error Rate</Text>
                <div>
                  <Text strong>{performanceMetrics.errorRate}%</Text>
                  <Progress
                    percent={100 - performanceMetrics.errorRate * 10}
                    size="small"
                    showInfo={false}
                    status={performanceMetrics.errorRate <= 1 ? 'success' : 'exception'}
                  />
                </div>
              </div>
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={18}>
          <Card title="Complaint Trends" size="small">
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="complaints"
                  stackId="1"
                  stroke="#1890ff"
                  fill="#1890ff"
                  fillOpacity={0.6}
                  name="Total Complaints"
                />
                <Area
                  type="monotone"
                  dataKey="resolved"
                  stackId="2"
                  stroke="#52c41a"
                  fill="#52c41a"
                  fillOpacity={0.6}
                  name="Resolved"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Charts Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="Complaint Types Distribution" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={complaintTypes}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ type, percentage }) => `${type} (${percentage}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {complaintTypes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Geographic Distribution" size="small">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={geographicData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="state" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Bar dataKey="complaints" fill="#1890ff" name="Total Complaints" />
                <Bar dataKey="resolved" fill="#52c41a" name="Resolved" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Department Performance Table */}
      <Card title="Department Performance" size="small">
        <Table
          columns={departmentColumns}
          dataSource={departmentStats}
          rowKey="department"
          pagination={{ pageSize: 10 }}
          size="small"
        />
      </Card>
    </div>
  );
};

export default AdvancedAnalyticsDashboard;