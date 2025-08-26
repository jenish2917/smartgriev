import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Statistic,
  Table,
  Tag,
  Space,
  Button,
  Select,
  DatePicker,
  Alert,
  Tabs,
  Progress,
  List,
  Avatar,
} from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  UserOutlined,
  TrophyOutlined,
  TeamOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { Column, Line, Pie } from '@ant-design/plots';
import type { ColumnsType, TabsProps } from 'antd/es/table';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

interface Assignment {
  id: string;
  complaint_id: string;
  complaint_title: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'in_progress' | 'resolved' | 'rejected';
  assigned_at: string;
  due_date: string;
  category: string;
  user_name: string;
  location: string;
  progress: number;
}

interface OfficerStats {
  total_assigned: number;
  completed: number;
  in_progress: number;
  pending: number;
  avg_resolution_time: number;
  satisfaction_score: number;
  this_month_completed: number;
  last_month_completed: number;
}

const OfficerDashboard: React.FC = () => {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [stats, setStats] = useState<OfficerStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');

  // Mock data
  const mockAssignments: Assignment[] = [
    {
      id: 'ASG-001',
      complaint_id: 'CMP-2024-001',
      complaint_title: 'Street Light Not Working - MG Road',
      priority: 'high',
      status: 'in_progress',
      assigned_at: '2024-01-15T10:00:00Z',
      due_date: '2024-01-17T23:59:59Z',
      category: 'Infrastructure',
      user_name: 'Rahul Sharma',
      location: 'MG Road, Sector 15',
      progress: 65,
    },
    {
      id: 'ASG-002',
      complaint_id: 'CMP-2024-002',
      complaint_title: 'Water Supply Disruption',
      priority: 'urgent',
      status: 'pending',
      assigned_at: '2024-01-16T08:30:00Z',
      due_date: '2024-01-16T18:00:00Z',
      category: 'Utilities',
      user_name: 'Priya Patel',
      location: 'Nehru Colony, Block A',
      progress: 10,
    },
    {
      id: 'ASG-003',
      complaint_id: 'CMP-2024-003',
      complaint_title: 'Garbage Collection Missed',
      priority: 'medium',
      status: 'resolved',
      assigned_at: '2024-01-14T14:20:00Z',
      due_date: '2024-01-16T23:59:59Z',
      category: 'Sanitation',
      user_name: 'Amit Kumar',
      location: 'Green Park Extension',
      progress: 100,
    },
  ];

  const mockStats: OfficerStats = {
    total_assigned: 45,
    completed: 38,
    in_progress: 5,
    pending: 2,
    avg_resolution_time: 18.5,
    satisfaction_score: 4.6,
    this_month_completed: 12,
    last_month_completed: 15,
  };

  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setAssignments(mockAssignments);
      setStats(mockStats);
      setLoading(false);
    }, 1000);
  }, []);

  const statusColors = {
    pending: 'orange',
    in_progress: 'blue',
    resolved: 'green',
    rejected: 'red',
  };

  const priorityColors = {
    low: 'default',
    medium: 'warning',
    high: 'error',
    urgent: 'error',
  };

  const columns: ColumnsType<Assignment> = [
    {
      title: 'Complaint Details',
      key: 'complaint',
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Text strong style={{ color: '#1890ff' }}>
            {record.complaint_id}
          </Text>
          <Text ellipsis style={{ maxWidth: 300 }}>
            {record.complaint_title}
          </Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            By: {record.user_name}
          </Text>
        </Space>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 120,
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority) => (
        <Tag color={priorityColors[priority as keyof typeof priorityColors]}>
          {priority.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
        <Tag color={statusColors[status as keyof typeof statusColors]}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      width: 120,
      render: (progress) => (
        <Progress 
          percent={progress} 
          size="small" 
          strokeColor={progress === 100 ? '#52c41a' : progress > 50 ? '#1890ff' : '#faad14'} 
        />
      ),
    },
    {
      title: 'Due Date',
      dataIndex: 'due_date',
      key: 'due_date',
      width: 120,
      render: (date) => {
        const dueDate = new Date(date);
        const now = new Date();
        const isOverdue = dueDate < now;
        return (
          <Text style={{ color: isOverdue ? '#f5222d' : '#000' }}>
            {dueDate.toLocaleDateString()}
            {isOverdue && <Text type="danger"> (Overdue)</Text>}
          </Text>
        );
      },
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
      ellipsis: true,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button type="primary" size="small">
            Update
          </Button>
          <Button size="small">
            View
          </Button>
        </Space>
      ),
    },
  ];

  const filteredAssignments = assignments.filter(assignment => {
    const statusMatch = filterStatus === 'all' || assignment.status === filterStatus;
    const priorityMatch = filterPriority === 'all' || assignment.priority === filterPriority;
    return statusMatch && priorityMatch;
  });

  // Chart data
  const statusData = [
    { status: 'Completed', count: stats?.completed || 0 },
    { status: 'In Progress', count: stats?.in_progress || 0 },
    { status: 'Pending', count: stats?.pending || 0 },
  ];

  const performanceData = [
    { month: 'Dec', completed: stats?.last_month_completed || 0 },
    { month: 'Jan', completed: stats?.this_month_completed || 0 },
  ];

  const pieConfig = {
    data: statusData,
    angleField: 'count',
    colorField: 'status',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name} ({percentage})',
    },
    color: ['#52c41a', '#1890ff', '#faad14'],
  };

  const columnConfig = {
    data: performanceData,
    xField: 'month',
    yField: 'completed',
    color: '#FF6600',
    label: {
      position: 'middle' as const,
      style: {
        fill: '#FFFFFF',
        opacity: 0.8,
      },
    },
  };

  const tabItems: TabsProps['items'] = [
    {
      key: 'assignments',
      label: `Assignments (${filteredAssignments.length})`,
      children: (
        <div>
          <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
            <Col>
              <Space>
                <Text strong>Filter by:</Text>
                <Select
                  value={filterStatus}
                  onChange={setFilterStatus}
                  style={{ width: 120 }}
                >
                  <Select.Option value="all">All Status</Select.Option>
                  <Select.Option value="pending">Pending</Select.Option>
                  <Select.Option value="in_progress">In Progress</Select.Option>
                  <Select.Option value="resolved">Resolved</Select.Option>
                </Select>
                <Select
                  value={filterPriority}
                  onChange={setFilterPriority}
                  style={{ width: 120 }}
                >
                  <Select.Option value="all">All Priority</Select.Option>
                  <Select.Option value="urgent">Urgent</Select.Option>
                  <Select.Option value="high">High</Select.Option>
                  <Select.Option value="medium">Medium</Select.Option>
                  <Select.Option value="low">Low</Select.Option>
                </Select>
              </Space>
            </Col>
            <Col>
              <Button type="primary">
                Update Status
              </Button>
            </Col>
          </Row>
          
          <Table
            columns={columns}
            dataSource={filteredAssignments}
            rowKey="id"
            loading={loading}
            pagination={{ pageSize: 10 }}
            scroll={{ x: 1200 }}
          />
        </div>
      ),
    },
    {
      key: 'performance',
      label: 'Performance',
      children: (
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Card title="Status Distribution" bordered={false}>
              <Pie {...pieConfig} />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Monthly Performance" bordered={false}>
              <Column {...columnConfig} />
            </Card>
          </Col>
        </Row>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={2} className="gov-title">
          Officer Dashboard
        </Title>
        <Text className="gov-subtitle">
          Manage your assigned complaints and track department performance
        </Text>
      </div>

      {/* Alert for urgent items */}
      {assignments.filter(a => a.priority === 'urgent' && a.status !== 'resolved').length > 0 && (
        <Alert
          message="Urgent Complaints Require Attention"
          description={`You have ${assignments.filter(a => a.priority === 'urgent' && a.status !== 'resolved').length} urgent complaints that need immediate action.`}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
          action={
            <Button size="small" danger>
              View Urgent
            </Button>
          }
        />
      )}

      {/* Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Assigned"
              value={stats?.total_assigned || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Completed"
              value={stats?.completed || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Avg Resolution Time"
              value={stats?.avg_resolution_time || 0}
              suffix="hours"
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Satisfaction Score"
              value={stats?.satisfaction_score || 0}
              suffix="/ 5"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#13c2c2' }}
              precision={1}
            />
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Text strong>Quick Actions:</Text>
          </Col>
          <Col>
            <Space>
              <Button type="primary" icon={<DashboardOutlined />}>
                Bulk Update
              </Button>
              <Button icon={<UserOutlined />}>
                Contact Citizens
              </Button>
              <Button icon={<BarChartOutlined />}>
                Generate Report
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Main Content */}
      <Card>
        <Tabs
          defaultActiveKey="assignments"
          items={tabItems}
        />
      </Card>
    </div>
  );
};

export default OfficerDashboard;
