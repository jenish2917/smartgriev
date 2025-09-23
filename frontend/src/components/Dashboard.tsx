import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Space,
  Typography,
  Alert,
  Button,
  Input,
  Select,
  Divider,
  Timeline,
  Progress,
  Badge,
} from 'antd';
import {
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  BankOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { apiService, handleApiError } from '@/services/api';
import type { Department } from '@/services/api';

const { Title, Text } = Typography;
const { Option } = Select;

interface DashboardProps {
  userRole?: 'citizen' | 'officer' | 'admin';
}

interface ComplaintStatus {
  id: number;
  title: string;
  department: string;
  status: 'submitted' | 'processing' | 'resolved' | 'rejected';
  urgency: 'low' | 'medium' | 'high' | 'critical';
  created_at: string;
  estimated_resolution: number;
  progress: number;
}

// Mock data for demonstration
const mockComplaints: ComplaintStatus[] = [
  {
    id: 1001,
    title: 'Power outage in residential area',
    department: 'Electricity Board',
    status: 'processing',
    urgency: 'high',
    created_at: '2025-09-23T10:30:00Z',
    estimated_resolution: 7,
    progress: 60,
  },
  {
    id: 1002,
    title: 'Road repair needed - multiple potholes',
    department: 'Public Works Department',
    status: 'submitted',
    urgency: 'medium',
    created_at: '2025-09-22T14:15:00Z',
    estimated_resolution: 14,
    progress: 20,
  },
  {
    id: 1003,
    title: 'Water supply disruption',
    department: 'Water and Sanitation',
    status: 'resolved',
    urgency: 'high',
    created_at: '2025-09-20T09:00:00Z',
    estimated_resolution: 5,
    progress: 100,
  },
];

export const Dashboard: React.FC<DashboardProps> = ({ userRole = 'citizen' }) => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [complaints, setComplaints] = useState<ComplaintStatus[]>(mockComplaints);
  const [loading, setLoading] = useState(false);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    loadDepartments();
    loadComplaints();
  }, []);

  const loadDepartments = async () => {
    try {
      const response = await apiService.getDepartments();
      setDepartments(response);
    } catch (error) {
      console.error('Failed to load departments:', error);
    }
  };

  const loadComplaints = async () => {
    setLoading(true);
    try {
      // In a real app, this would fetch user's complaints
      // For now, using mock data
      setComplaints(mockComplaints);
    } catch (error) {
      console.error('Failed to load complaints:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'submitted': return 'blue';
      case 'processing': return 'orange';
      case 'resolved': return 'green';
      case 'rejected': return 'red';
      default: return 'default';
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'blue';
      case 'low': return 'green';
      default: return 'default';
    }
  };

  const getDepartmentStats = () => {
    const stats = departments.map(dept => {
      const deptComplaints = complaints.filter(c => 
        c.department.toLowerCase().includes(dept.name.toLowerCase())
      );
      return {
        name: dept.name,
        count: deptComplaints.length,
        avgResolution: dept.avg_resolution_days,
      };
    });
    return stats;
  };

  const filteredComplaints = complaints.filter(complaint => {
    const matchesDepartment = selectedDepartment === 'all' || 
      complaint.department.toLowerCase().includes(selectedDepartment.toLowerCase());
    const matchesSearch = searchText === '' || 
      complaint.title.toLowerCase().includes(searchText.toLowerCase());
    return matchesDepartment && matchesSearch;
  });

  const complaintColumns = [
    {
      title: 'Complaint ID',
      dataIndex: 'id',
      key: 'id',
      render: (id: number) => <Text strong>#{id}</Text>,
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: 'Department',
      dataIndex: 'department',
      key: 'department',
      render: (dept: string) => <Tag icon={<BankOutlined />}>{dept}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)} icon={
          status === 'resolved' ? <CheckCircleOutlined /> :
          status === 'processing' ? <ClockCircleOutlined /> :
          <FileTextOutlined />
        }>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Urgency',
      dataIndex: 'urgency',
      key: 'urgency',
      render: (urgency: string) => (
        <Tag color={getUrgencyColor(urgency)}>
          {urgency.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number) => (
        <Progress 
          percent={progress} 
          size="small" 
          status={progress === 100 ? 'success' : 'active'}
        />
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: ComplaintStatus) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => {
            // Handle view complaint details
            console.log('View complaint:', record.id);
          }}
        >
          View
        </Button>
      ),
    },
  ];

  const renderDepartmentCards = () => (
    <Row gutter={[16, 16]}>
      {departments.slice(0, 6).map((dept, index) => (
        <Col key={dept.id} xs={24} sm={12} lg={8}>
          <Card 
            size="small" 
            hoverable
            onClick={() => setSelectedDepartment(dept.name)}
          >
            <Statistic
              title={dept.name}
              value={dept.avg_resolution_days}
              suffix="days"
              prefix={<BankOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              Average resolution time
            </Text>
          </Card>
        </Col>
      ))}
    </Row>
  );

  const renderSystemHealth = () => (
    <Card title="System Status" size="small">
      <Row gutter={[16, 8]}>
        <Col span={8}>
          <Badge status="success" text="Backend API" />
        </Col>
        <Col span={8}>
          <Badge status="success" text="AI Processing" />
        </Col>
        <Col span={8}>
          <Badge status="success" text="Database" />
        </Col>
        <Col span={8}>
          <Badge status="warning" text="Groq AI" />
        </Col>
        <Col span={8}>
          <Badge status="processing" text="OTP Service" />
        </Col>
        <Col span={8}>
          <Badge status="success" text="File Upload" />
        </Col>
      </Row>
    </Card>
  );

  return (
    <div className="p-6">
      <div className="mb-6">
        <Title level={2}>SmartGriev Dashboard</Title>
        <Text type="secondary">
          Monitor your complaints and system performance
        </Text>
      </div>

      {/* System Health Alert */}
      <Alert
        message="System Operational"
        description="All core services are running. AI enhancement available with API key configuration."
        type="success"
        showIcon
        closable
        style={{ marginBottom: 24 }}
      />

      {/* Statistics Overview */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Complaints"
              value={complaints.length}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="In Progress"
              value={complaints.filter(c => c.status === 'processing').length}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Resolved"
              value={complaints.filter(c => c.status === 'resolved').length}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Avg Resolution"
              value={7}
              suffix="days"
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* System Health */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          {renderSystemHealth()}
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Quick Actions" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button type="primary" block icon={<FileTextOutlined />}>
                Submit New Complaint
              </Button>
              <Button block icon={<SearchOutlined />}>
                Track Complaint Status
              </Button>
              <Button block icon={<BankOutlined />}>
                View Department Info
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Department Overview */}
      <Card title="Government Departments" style={{ marginBottom: 24 }}>
        {renderDepartmentCards()}
      </Card>

      {/* Complaints Table */}
      <Card title="Your Complaints">
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="Search complaints..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 200 }}
          />
          <Select
            value={selectedDepartment}
            onChange={setSelectedDepartment}
            style={{ width: 200 }}
          >
            <Option value="all">All Departments</Option>
            {departments.map(dept => (
              <Option key={dept.id} value={dept.name}>
                {dept.name}
              </Option>
            ))}
          </Select>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadComplaints}
            loading={loading}
          >
            Refresh
          </Button>
        </Space>

        <Table
          columns={complaintColumns}
          dataSource={filteredComplaints}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} complaints`,
          }}
        />
      </Card>
    </div>
  );
};

export default Dashboard;