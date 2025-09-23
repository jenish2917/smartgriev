import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Typography,
  Space,
  Spin,
  Row,
  Col,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  MessageOutlined,
  EnvironmentOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store';
import { fetchComplaint } from '@/store/slices/complaintSlice';

const { Title, Text } = Typography;

const ComplaintDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const { currentComplaint, loading } = useSelector((state: RootState) => state.complaints);
  const { user } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    if (id) {
      dispatch(fetchComplaint(Number(id)) as any);
    }
  }, [dispatch, id]);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'pending': 'orange',
      'in_progress': 'blue',
      'resolved': 'green',
      'closed': 'gray',
      'rejected': 'red',
    };
    return colors[status] || 'default';
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'low': 'green',
      'medium': 'orange',
      'high': 'red',
      'urgent': 'magenta',
    };
    return colors[priority] || 'default';
  };

  if (loading.detail || !currentComplaint) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate('/complaints')}
          style={{ marginRight: 16 }}
        >
          Back to Complaints
        </Button>
        <Space>
          {(user?.is_officer || user?.is_superuser) && (
            <Button 
              type="primary" 
              icon={<EditOutlined />}
              onClick={() => navigate(`/complaints/${id}/edit`)}
            >
              Edit Complaint
            </Button>
          )}
          <Button 
            icon={<MessageOutlined />}
            onClick={() => console.log('Add comment feature coming soon')}
          >
            Add Comment
          </Button>
        </Space>
      </div>

      <Row gutter={[24, 24]}>
        <Col span={16}>
          <Card title={<Title level={3}>Complaint Details</Title>}>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="Complaint ID">{currentComplaint.id}</Descriptions.Item>
              <Descriptions.Item label="Status">
                <Tag color={getStatusColor(currentComplaint.status)}>
                  {currentComplaint.status.replace('_', ' ').toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Priority">
                <Tag color={getPriorityColor(currentComplaint.priority)}>
                  {currentComplaint.priority.toUpperCase()}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Category">{currentComplaint.category}</Descriptions.Item>
              <Descriptions.Item label="Title" span={2}>{currentComplaint.title}</Descriptions.Item>
              <Descriptions.Item label="Description" span={2}>
                {currentComplaint.description}
              </Descriptions.Item>
              <Descriptions.Item label="Created">
                {new Date(currentComplaint.created_at).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label="Updated">
                {new Date(currentComplaint.updated_at).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        <Col span={8}>
          <Card title="Additional Information">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <UserOutlined style={{ marginRight: 8 }} />
                <Text strong>User ID: </Text>
                <Text>{currentComplaint.user}</Text>
              </div>
              <div>
                <Text strong>Department: </Text>
                <Text>{currentComplaint.department_name || currentComplaint.department}</Text>
              </div>
              {currentComplaint.incident_address && (
                <div>
                  <EnvironmentOutlined style={{ marginRight: 8 }} />
                  <Text strong>Address: </Text>
                  <Text>{currentComplaint.incident_address}</Text>
                </div>
              )}
              {(currentComplaint.incident_latitude && currentComplaint.incident_longitude) && (
                <div>
                  <Text strong>Coordinates: </Text>
                  <Text>
                    {currentComplaint.incident_latitude}, {currentComplaint.incident_longitude}
                  </Text>
                </div>
              )}
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ComplaintDetail;
