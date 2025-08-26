import React, { useState, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Table,
  Tag,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Timeline,
  Progress,
  Divider,
  Alert,
} from 'antd';
import {
  SearchOutlined,
  EyeOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Search } = Input;

interface Complaint {
  id: string;
  title: string;
  status: 'pending' | 'in_progress' | 'resolved' | 'rejected';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  created_at: string;
  department: string;
  category: string;
  progress: number;
}

const ComplaintTracking: React.FC = () => {
  const navigate = useNavigate();
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');

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

  const columns: ColumnsType<Complaint> = [
    {
      title: 'Complaint ID',
      dataIndex: 'id',
      key: 'id',
      width: 120,
      render: (id) => (
        <Text code style={{ color: '#1890ff' }}>
          {id}
        </Text>
      ),
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
      width: 150,
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 120,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
        <Tag color={statusColors[status as keyof typeof statusColors]}>
          {status.toUpperCase()}
        </Tag>
      ),
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
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      width: 120,
      render: (progress) => (
        <Progress 
          percent={progress} 
          size="small" 
          strokeColor={progress === 100 ? '#52c41a' : '#1890ff'} 
        />
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      render: (date) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/complaints/${record.id}`)}
          >
            View
          </Button>
        </Space>
      ),
    },
  ];

  // Mock data - replace with actual API call
  const mockComplaints: Complaint[] = [
    {
      id: 'CMP-2024-001',
      title: 'Street Light Not Working',
      status: 'in_progress',
      priority: 'medium',
      created_at: '2024-01-15',
      department: 'Electricity Board',
      category: 'Infrastructure',
      progress: 65,
    },
    {
      id: 'CMP-2024-002',
      title: 'Water Supply Issue',
      status: 'resolved',
      priority: 'high',
      created_at: '2024-01-14',
      department: 'Water Board',
      category: 'Utilities',
      progress: 100,
    },
    {
      id: 'CMP-2024-003',
      title: 'Road Maintenance Required',
      status: 'pending',
      priority: 'low',
      created_at: '2024-01-16',
      department: 'PWD',
      category: 'Infrastructure',
      progress: 25,
    },
  ];

  useEffect(() => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setComplaints(mockComplaints);
      setLoading(false);
    }, 1000);
  }, []);

  const handleSearch = (value: string) => {
    setSearchText(value);
    // Implement search logic here
  };

  const stats = [
    {
      title: 'Total Complaints',
      value: complaints.length,
      icon: <FileTextOutlined />,
      color: '#1890ff',
    },
    {
      title: 'In Progress',
      value: complaints.filter(c => c.status === 'in_progress').length,
      icon: <ClockCircleOutlined />,
      color: '#faad14',
    },
    {
      title: 'Resolved',
      value: complaints.filter(c => c.status === 'resolved').length,
      icon: <CheckCircleOutlined />,
      color: '#52c41a',
    },
    {
      title: 'Pending',
      value: complaints.filter(c => c.status === 'pending').length,
      icon: <ExclamationCircleOutlined />,
      color: '#f5222d',
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={2} className="gov-title">
          Track Your Complaints
        </Title>
        <Text className="gov-subtitle">
          Monitor the status and progress of your submitted grievances
        </Text>
      </div>

      {/* Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {stats.map((stat, index) => (
          <Col xs={24} sm={12} md={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.value}
                prefix={stat.icon}
                valueStyle={{ color: stat.color }}
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Search */}
          <Row justify="space-between" align="middle">
            <Col>
              <Title level={4}>Your Complaints</Title>
            </Col>
            <Col>
              <Search
                placeholder="Search by complaint ID, title, or department"
                allowClear
                enterButton={<SearchOutlined />}
                size="large"
                style={{ width: 400 }}
                onSearch={handleSearch}
              />
            </Col>
          </Row>

          <Divider />

          {/* Instructions */}
          <Alert
            message="Track Your Complaints"
            description="Use your complaint ID or search through your submitted grievances to track their current status and progress."
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />

          {/* Table */}
          <Table
            columns={columns}
            dataSource={complaints}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) =>
                `${range[0]}-${range[1]} of ${total} complaints`,
            }}
            scroll={{ x: 1200 }}
          />
        </Space>
      </Card>
    </div>
  );
};

export default ComplaintTracking;
