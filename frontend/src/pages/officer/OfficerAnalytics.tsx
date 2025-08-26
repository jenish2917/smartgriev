import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Statistic,
  Select,
  DatePicker,
  Space,
  Button,
  Table,
  Tag,
  Progress,
  Alert,
  Tabs,
} from 'antd';
import {
  BarChartOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  TrophyOutlined,
  TeamOutlined,
  DownloadOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { Line, Column, Pie, Area } from '@ant-design/plots';
import type { ColumnsType } from 'antd/es/table';
import type { TabsProps } from 'antd/es/tabs';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

interface DepartmentMetric {
  period: string;
  complaints_received: number;
  complaints_resolved: number;
  avg_resolution_time: number;
  satisfaction_score: number;
  efficiency_rate: number;
}

interface CategoryBreakdown {
  category: string;
  count: number;
  avg_resolution_time: number;
  satisfaction: number;
}

interface TeamPerformance {
  officer_name: string;
  assigned: number;
  completed: number;
  avg_time: number;
  satisfaction: number;
  efficiency: number;
}

const OfficerAnalytics: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('30d');
  const [departmentMetrics, setDepartmentMetrics] = useState<DepartmentMetric[]>([]);
  const [categoryData, setCategoryData] = useState<CategoryBreakdown[]>([]);
  const [teamData, setTeamData] = useState<TeamPerformance[]>([]);

  // Mock data
  const mockMetrics: DepartmentMetric[] = [
    {
      period: 'Week 1',
      complaints_received: 45,
      complaints_resolved: 38,
      avg_resolution_time: 18.5,
      satisfaction_score: 4.2,
      efficiency_rate: 84.4,
    },
    {
      period: 'Week 2',
      complaints_received: 52,
      complaints_resolved: 47,
      avg_resolution_time: 16.8,
      satisfaction_score: 4.5,
      efficiency_rate: 90.4,
    },
    {
      period: 'Week 3',
      complaints_received: 38,
      complaints_resolved: 35,
      avg_resolution_time: 20.2,
      satisfaction_score: 4.1,
      efficiency_rate: 92.1,
    },
    {
      period: 'Week 4',
      complaints_received: 49,
      complaints_resolved: 44,
      avg_resolution_time: 15.5,
      satisfaction_score: 4.7,
      efficiency_rate: 89.8,
    },
  ];

  const mockCategoryData: CategoryBreakdown[] = [
    {
      category: 'Infrastructure',
      count: 65,
      avg_resolution_time: 24.5,
      satisfaction: 4.2,
    },
    {
      category: 'Utilities',
      count: 43,
      avg_resolution_time: 18.2,
      satisfaction: 4.5,
    },
    {
      category: 'Sanitation',
      count: 38,
      avg_resolution_time: 12.8,
      satisfaction: 4.1,
    },
    {
      category: 'Security',
      count: 22,
      avg_resolution_time: 8.5,
      satisfaction: 4.8,
    },
    {
      category: 'Transportation',
      count: 16,
      avg_resolution_time: 32.1,
      satisfaction: 3.9,
    },
  ];

  const mockTeamData: TeamPerformance[] = [
    {
      officer_name: 'Rajesh Kumar',
      assigned: 45,
      completed: 42,
      avg_time: 16.5,
      satisfaction: 4.6,
      efficiency: 93.3,
    },
    {
      officer_name: 'Priya Sharma',
      assigned: 38,
      completed: 35,
      avg_time: 18.2,
      satisfaction: 4.4,
      efficiency: 92.1,
    },
    {
      officer_name: 'Amit Patel',
      assigned: 52,
      completed: 46,
      avg_time: 20.8,
      satisfaction: 4.2,
      efficiency: 88.5,
    },
    {
      officer_name: 'Sunita Verma',
      assigned: 29,
      completed: 28,
      avg_time: 14.3,
      satisfaction: 4.8,
      efficiency: 96.6,
    },
  ];

  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setDepartmentMetrics(mockMetrics);
      setCategoryData(mockCategoryData);
      setTeamData(mockTeamData);
      setLoading(false);
    }, 1000);
  }, [timeRange]);

  // Chart configurations
  const resolutionTrendConfig = {
    data: departmentMetrics,
    xField: 'period',
    yField: 'complaints_resolved',
    color: '#52c41a',
    point: {
      size: 5,
      shape: 'diamond',
    },
  };

  const satisfactionTrendConfig = {
    data: departmentMetrics,
    xField: 'period',
    yField: 'satisfaction_score',
    color: '#1890ff',
    point: {
      size: 5,
      shape: 'circle',
    },
  };

  const categoryPieConfig = {
    data: categoryData,
    angleField: 'count',
    colorField: 'category',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name}: {percentage}',
    },
  };

  const efficiencyColumnConfig = {
    data: teamData,
    xField: 'officer_name',
    yField: 'efficiency',
    color: '#FF6600',
    label: {
      position: 'middle' as const,
      style: {
        fill: '#FFFFFF',
        opacity: 0.8,
      },
    },
  };

  const teamColumns: ColumnsType<TeamPerformance> = [
    {
      title: 'Officer Name',
      dataIndex: 'officer_name',
      key: 'officer_name',
      render: (name) => <Text strong>{name}</Text>,
    },
    {
      title: 'Assigned',
      dataIndex: 'assigned',
      key: 'assigned',
      align: 'center',
    },
    {
      title: 'Completed',
      dataIndex: 'completed',
      key: 'completed',
      align: 'center',
      render: (completed, record) => (
        <Space direction="vertical" size={0}>
          <Text>{completed}</Text>
          <Text type="secondary" style={{ fontSize: 11 }}>
            {((completed / record.assigned) * 100).toFixed(1)}%
          </Text>
        </Space>
      ),
    },
    {
      title: 'Avg Time (hrs)',
      dataIndex: 'avg_time',
      key: 'avg_time',
      align: 'center',
      render: (time) => `${time}h`,
    },
    {
      title: 'Satisfaction',
      dataIndex: 'satisfaction',
      key: 'satisfaction',
      align: 'center',
      render: (score) => (
        <Space>
          <Text>{score.toFixed(1)}</Text>
          <Progress
            type="circle"
            size={30}
            percent={(score / 5) * 100}
            format={() => ''}
            strokeColor={score >= 4.5 ? '#52c41a' : score >= 4.0 ? '#faad14' : '#ff4d4f'}
          />
        </Space>
      ),
    },
    {
      title: 'Efficiency',
      dataIndex: 'efficiency',
      key: 'efficiency',
      align: 'center',
      render: (efficiency) => (
        <Progress
          percent={efficiency}
          size="small"
          strokeColor={efficiency >= 90 ? '#52c41a' : efficiency >= 80 ? '#faad14' : '#ff4d4f'}
        />
      ),
    },
    {
      title: 'Performance',
      key: 'performance',
      align: 'center',
      render: (_, record) => {
        const performanceScore = (
          (record.efficiency * 0.4) +
          ((record.satisfaction / 5) * 100 * 0.3) +
          ((record.completed / record.assigned) * 100 * 0.3)
        );
        
        let color = '#52c41a';
        let text = 'Excellent';
        
        if (performanceScore < 70) {
          color = '#ff4d4f';
          text = 'Needs Improvement';
        } else if (performanceScore < 85) {
          color = '#faad14';
          text = 'Good';
        }
        
        return <Tag color={color}>{text}</Tag>;
      },
    },
  ];

  const categoryColumns: ColumnsType<CategoryBreakdown> = [
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      render: (category) => <Text strong>{category}</Text>,
    },
    {
      title: 'Total Complaints',
      dataIndex: 'count',
      key: 'count',
      align: 'center',
    },
    {
      title: 'Avg Resolution Time',
      dataIndex: 'avg_resolution_time',
      key: 'avg_resolution_time',
      align: 'center',
      render: (time) => `${time}h`,
    },
    {
      title: 'Satisfaction Score',
      dataIndex: 'satisfaction',
      key: 'satisfaction',
      align: 'center',
      render: (score) => (
        <Space>
          <Text>{score.toFixed(1)}/5</Text>
          <Progress
            type="circle"
            size={25}
            percent={(score / 5) * 100}
            format={() => ''}
            strokeColor={score >= 4.5 ? '#52c41a' : score >= 4.0 ? '#faad14' : '#ff4d4f'}
          />
        </Space>
      ),
    },
  ];

  // Calculate summary statistics
  const totalAssigned = teamData.reduce((sum, officer) => sum + officer.assigned, 0);
  const totalCompleted = teamData.reduce((sum, officer) => sum + officer.completed, 0);
  const avgSatisfaction = teamData.reduce((sum, officer) => sum + officer.satisfaction, 0) / teamData.length;
  const departmentEfficiency = (totalCompleted / totalAssigned) * 100;

  const tabItems: TabsProps['items'] = [
    {
      key: 'overview',
      label: 'Department Overview',
      children: (
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Card title="Resolution Trend" bordered={false}>
              <Line {...resolutionTrendConfig} />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Satisfaction Trend" bordered={false}>
              <Line {...satisfactionTrendConfig} />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Category Distribution" bordered={false}>
              <Pie {...categoryPieConfig} />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Category Performance" bordered={false}>
              <Table
                columns={categoryColumns}
                dataSource={categoryData}
                rowKey="category"
                pagination={false}
                size="small"
              />
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: 'team',
      label: 'Team Performance',
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Officer Efficiency Comparison" bordered={false}>
              <Column {...efficiencyColumnConfig} />
            </Card>
          </Col>
          <Col span={24}>
            <Card title="Detailed Team Performance" bordered={false}>
              <Table
                columns={teamColumns}
                dataSource={teamData}
                rowKey="officer_name"
                pagination={false}
              />
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: 'insights',
      label: 'Insights & Recommendations',
      children: (
        <Space direction="vertical" style={{ width: '100%' }}>
          <Alert
            message="Performance Insights"
            description="Based on current data analysis"
            type="info"
            showIcon
          />
          
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card title="Strengths" bordered={false}>
                <ul>
                  <li>High overall satisfaction score (4.5/5)</li>
                  <li>Consistent resolution rates</li>
                  <li>Efficient team collaboration</li>
                  <li>Quick response to urgent complaints</li>
                </ul>
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card title="Areas for Improvement" bordered={false}>
                <ul>
                  <li>Transportation category needs attention</li>
                  <li>Weekend response times can be improved</li>
                  <li>Need more resources for infrastructure issues</li>
                  <li>Officer training on new technologies</li>
                </ul>
              </Card>
            </Col>
          </Row>

          <Card title="Recommendations" bordered={false}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>1. Resource Allocation</Text>
              <Text>Consider assigning additional resources to transportation and infrastructure categories which show longer resolution times.</Text>
              
              <Text strong>2. Training Programs</Text>
              <Text>Implement specialized training for officers handling complex infrastructure complaints.</Text>
              
              <Text strong>3. Process Optimization</Text>
              <Text>Review and optimize workflows for categories with below-average satisfaction scores.</Text>
              
              <Text strong>4. Performance Recognition</Text>
              <Text>Recognize top-performing officers and share best practices across the team.</Text>
            </Space>
          </Card>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={2} className="gov-title">
          Department Analytics
        </Title>
        <Text className="gov-subtitle">
          Comprehensive performance analysis and insights for your department
        </Text>
      </div>

      {/* Controls */}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Text strong>Time Period:</Text>
              <Select
                value={timeRange}
                onChange={setTimeRange}
                style={{ width: 120 }}
              >
                <Select.Option value="7d">Last 7 days</Select.Option>
                <Select.Option value="30d">Last 30 days</Select.Option>
                <Select.Option value="90d">Last 3 months</Select.Option>
                <Select.Option value="1y">Last year</Select.Option>
              </Select>
              <RangePicker />
            </Space>
          </Col>
          <Col>
            <Space>
              <Button icon={<DownloadOutlined />}>
                Export Report
              </Button>
              <Button type="primary" icon={<BarChartOutlined />}>
                Generate Dashboard
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Assigned"
              value={totalAssigned}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Completed"
              value={totalCompleted}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Department Efficiency"
              value={departmentEfficiency}
              precision={1}
              suffix="%"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Avg Satisfaction"
              value={avgSatisfaction}
              precision={1}
              suffix="/5"
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#13c2c2' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Main Analytics */}
      <Card>
        <Tabs
          defaultActiveKey="overview"
          items={tabItems}
        />
      </Card>
    </div>
  );
};

export default OfficerAnalytics;
