import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Button, 
  Input, 
  Select, 
  Space, 
  Typography, 
  Row, 
  Col,
  Statistic,
  Progress,
  Avatar,
  Tooltip,
  Alert,
  Badge,
  Divider
} from 'antd';
import { 
  SearchOutlined, 
  FilterOutlined, 
  EyeOutlined,
  DownloadOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SyncOutlined,
  UserOutlined,
  CalendarOutlined,
  EnvironmentOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Search } = Input;

interface Complaint {
  id: string;
  title: string;
  description: string;
  category: string;
  subcategory: string;
  component: string;
  status: 'submitted' | 'in_progress' | 'resolved' | 'closed' | 'rejected';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  severity: 'low' | 'medium' | 'high' | 'critical';
  created_at: string;
  updated_at: string;
  estimated_resolution: string;
  assigned_department: string;
  location?: string;
  citizen_name: string;
  citizen_email: string;
  citizen_phone: string;
  progress_percentage: number;
  attachments_count: number;
  last_update: string;
}

const ComplaintDashboard: React.FC = () => {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  // Mock data - replace with API call
  useEffect(() => {
    const mockData: Complaint[] = [
      {
        id: 'CMP-2024-001',
        title: 'Broken Street Light on MG Road',
        description: 'Street light not working for past 3 days, causing safety issues',
        category: 'Infrastructure',
        subcategory: 'Road Infrastructure',
        component: 'Street Lighting',
        status: 'in_progress',
        priority: 'high',
        severity: 'medium',
        created_at: '2024-01-15T10:30:00Z',
        updated_at: '2024-01-16T14:20:00Z',
        estimated_resolution: '3-5 business days',
        assigned_department: 'Municipal Corporation',
        location: 'MG Road, Sector 15, Delhi',
        citizen_name: 'Rajesh Kumar',
        citizen_email: 'rajesh.kumar@email.com',
        citizen_phone: '+91-9876543210',
        progress_percentage: 65,
        attachments_count: 2,
        last_update: 'Technician assigned, parts ordered'
      },
      {
        id: 'CMP-2024-002',
        title: 'Water Supply Disruption',
        description: 'No water supply in residential area for 2 days',
        category: 'Utilities',
        subcategory: 'Water Supply',
        component: 'Water Distribution',
        status: 'submitted',
        priority: 'urgent',
        severity: 'high',
        created_at: '2024-01-16T08:15:00Z',
        updated_at: '2024-01-16T08:15:00Z',
        estimated_resolution: '1-2 business days',
        assigned_department: 'Water Department',
        location: 'Green Park Extension, Delhi',
        citizen_name: 'Priya Sharma',
        citizen_email: 'priya.sharma@email.com',
        citizen_phone: '+91-9876543211',
        progress_percentage: 10,
        attachments_count: 1,
        last_update: 'Complaint registered, inspection scheduled'
      },
      {
        id: 'CMP-2024-003',
        title: 'Garbage Collection Missed',
        description: 'Garbage not collected for past week in our locality',
        category: 'Utilities',
        subcategory: 'Waste Management',
        component: 'Garbage Collection',
        status: 'resolved',
        priority: 'medium',
        severity: 'low',
        created_at: '2024-01-10T16:45:00Z',
        updated_at: '2024-01-14T11:30:00Z',
        estimated_resolution: '2-3 business days',
        assigned_department: 'Sanitation Department',
        location: 'Lajpat Nagar, Delhi',
        citizen_name: 'Amit Singh',
        citizen_email: 'amit.singh@email.com',
        citizen_phone: '+91-9876543212',
        progress_percentage: 100,
        attachments_count: 0,
        last_update: 'Issue resolved, regular collection resumed'
      }
    ];
    
    setTimeout(() => {
      setComplaints(mockData);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'submitted': return '#1890FF';
      case 'in_progress': return '#FA8C16';
      case 'resolved': return '#52C41A';
      case 'closed': return '#666666';
      case 'rejected': return '#FF4D4F';
      default: return '#1890FF';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'submitted': return <ClockCircleOutlined />;
      case 'in_progress': return <SyncOutlined spin />;
      case 'resolved': return <CheckCircleOutlined />;
      case 'closed': return <CheckCircleOutlined />;
      case 'rejected': return <ExclamationCircleOutlined />;
      default: return <ClockCircleOutlined />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return '#FF4D4F';
      case 'high': return '#FA8C16';
      case 'medium': return '#1890FF';
      case 'low': return '#52C41A';
      default: return '#1890FF';
    }
  };

  const filteredComplaints = complaints.filter(complaint => {
    const matchesSearch = complaint.title.toLowerCase().includes(searchText.toLowerCase()) ||
                         complaint.description.toLowerCase().includes(searchText.toLowerCase()) ||
                         complaint.id.toLowerCase().includes(searchText.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || complaint.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || complaint.priority === priorityFilter;
    const matchesCategory = categoryFilter === 'all' || complaint.category === categoryFilter;
    
    return matchesSearch && matchesStatus && matchesPriority && matchesCategory;
  });

  const getStats = () => {
    const total = complaints.length;
    const submitted = complaints.filter(c => c.status === 'submitted').length;
    const inProgress = complaints.filter(c => c.status === 'in_progress').length;
    const resolved = complaints.filter(c => c.status === 'resolved').length;
    const avgResolutionTime = '3.2 days'; // Mock calculation
    
    return { total, submitted, inProgress, resolved, avgResolutionTime };
  };

  const stats = getStats();

  const columns = [
    {
      title: 'Complaint ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      render: (id: string) => (
        <Text code style={{ fontSize: 12, fontWeight: 'bold' }}>{id}</Text>
      ),
    },
    {
      title: 'Details',
      key: 'details',
      width: 300,
      render: (record: Complaint) => (
        <div>
          <Text strong style={{ display: 'block', marginBottom: 4 }}>
            {record.title}
          </Text>
          <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
            {record.description.length > 80 
              ? `${record.description.substring(0, 80)}...` 
              : record.description}
          </Text>
          <Space size="small">
            <Tag color="blue" style={{ fontSize: 10 }}>{record.category}</Tag>
            <Tag color="cyan" style={{ fontSize: 10 }}>{record.subcategory}</Tag>
          </Space>
        </div>
      ),
    },
    {
      title: 'Citizen',
      key: 'citizen',
      width: 200,
      render: (record: Complaint) => (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
            <Avatar size="small" icon={<UserOutlined />} style={{ marginRight: 8 }} />
            <Text strong style={{ fontSize: 12 }}>{record.citizen_name}</Text>
          </div>
          <Text type="secondary" style={{ fontSize: 11, display: 'block' }}>
            {record.citizen_email}
          </Text>
          <Text type="secondary" style={{ fontSize: 11, display: 'block' }}>
            {record.citizen_phone}
          </Text>
          {record.location && (
            <div style={{ marginTop: 4 }}>
              <EnvironmentOutlined style={{ fontSize: 10, marginRight: 4 }} />
              <Text type="secondary" style={{ fontSize: 10 }}>
                {record.location.length > 30 
                  ? `${record.location.substring(0, 30)}...` 
                  : record.location}
              </Text>
            </div>
          )}
        </div>
      ),
    },
    {
      title: 'Status & Priority',
      key: 'status',
      width: 150,
      render: (record: Complaint) => (
        <div>
          <Tag 
            color={getStatusColor(record.status)} 
            icon={getStatusIcon(record.status)}
            style={{ marginBottom: 8, fontSize: 11, fontWeight: 'bold' }}
          >
            {record.status.replace('_', ' ').toUpperCase()}
          </Tag>
          <br />
          <Tag 
            color={getPriorityColor(record.priority)}
            style={{ fontSize: 10, fontWeight: 'bold' }}
          >
            {record.priority.toUpperCase()}
          </Tag>
          <div style={{ marginTop: 8 }}>
            <Text style={{ fontSize: 10, color: '#666' }}>Progress:</Text>
            <Progress 
              percent={record.progress_percentage} 
              size="small" 
              strokeColor={getStatusColor(record.status)}
              showInfo={false}
            />
            <Text style={{ fontSize: 10 }}>{record.progress_percentage}%</Text>
          </div>
        </div>
      ),
    },
    {
      title: 'Timeline',
      key: 'timeline',
      width: 180,
      render: (record: Complaint) => (
        <div>
          <div style={{ marginBottom: 4 }}>
            <CalendarOutlined style={{ fontSize: 10, marginRight: 4 }} />
            <Text style={{ fontSize: 11 }}>
              Created: {new Date(record.created_at).toLocaleDateString()}
            </Text>
          </div>
          <div style={{ marginBottom: 4 }}>
            <Text style={{ fontSize: 11, color: '#666' }}>
              Updated: {new Date(record.updated_at).toLocaleDateString()}
            </Text>
          </div>
          <div style={{ marginBottom: 4 }}>
            <Text style={{ fontSize: 11, color: '#FA8C16' }}>
              ETA: {record.estimated_resolution}
            </Text>
          </div>
          <Text style={{ fontSize: 10, color: '#666' }}>
            Dept: {record.assigned_department}
          </Text>
        </div>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 120,
      render: (record: Complaint) => (
        <Space direction="vertical" size="small">
          <Button 
            type="primary" 
            size="small" 
            icon={<EyeOutlined />}
            style={{ fontSize: 11, width: '100%' }}
          >
            View Details
          </Button>
          <Button 
            size="small" 
            icon={<DownloadOutlined />}
            style={{ fontSize: 11, width: '100%' }}
          >
            Download
          </Button>
          {record.attachments_count > 0 && (
            <Badge count={record.attachments_count} size="small">
              <Button size="small" style={{ fontSize: 10, width: '100%' }}>
                Attachments
              </Button>
            </Badge>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '20px', background: '#F5F5F5', minHeight: '100vh' }}>
      {/* Page Title */}
      <Card style={{ textAlign: 'center', marginBottom: 30, border: '2px solid #FF9933' }}>
        <Title level={2} style={{ color: '#FF9933', marginBottom: 16 }}>
          📊 Complaint Management Dashboard
        </Title>
        <Text style={{ fontSize: 16, color: '#666' }}>
          Track and manage citizen grievances with real-time insights
        </Text>
      </Card>

      {/* Statistics */}
      <Row gutter={[20, 20]} style={{ marginBottom: 30 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Complaints"
              value={stats.total}
              prefix={<ExclamationCircleOutlined style={{ color: '#1890FF' }} />}
              valueStyle={{ color: '#1890FF' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="New Submissions"
              value={stats.submitted}
              prefix={<ClockCircleOutlined style={{ color: '#FA8C16' }} />}
              valueStyle={{ color: '#FA8C16' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="In Progress"
              value={stats.inProgress}
              prefix={<SyncOutlined style={{ color: '#FF4D4F' }} />}
              valueStyle={{ color: '#FF4D4F' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Resolved"
              value={stats.resolved}
              prefix={<CheckCircleOutlined style={{ color: '#52C41A' }} />}
              valueStyle={{ color: '#52C41A' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filters */}
      <Card style={{ marginBottom: 20 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8}>
            <Search
              placeholder="Search complaints..."
              allowClear
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </Col>
          <Col xs={24} sm={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="Status"
              value={statusFilter}
              onChange={setStatusFilter}
            >
              <Select.Option value="all">All Status</Select.Option>
              <Select.Option value="submitted">Submitted</Select.Option>
              <Select.Option value="in_progress">In Progress</Select.Option>
              <Select.Option value="resolved">Resolved</Select.Option>
              <Select.Option value="closed">Closed</Select.Option>
              <Select.Option value="rejected">Rejected</Select.Option>
            </Select>
          </Col>
          <Col xs={24} sm={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="Priority"
              value={priorityFilter}
              onChange={setPriorityFilter}
            >
              <Select.Option value="all">All Priority</Select.Option>
              <Select.Option value="urgent">Urgent</Select.Option>
              <Select.Option value="high">High</Select.Option>
              <Select.Option value="medium">Medium</Select.Option>
              <Select.Option value="low">Low</Select.Option>
            </Select>
          </Col>
          <Col xs={24} sm={4}>
            <Select
              style={{ width: '100%' }}
              placeholder="Category"
              value={categoryFilter}
              onChange={setCategoryFilter}
            >
              <Select.Option value="all">All Categories</Select.Option>
              <Select.Option value="Infrastructure">Infrastructure</Select.Option>
              <Select.Option value="Utilities">Utilities</Select.Option>
              <Select.Option value="Healthcare">Healthcare</Select.Option>
              <Select.Option value="Education">Education</Select.Option>
              <Select.Option value="Social Services">Social Services</Select.Option>
            </Select>
          </Col>
          <Col xs={24} sm={4}>
            <Button type="primary" icon={<FilterOutlined />} style={{ width: '100%' }}>
              Apply Filters
            </Button>
          </Col>
        </Row>
      </Card>

      {/* Results Summary */}
      <Alert
        message={`Showing ${filteredComplaints.length} of ${complaints.length} complaints`}
        type="info"
        style={{ marginBottom: 20 }}
        showIcon
      />

      {/* Complaints Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredComplaints}
          loading={loading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${range[0]}-${range[1]} of ${total} complaints`,
          }}
          scroll={{ x: 1200 }}
          size="small"
        />
      </Card>
    </div>
  );
};

export default ComplaintDashboard;