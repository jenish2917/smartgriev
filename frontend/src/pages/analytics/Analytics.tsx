import React, { useState, useEffect } from 'react';
import {
  Row,
  Col,
  Card,
  Typography,
  Space,
  Select,
  DatePicker,
  Button,
  Statistic,
  Progress,
  Tabs,
} from 'antd';
import {
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  DownloadOutlined,
  FileExcelOutlined,
  FilePdfOutlined,
} from '@ant-design/icons';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { TabsProps } from 'antd';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

// Mock data for analytics
const complaintsByCategory = [
  { name: 'Water Supply', value: 420, percentage: 28 },
  { name: 'Road Maintenance', value: 315, percentage: 21 },
  { name: 'Electricity', value: 280, percentage: 19 },
  { name: 'Waste Management', value: 245, percentage: 16 },
  { name: 'Public Health', value: 190, percentage: 13 },
  { name: 'Others', value: 50, percentage: 3 },
];

const monthlyTrends = [
  { month: 'Jan', complaints: 120, resolved: 110 },
  { month: 'Feb', complaints: 145, resolved: 130 },
  { month: 'Mar', complaints: 180, resolved: 165 },
  { month: 'Apr', complaints: 220, resolved: 200 },
  { month: 'May', complaints: 195, resolved: 185 },
  { month: 'Jun', complaints: 170, resolved: 160 },
];

const resolutionTimes = [
  { category: 'Water Supply', avgTime: 4.2, target: 3.0 },
  { category: 'Road Maintenance', avgTime: 8.5, target: 7.0 },
  { category: 'Electricity', avgTime: 2.8, target: 2.5 },
  { category: 'Waste Management', avgTime: 3.5, target: 3.0 },
];

const COLORS = ['#FF6600', '#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1'];

const Analytics: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('this-month');
  const [selectedRegion, setSelectedRegion] = useState('all');

  useEffect(() => {
    // Simulate API call
    setLoading(true);
    setTimeout(() => setLoading(false), 1000);
  }, [selectedPeriod, selectedRegion]);

  const handleExport = (format: 'excel' | 'pdf') => {
    console.log(`Exporting analytics in ${format} format`);
    // Implement export functionality
  };

  const summaryStats = [
    {
      title: 'Total Complaints',
      value: 1500,
      change: 12,
      trend: 'up',
    },
    {
      title: 'Resolution Rate',
      value: 89.5,
      suffix: '%',
      change: 3.2,
      trend: 'up',
    },
    {
      title: 'Avg Resolution Time',
      value: 4.8,
      suffix: ' days',
      change: -8.5,
      trend: 'down',
    },
    {
      title: 'Satisfaction Score',
      value: 4.2,
      suffix: '/5',
      change: 5.1,
      trend: 'up',
    },
  ];

  const tabItems: TabsProps['items'] = [
    {
      key: 'overview',
      label: 'Overview',
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Complaint Volume Trends" extra={<Button icon={<DownloadOutlined />}>Export</Button>}>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={monthlyTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="complaints" stroke="#FF6600" strokeWidth={2} />
                  <Line type="monotone" dataKey="resolved" stroke="#52c41a" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Complaints by Category">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={complaintsByCategory}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {complaintsByCategory.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Resolution Performance">
              <Space direction="vertical" style={{ width: '100%' }}>
                {resolutionTimes.map((item, index) => (
                  <div key={index}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <Text>{item.category}</Text>
                      <Text>{item.avgTime} days</Text>
                    </div>
                    <Progress
                      percent={(item.target / item.avgTime) * 100}
                      status={item.avgTime <= item.target ? 'success' : 'exception'}
                      showInfo={false}
                    />
                  </div>
                ))}
              </Space>
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: 'trends',
      label: 'Trends Analysis',
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Department Performance Comparison">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={resolutionTimes}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="avgTime" fill="#FF6600" name="Actual Time (days)" />
                  <Bar dataKey="target" fill="#52c41a" name="Target Time (days)" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: 'reports',
      label: 'Reports',
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Generate Reports">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Title level={4}>Export Options</Title>
                  <Space>
                    <Button icon={<FileExcelOutlined />} onClick={() => handleExport('excel')}>
                      Export to Excel
                    </Button>
                    <Button icon={<FilePdfOutlined />} onClick={() => handleExport('pdf')}>
                      Export to PDF
                    </Button>
                  </Space>
                </div>
                <div>
                  <Title level={4}>Automated Reports</Title>
                  <Text>Set up automated weekly and monthly reports to be delivered to stakeholders.</Text>
                </div>
              </Space>
            </Card>
          </Col>
        </Row>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>Analytics & Reports</Title>
        <Text type="secondary">
          Comprehensive analysis of complaint data and department performance metrics
        </Text>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Select
            value={selectedPeriod}
            onChange={setSelectedPeriod}
            style={{ width: '100%' }}
            placeholder="Select Period"
          >
            <Option value="this-week">This Week</Option>
            <Option value="this-month">This Month</Option>
            <Option value="last-quarter">Last Quarter</Option>
            <Option value="this-year">This Year</Option>
            <Option value="custom">Custom Range</Option>
          </Select>
        </Col>
        <Col span={6}>
          <Select
            value={selectedRegion}
            onChange={setSelectedRegion}
            style={{ width: '100%' }}
            placeholder="Select Region"
          >
            <Option value="all">All Regions</Option>
            <Option value="north">North Zone</Option>
            <Option value="south">South Zone</Option>
            <Option value="east">East Zone</Option>
            <Option value="west">West Zone</Option>
          </Select>
        </Col>
        <Col span={8}>
          <RangePicker style={{ width: '100%' }} />
        </Col>
        <Col span={4}>
          <Button type="primary" block>
            Apply Filters
          </Button>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {summaryStats.map((stat, index) => (
          <Col span={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.value}
                suffix={stat.suffix}
                valueStyle={{
                  color: stat.trend === 'up' ? '#3f8600' : stat.trend === 'down' ? '#cf1322' : undefined,
                }}
                prefix={
                  stat.trend === 'up' ? (
                    <span style={{ color: '#3f8600' }}>↗ +{stat.change}%</span>
                  ) : stat.trend === 'down' ? (
                    <span style={{ color: '#cf1322' }}>↘ {stat.change}%</span>
                  ) : null
                }
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Card>
        <Tabs defaultActiveKey="overview" items={tabItems} />
      </Card>
    </div>
  );
};

export default Analytics;
