import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Typography,
  Space,
  Button,
  Tag,
  Row,
  Col,
  Select,
  Input,
  Modal,
  Form,
  Upload,
  Progress,
  Alert,
  Tooltip,
  Steps,
} from 'antd';
import {
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  UploadOutlined,
  DownloadOutlined,
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
  EnvironmentOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Search } = Input;
const { Step } = Steps;

interface Assignment {
  id: string;
  complaint_id: string;
  complaint_title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'in_progress' | 'resolved' | 'rejected';
  assigned_at: string;
  due_date: string;
  category: string;
  user_name: string;
  user_phone: string;
  user_email: string;
  location: string;
  latitude?: number;
  longitude?: number;
  progress: number;
  notes: string[];
  attachments: string[];
}

const OfficerAssignments: React.FC = () => {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState<Assignment | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [updateModalVisible, setUpdateModalVisible] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [searchText, setSearchText] = useState('');
  const [form] = Form.useForm();

  // Mock data
  const mockAssignments: Assignment[] = [
    {
      id: 'ASG-001',
      complaint_id: 'CMP-2024-001',
      complaint_title: 'Street Light Not Working - MG Road',
      description: 'The street light near bus stop on MG Road has been non-functional for the past 3 days. This is causing safety concerns for commuters and residents.',
      priority: 'high',
      status: 'in_progress',
      assigned_at: '2024-01-15T10:00:00Z',
      due_date: '2024-01-17T23:59:59Z',
      category: 'Infrastructure',
      user_name: 'Rahul Sharma',
      user_phone: '+91-9876543210',
      user_email: 'rahul.sharma@email.com',
      location: 'MG Road, Sector 15, Near Bus Stop',
      latitude: 28.6139,
      longitude: 77.2090,
      progress: 65,
      notes: [
        'Initial inspection completed',
        'Faulty bulb identified',
        'Replacement parts ordered'
      ],
      attachments: ['photo1.jpg', 'inspection_report.pdf'],
    },
    {
      id: 'ASG-002',
      complaint_id: 'CMP-2024-002',
      complaint_title: 'Water Supply Disruption',
      description: 'No water supply for the past 2 days in Nehru Colony Block A. Affecting approximately 50 families.',
      priority: 'urgent',
      status: 'pending',
      assigned_at: '2024-01-16T08:30:00Z',
      due_date: '2024-01-16T18:00:00Z',
      category: 'Utilities',
      user_name: 'Priya Patel',
      user_phone: '+91-9765432101',
      user_email: 'priya.patel@email.com',
      location: 'Nehru Colony, Block A',
      latitude: 28.5355,
      longitude: 77.3910,
      progress: 10,
      notes: ['Complaint received', 'Team assigned'],
      attachments: [],
    },
    {
      id: 'ASG-003',
      complaint_id: 'CMP-2024-003',
      complaint_title: 'Garbage Collection Missed',
      description: 'Garbage has not been collected for 4 days in Green Park Extension. Creating hygiene issues.',
      priority: 'medium',
      status: 'resolved',
      assigned_at: '2024-01-14T14:20:00Z',
      due_date: '2024-01-16T23:59:59Z',
      category: 'Sanitation',
      user_name: 'Amit Kumar',
      user_phone: '+91-9654321012',
      user_email: 'amit.kumar@email.com',
      location: 'Green Park Extension',
      latitude: 28.5469,
      longitude: 77.2062,
      progress: 100,
      notes: [
        'Issue identified',
        'Garbage collection team dispatched',
        'Area cleaned and regular schedule resumed'
      ],
      attachments: ['before.jpg', 'after.jpg', 'completion_report.pdf'],
    },
  ];

  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setAssignments(mockAssignments);
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
      fixed: 'left',
      width: 300,
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Text strong style={{ color: '#1890ff' }}>
            {record.complaint_id}
          </Text>
          <Text ellipsis style={{ maxWidth: 280 }}>
            {record.complaint_title}
          </Text>
          <Space>
            <Tag color={priorityColors[record.priority as keyof typeof priorityColors]}>
              {record.priority.toUpperCase()}
            </Tag>
            <Tag color={statusColors[record.status as keyof typeof statusColors]}>
              {record.status.replace('_', ' ').toUpperCase()}
            </Tag>
          </Space>
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
      filters: [
        { text: 'Infrastructure', value: 'Infrastructure' },
        { text: 'Utilities', value: 'Utilities' },
        { text: 'Sanitation', value: 'Sanitation' },
        { text: 'Security', value: 'Security' },
      ],
      onFilter: (value, record) => record.category === value,
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      width: 120,
      render: (progress, record) => (
        <Space direction="vertical" size={0} style={{ width: '100%' }}>
          <Progress 
            percent={progress} 
            size="small" 
            strokeColor={progress === 100 ? '#52c41a' : progress > 50 ? '#1890ff' : '#faad14'} 
          />
          <Text style={{ fontSize: 12 }}>
            {record.notes.length} updates
          </Text>
        </Space>
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
        const timeLeft = Math.ceil((dueDate.getTime() - now.getTime()) / (1000 * 60 * 60));
        
        return (
          <Space direction="vertical" size={0}>
            <Text style={{ color: isOverdue ? '#f5222d' : timeLeft < 24 ? '#faad14' : '#000' }}>
              {dueDate.toLocaleDateString()}
            </Text>
            <Text style={{ fontSize: 11, color: isOverdue ? '#f5222d' : timeLeft < 24 ? '#faad14' : '#666' }}>
              {isOverdue ? 'Overdue' : timeLeft > 0 ? `${timeLeft}h left` : 'Due today'}
            </Text>
          </Space>
        );
      },
      sorter: (a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime(),
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
      width: 200,
      ellipsis: true,
      render: (location, record) => (
        <Tooltip title={location}>
          <Space>
            <EnvironmentOutlined style={{ color: '#1890ff' }} />
            <Text ellipsis style={{ maxWidth: 160 }}>
              {location}
            </Text>
          </Space>
        </Tooltip>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 200,
      render: (_, record) => (
        <Space>
          <Tooltip title="View Details">
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => viewAssignment(record)}
            />
          </Tooltip>
          <Tooltip title="Update Status">
            <Button
              size="small"
              type="primary"
              icon={<EditOutlined />}
              onClick={() => updateAssignment(record)}
              disabled={record.status === 'resolved'}
            />
          </Tooltip>
          <Tooltip title="Contact Citizen">
            <Button
              size="small"
              icon={<PhoneOutlined />}
              onClick={() => contactCitizen(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const viewAssignment = (assignment: Assignment) => {
    setSelectedAssignment(assignment);
    setIsModalVisible(true);
  };

  const updateAssignment = (assignment: Assignment) => {
    setSelectedAssignment(assignment);
    form.setFieldsValue({
      status: assignment.status,
      progress: assignment.progress,
      note: '',
    });
    setUpdateModalVisible(true);
  };

  const contactCitizen = (assignment: Assignment) => {
    // Implement contact functionality
    Modal.info({
      title: 'Contact Citizen',
      content: (
        <Space direction="vertical">
          <Text><strong>Name:</strong> {assignment.user_name}</Text>
          <Text><strong>Phone:</strong> {assignment.user_phone}</Text>
          <Text><strong>Email:</strong> {assignment.user_email}</Text>
        </Space>
      ),
    });
  };

  const handleStatusUpdate = (values: any) => {
    if (!selectedAssignment) return;

    // Update assignment
    const updatedAssignments = assignments.map(assignment =>
      assignment.id === selectedAssignment.id
        ? {
            ...assignment,
            status: values.status,
            progress: values.progress,
            notes: [...assignment.notes, values.note].filter(Boolean),
          }
        : assignment
    );

    setAssignments(updatedAssignments);
    setUpdateModalVisible(false);
    form.resetFields();
  };

  const getStatusSteps = (status: string) => {
    const steps = [
      { title: 'Assigned', status: 'finish' },
      { title: 'In Progress', status: status === 'pending' ? 'wait' : 'finish' },
      { title: 'Completed', status: status === 'resolved' ? 'finish' : 'wait' },
    ];
    return steps;
  };

  const filteredAssignments = assignments.filter(assignment => {
    const statusMatch = filterStatus === 'all' || assignment.status === filterStatus;
    const priorityMatch = filterPriority === 'all' || assignment.priority === filterPriority;
    const searchMatch = searchText === '' || 
      assignment.complaint_title.toLowerCase().includes(searchText.toLowerCase()) ||
      assignment.complaint_id.toLowerCase().includes(searchText.toLowerCase()) ||
      assignment.user_name.toLowerCase().includes(searchText.toLowerCase());
    
    return statusMatch && priorityMatch && searchMatch;
  });

  const urgentCount = assignments.filter(a => a.priority === 'urgent' && a.status !== 'resolved').length;
  const overdueCount = assignments.filter(a => new Date(a.due_date) < new Date() && a.status !== 'resolved').length;

  return (
    <div>
      <div className="page-header">
        <Title level={2} className="gov-title">
          My Assignments
        </Title>
        <Text className="gov-subtitle">
          Manage and update your assigned complaints
        </Text>
      </div>

      {/* Alerts */}
      {urgentCount > 0 && (
        <Alert
          message={`${urgentCount} Urgent Complaints`}
          description="These complaints require immediate attention"
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {overdueCount > 0 && (
        <Alert
          message={`${overdueCount} Overdue Complaints`}
          description="These complaints have passed their due date"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Filters */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8}>
            <Search
              placeholder="Search by complaint ID, title, or citizen name"
              allowClear
              enterButton={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </Col>
          <Col xs={12} sm={4}>
            <Select
              value={filterStatus}
              onChange={setFilterStatus}
              style={{ width: '100%' }}
              placeholder="Status"
            >
              <Select.Option value="all">All Status</Select.Option>
              <Select.Option value="pending">Pending</Select.Option>
              <Select.Option value="in_progress">In Progress</Select.Option>
              <Select.Option value="resolved">Resolved</Select.Option>
            </Select>
          </Col>
          <Col xs={12} sm={4}>
            <Select
              value={filterPriority}
              onChange={setFilterPriority}
              style={{ width: '100%' }}
              placeholder="Priority"
            >
              <Select.Option value="all">All Priority</Select.Option>
              <Select.Option value="urgent">Urgent</Select.Option>
              <Select.Option value="high">High</Select.Option>
              <Select.Option value="medium">Medium</Select.Option>
              <Select.Option value="low">Low</Select.Option>
            </Select>
          </Col>
          <Col xs={24} sm={8}>
            <Space>
              <Text strong>
                Showing {filteredAssignments.length} of {assignments.length} assignments
              </Text>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Assignments Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={filteredAssignments}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} assignments`,
          }}
          scroll={{ x: 1200 }}
          rowClassName={(record) => {
            if (record.priority === 'urgent' && record.status !== 'resolved') return 'urgent-row';
            if (new Date(record.due_date) < new Date() && record.status !== 'resolved') return 'overdue-row';
            return '';
          }}
        />
      </Card>

      {/* View Details Modal */}
      <Modal
        title={`Assignment Details - ${selectedAssignment?.complaint_id}`}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setIsModalVisible(false)}>
            Close
          </Button>,
        ]}
        width={800}
      >
        {selectedAssignment && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Steps
              current={selectedAssignment.status === 'pending' ? 0 : selectedAssignment.status === 'in_progress' ? 1 : 2}
              items={getStatusSteps(selectedAssignment.status)}
            />

            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Text strong>Priority:</Text><br />
                <Tag color={priorityColors[selectedAssignment.priority as keyof typeof priorityColors]}>
                  {selectedAssignment.priority.toUpperCase()}
                </Tag>
              </Col>
              <Col span={12}>
                <Text strong>Category:</Text><br />
                <Text>{selectedAssignment.category}</Text>
              </Col>
              <Col span={12}>
                <Text strong>Assigned:</Text><br />
                <Text>{new Date(selectedAssignment.assigned_at).toLocaleString()}</Text>
              </Col>
              <Col span={12}>
                <Text strong>Due Date:</Text><br />
                <Text>{new Date(selectedAssignment.due_date).toLocaleString()}</Text>
              </Col>
            </Row>

            <div>
              <Text strong>Description:</Text><br />
              <Text>{selectedAssignment.description}</Text>
            </div>

            <div>
              <Text strong>Citizen Information:</Text><br />
              <Space direction="vertical">
                <Text><UserOutlined /> {selectedAssignment.user_name}</Text>
                <Text><PhoneOutlined /> {selectedAssignment.user_phone}</Text>
                <Text><MailOutlined /> {selectedAssignment.user_email}</Text>
                <Text><EnvironmentOutlined /> {selectedAssignment.location}</Text>
              </Space>
            </div>

            <div>
              <Text strong>Progress Notes:</Text><br />
              {selectedAssignment.notes.length > 0 ? (
                <ul>
                  {selectedAssignment.notes.map((note, index) => (
                    <li key={index}>{note}</li>
                  ))}
                </ul>
              ) : (
                <Text type="secondary">No notes available</Text>
              )}
            </div>

            {selectedAssignment.attachments.length > 0 && (
              <div>
                <Text strong>Attachments:</Text><br />
                <Space wrap>
                  {selectedAssignment.attachments.map((attachment, index) => (
                    <Button key={index} size="small" icon={<DownloadOutlined />}>
                      {attachment}
                    </Button>
                  ))}
                </Space>
              </div>
            )}
          </Space>
        )}
      </Modal>

      {/* Update Status Modal */}
      <Modal
        title={`Update Assignment - ${selectedAssignment?.complaint_id}`}
        open={updateModalVisible}
        onCancel={() => setUpdateModalVisible(false)}
        onOk={() => form.submit()}
        okText="Update"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleStatusUpdate}
        >
          <Form.Item
            label="Status"
            name="status"
            rules={[{ required: true, message: 'Please select status' }]}
          >
            <Select>
              <Select.Option value="pending">Pending</Select.Option>
              <Select.Option value="in_progress">In Progress</Select.Option>
              <Select.Option value="resolved">Resolved</Select.Option>
              <Select.Option value="rejected">Rejected</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Progress (%)"
            name="progress"
            rules={[{ required: true, message: 'Please set progress' }]}
          >
            <Input type="number" min={0} max={100} />
          </Form.Item>

          <Form.Item
            label="Update Note"
            name="note"
            rules={[{ required: true, message: 'Please add an update note' }]}
          >
            <TextArea rows={4} placeholder="Describe the current status and any actions taken..." />
          </Form.Item>

          <Form.Item label="Attachments">
            <Upload>
              <Button icon={<UploadOutlined />}>Upload Files</Button>
            </Upload>
          </Form.Item>
        </Form>
      </Modal>

      <style jsx>{`
        .urgent-row {
          background-color: #fff2f0;
          border-left: 4px solid #ff4d4f;
        }
        .overdue-row {
          background-color: #fffbe6;
          border-left: 4px solid #faad14;
        }
      `}</style>
    </div>
  );
};

export default OfficerAssignments;
