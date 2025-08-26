import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Progress,
  Table,
  Tag,
  Space,
  Button,
  Select,
  DatePicker,
  Alert,
  Tooltip,
} from 'antd';
import {
  DashboardOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  TeamOutlined,
  RiseOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import { Line, Column, Pie } from '@ant-design/plots';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

interface PerformanceMetric {
  id: string;
  metric_name: string;
  metric_value: number;
  timestamp: string;
  server_node?: string;
  metadata: Record<string, any>;
}

interface SystemAlert {
  id: string;
  rule_name: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  is_resolved: boolean;
  triggered_at: string;
}

const PerformanceMetrics: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('24h');

  // Mock performance data
  const responseTimeData = [
    { time: '00:00', value: 120 },
    { time: '04:00', value: 98 },
    { time: '08:00', value: 250 },
    { time: '12:00', value: 180 },
    { time: '16:00', value: 320 },
    { time: '20:00', value: 200 },
  ];

  const systemHealthData = [
    { category: 'CPU Usage', value: 65, status: 'normal' },
    { category: 'Memory Usage', value: 78, status: 'warning' },
    { category: 'Disk Usage', value: 45, status: 'normal' },
    { category: 'Network I/O', value: 89, status: 'critical' },
  ];

  const departmentPerformance = [
    { department: 'Water Board', avg_response: 24, resolution_rate: 85 },
    { department: 'Electricity', avg_response: 18, resolution_rate: 92 },
    { department: 'PWD', avg_response: 36, resolution_rate: 78 },
    { department: 'Health', avg_response: 12, resolution_rate: 95 },
  ];

  const alertColumns: ColumnsType<SystemAlert> = [
    {
      title: 'Rule',
      dataIndex: 'rule_name',
      key: 'rule_name',
    },
    {
      title: 'Message',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      render: (severity) => {
        const colors = {
          low: 'blue',
          medium: 'orange',
          high: 'red',
          critical: 'red',
        };
        return <Tag color={colors[severity as keyof typeof colors]}>{severity.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Status',
      dataIndex: 'is_resolved',
      key: 'is_resolved',
      render: (resolved) => (
        <Tag color={resolved ? 'green' : 'red'}>
          {resolved ? 'RESOLVED' : 'ACTIVE'}
        </Tag>
      ),
    },
    {
      title: 'Triggered',
      dataIndex: 'triggered_at',
      key: 'triggered_at',
      render: (date) => new Date(date).toLocaleString(),
    },
  ];

  const mockAlerts: SystemAlert[] = [
    {
      id: '1',
      rule_name: 'High Response Time',
      message: 'Average response time exceeded 300ms threshold',
      severity: 'high',
      is_resolved: false,
      triggered_at: '2024-01-16T10:30:00Z',
    },
    {
      id: '2',
      rule_name: 'Memory Usage Alert',
      message: 'Memory usage above 80% for 10 minutes',
      severity: 'medium',
      is_resolved: true,
      triggered_at: '2024-01-16T09:15:00Z',
    },
  ];

  useEffect(() => {
    setLoading(true);
    // Simulate API calls
    setTimeout(() => {
      setAlerts(mockAlerts);
      setLoading(false);
    }, 1000);
  }, [timeRange]);

  const getHealthColor = (value: number) => {
    if (value < 50) return '#52c41a';
    if (value < 80) return '#faad14';
    return '#f5222d';
  };

  const lineConfig = {
    data: responseTimeData,
    xField: 'time',
    yField: 'value',
    point: {
      size: 5,
      shape: 'diamond',
    },
    color: '#1890ff',
    label: {
      style: {
        fill: '#aaa',
      },
    },
  };

  const columnConfig = {
    data: departmentPerformance,
    xField: 'department',
    yField: 'resolution_rate',
    color: '#FF6600',
    label: {
      position: 'middle' as const,
      style: {
        fill: '#FFFFFF',
        opacity: 0.6,
      },
    },
  };

  return (
    <div>
      <div className="page-header">
        <Title level={2} className="gov-title">
          Performance Metrics & System Health
        </Title>
        <Text className="gov-subtitle">
          Real-time monitoring and performance analytics for the grievance system
        </Text>
      </div>

      {/* Controls */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Space>
            <Text strong>Time Range:</Text>
            <Select
              value={timeRange}
              onChange={setTimeRange}
              style={{ width: 120 }}
            >
              <Select.Option value="1h">Last Hour</Select.Option>
              <Select.Option value="24h">Last 24h</Select.Option>
              <Select.Option value="7d">Last 7 days</Select.Option>
              <Select.Option value="30d">Last 30 days</Select.Option>
            </Select>
          </Space>
        </Col>
        <Col>
          <Button type="primary" icon={<DashboardOutlined />}>
            Export Report
          </Button>
        </Col>
      </Row>

      {/* Key Metrics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Avg Response Time"
              value={186}
              suffix="ms"
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="System Uptime"
              value={99.9}
              suffix="%"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Active Users"
              value={1284}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Throughput"
              value={45.6}
              suffix="req/s"
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#13c2c2' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {/* Response Time Chart */}
        <Col xs={24} lg={12}>
          <Card title="Response Time Trend" bordered={false}>
            <Line {...lineConfig} />
          </Card>
        </Col>

        {/* System Health */}
        <Col xs={24} lg={12}>
          <Card title="System Health" bordered={false}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {systemHealthData.map((item, index) => (
                <div key={index}>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Text>{item.category}</Text>
                    </Col>
                    <Col>
                      <Text style={{ color: getHealthColor(item.value) }}>
                        {item.value}%
                      </Text>
                    </Col>
                  </Row>
                  <Progress
                    percent={item.value}
                    strokeColor={getHealthColor(item.value)}
                    showInfo={false}
                    size="small"
                  />
                </div>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Department Performance */}
        <Col xs={24} lg={14}>
          <Card title="Department Resolution Rates" bordered={false}>
            <Column {...columnConfig} />
          </Card>
        </Col>

        {/* Active Alerts */}
        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <WarningOutlined style={{ color: '#f5222d' }} />
                System Alerts
              </Space>
            }
            bordered={false}
          >
            <Alert
              message="2 active alerts require attention"
              type="warning"
              style={{ marginBottom: 16 }}
              showIcon
            />
            <Table
              columns={alertColumns}
              dataSource={alerts}
              rowKey="id"
              loading={loading}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default PerformanceMetrics;
