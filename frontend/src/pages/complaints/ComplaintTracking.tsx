import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Card,
  Table,
  Tag,
  Input,
  Select,
  DatePicker,
  Button,
  Row,
  Col,
  Space,
  Statistic,
  Progress,
  Timeline,
  Badge,
} from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
  ReloadOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import BasePage from '@/components/common/BaseComponent';
import { fetchComplaints } from '@/store/slices/complaintSlice';
import { RootState, AppDispatch } from '@/store';
import type { Complaint } from '@/types';

const { Option } = Select;
const { RangePicker } = DatePicker;

interface ComplaintTrackingProps {}

const ComplaintTracking: React.FC<ComplaintTrackingProps> = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  
  const {
    complaints,
    loading,
    error,
    pagination
  } = useSelector((state: RootState) => state.complaints);

  const [filters, setFilters] = useState({
    search: '',
    status: [] as string[],
    priority: [] as string[],
    category: '',
    assignedTo: '',
    dateRange: null as any,
  });

  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  useEffect(() => {
    const apiFilters: any = {
      ...filters,
      status: filters.status.length > 0 ? filters.status : undefined,
      priority: filters.priority.length > 0 ? filters.priority : undefined,
    };
    dispatch(fetchComplaints(apiFilters));
  }, [dispatch, filters]);

  const getStatusColor = (status: string) => {
    const statusColors: Record<string, string> = {
      'pending': 'orange',
      'in_progress': 'blue',
      'resolved': 'green',
      'closed': 'default',
      'rejected': 'red',
    };
    return statusColors[status] || 'default';
  };

  const getPriorityColor = (priority: string) => {
    const priorityColors: Record<string, string> = {
      'low': 'green',
      'medium': 'orange',
      'high': 'red',
      'urgent': 'purple',
    };
    return priorityColors[priority] || 'default';
  };

  const getProgressPercentage = (status: string) => {
    const progressMap: Record<string, number> = {
      'pending': 10,
      'in_progress': 50,
      'resolved': 90,
      'closed': 100,
      'rejected': 0,
    };
    return progressMap[status] || 0;
  };

  const columns: ColumnsType<Complaint> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: true,
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text: string, record: Complaint) => (
        <a onClick={() => navigate(`/complaints/${record.id}`)}>
          {text}
        </a>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status.replace('_', ' ').toUpperCase()}
        </Tag>
      ),
      filters: [
        { text: 'Pending', value: 'pending' },
        { text: 'In Progress', value: 'in_progress' },
        { text: 'Resolved', value: 'resolved' },
        { text: 'Closed', value: 'closed' },
        { text: 'Rejected', value: 'rejected' },
      ],
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: string) => (
        <Tag color={getPriorityColor(priority)}>
          {priority.toUpperCase()}
        </Tag>
      ),
      filters: [
        { text: 'Low', value: 'low' },
        { text: 'Medium', value: 'medium' },
        { text: 'High', value: 'high' },
        { text: 'Urgent', value: 'urgent' },
      ],
    },
    {
      title: 'Progress',
      dataIndex: 'status',
      key: 'progress',
      width: 120,
      render: (status: string) => (
        <Progress
          percent={getProgressPercentage(status)}
          size="small"
          status={status === 'rejected' ? 'exception' : 'active'}
        />
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      ellipsis: true,
    },
    {
      title: 'Created Date',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 120,
      sorter: true,
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Assigned To',
      key: 'assignedTo',
      width: 120,
      render: () => 'Unassigned',
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_, record: Complaint) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/complaints/${record.id}`)}
          >
            View
          </Button>
        </Space>
      ),
    },
  ];

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      status: [],
      priority: [],
      category: '',
      assignedTo: '',
      dateRange: null,
    });
  };

  const handleRefresh = () => {
    const apiFilters: any = {
      ...filters,
      status: filters.status.length > 0 ? filters.status : undefined,
      priority: filters.priority.length > 0 ? filters.priority : undefined,
    };
    dispatch(fetchComplaints(apiFilters));
  };

  const handleExport = () => {
    // TODO: Implement export functionality
    console.log('Export complaints');
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys);
    },
    getCheckboxProps: (record: Complaint) => ({
      disabled: record.status === 'resolved',
      name: record.title,
    }),
  };

  const statusCounts = complaints.reduce((acc: Record<string, number>, complaint: Complaint) => {
    acc[complaint.status] = (acc[complaint.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <BasePage
      title="Complaint Tracking"
      loading={loading.list}
      error={error.list}
    >
      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={6}>
          <Card>
            <Statistic
              title="Total Complaints"
              value={pagination.count || 0}
              prefix={<Badge count={pagination.count || 0} color="blue" />}
            />
          </Card>
        </Col>
        <Col xs={6}>
          <Card>
            <Statistic
              title="Pending"
              value={statusCounts.pending || 0}
              prefix={<Badge count={statusCounts.pending || 0} color="orange" />}
            />
          </Card>
        </Col>
        <Col xs={6}>
          <Card>
            <Statistic
              title="In Progress"
              value={statusCounts.in_progress || 0}
              prefix={<Badge count={statusCounts.in_progress || 0} color="blue" />}
            />
          </Card>
        </Col>
        <Col xs={6}>
          <Card>
            <Statistic
              title="Resolved"
              value={statusCounts.resolved || 0}
              prefix={<Badge count={statusCounts.resolved || 0} color="green" />}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        {/* Filters */}
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={6}>
            <Input
              placeholder="Search complaints..."
              prefix={<SearchOutlined />}
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </Col>
          <Col xs={12} sm={4}>
            <Select
              mode="multiple"
              placeholder="Status"
              value={filters.status}
              onChange={(value) => handleFilterChange('status', value)}
              style={{ width: '100%' }}
              allowClear
            >
              <Option value="pending">Pending</Option>
              <Option value="in_progress">In Progress</Option>
              <Option value="resolved">Resolved</Option>
              <Option value="rejected">Rejected</Option>
            </Select>
          </Col>
          <Col xs={12} sm={4}>
            <Select
              mode="multiple"
              placeholder="Priority"
              value={filters.priority}
              onChange={(value) => handleFilterChange('priority', value)}
              style={{ width: '100%' }}
              allowClear
            >
              <Option value="low">Low</Option>
              <Option value="medium">Medium</Option>
              <Option value="high">High</Option>
              <Option value="urgent">Urgent</Option>
            </Select>
          </Col>
          <Col xs={24} sm={6}>
            <RangePicker
              value={filters.dateRange}
              onChange={(dates) => handleFilterChange('dateRange', dates)}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} sm={4}>
            <Space>
              <Button
                icon={<FilterOutlined />}
                onClick={clearFilters}
              >
                Clear
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleRefresh}
              >
                Refresh
              </Button>
              <Button
                icon={<ExportOutlined />}
                onClick={handleExport}
              >
                Export
              </Button>
            </Space>
          </Col>
        </Row>

        {/* Complaints Table */}
        <Table
          columns={columns}
          dataSource={complaints}
          rowKey="id"
          loading={loading.list}
          rowSelection={rowSelection}
          pagination={{
            current: pagination.currentPage,
            total: pagination.count,
            pageSize: pagination.pageSize,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} complaints`,
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </BasePage>
  );
};

export default ComplaintTracking;