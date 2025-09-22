import React, { useEffect } from 'react';import React, { useEffect } from 'react';import React, { useEffect } from 'react';import React, { useState, useEffect } from 'react';

import { useParams, useNavigate } from 'react-router-dom';

import {import { useParams, useNavigate } from 'react-router-dom';

  Card,

  Descriptions,import {import { useParams, useNavigate } from 'react-router-dom';import { useParams, useNavigate } from 'react-router-dom';

  Tag,

  Button,  Card,

  Typography,

  Space,  Descriptions,import {import {

  Spin,

  Row,  Tag,

  Col,

} from 'antd';  Button,  Card,  Card,

import {

  ArrowLeftOutlined,  Typography,

  EditOutlined,

  MessageOutlined,  Space,  Descriptions,  Row,

  EnvironmentOutlined,

  UserOutlined,  Spin,

} from '@ant-design/icons';

import { useSelector, useDispatch } from 'react-redux';  Row,  Tag,  Col,

import { RootState } from '@/store';

import { fetchComplaint } from '@/store/slices/complaintSlice';  Col,



const { Title, Text } = Typography;} from 'antd';  Button,  Descriptions,



const ComplaintDetail: React.FC = () => {import {

  const { id } = useParams<{ id: string }>();

  const navigate = useNavigate();  ArrowLeftOutlined,  Typography,  Tag,

  const dispatch = useDispatch();

  EditOutlined,

  const { currentComplaint, loading } = useSelector((state: RootState) => state.complaints);

  const { user } = useSelector((state: RootState) => state.auth);  MessageOutlined,  Space,  Button,



  useEffect(() => {  EnvironmentOutlined,

    if (id) {

      dispatch(fetchComplaint(Number(id)) as any);  UserOutlined,  Spin,  Typography,

    }

  }, [dispatch, id]);} from '@ant-design/icons';



  const getStatusColor = (status: string) => {import { useSelector, useDispatch } from 'react-redux';  Row,  Space,

    const colors: Record<string, string> = {

      'pending': 'orange',import { RootState } from '@/store';

      'in_progress': 'blue',

      'resolved': 'green',import { fetchComplaint } from '@/store/slices/complaintSlice';  Col,  Timeline,

      'closed': 'gray',

      'rejected': 'red',

    };

    return colors[status] || 'default';const { Title, Text } = Typography;} from 'antd';  Image,

  };



  const getPriorityColor = (priority: string) => {

    const colors: Record<string, string> = {const ComplaintDetail: React.FC = () => {import {  Divider,

      'low': 'green',

      'medium': 'orange',  const { id } = useParams<{ id: string }>();

      'high': 'red',

      'urgent': 'magenta',  const navigate = useNavigate();  ArrowLeftOutlined,  Modal,

    };

    return colors[priority] || 'default';  const dispatch = useDispatch();

  };

  EditOutlined,  Form,

  if (loading.detail || !currentComplaint) {

    return (  const { currentComplaint, loading } = useSelector((state: RootState) => state.complaints);

      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>

        <Spin size="large" />  const { user } = useSelector((state: RootState) => state.auth);  MessageOutlined,  Input,

      </div>

    );

  }

  useEffect(() => {  EnvironmentOutlined,  Select,

  return (

    <div>    if (id) {

      <div style={{ marginBottom: 16 }}>

        <Button       dispatch(fetchComplaint(Number(id)) as any);  UserOutlined,  Upload,

          icon={<ArrowLeftOutlined />} 

          onClick={() => navigate('/complaints')}    }

          style={{ marginRight: 16 }}

        >  }, [dispatch, id]);} from '@ant-design/icons';  message,

          Back to Complaints

        </Button>

        <Space>

          {(user?.is_officer || user?.is_superuser) && (  const getStatusColor = (status: string) => {import { useSelector, useDispatch } from 'react-redux';  Spin,

            <Button 

              type="primary"     const colors: Record<string, string> = {

              icon={<EditOutlined />}

              onClick={() => navigate(`/complaints/${id}/edit`)}      'pending': 'orange',import { RootState } from '@/store';} from 'antd';

            >

              Edit Complaint      'in_progress': 'blue',

            </Button>

          )}      'resolved': 'green',import { fetchComplaint } from '@/store/slices/complaintSlice';import {

          <Button 

            icon={<MessageOutlined />}      'closed': 'gray',

            onClick={() => console.log('Add comment feature coming soon')}

          >      'rejected': 'red',  ArrowLeftOutlined,

            Add Comment

          </Button>    };

        </Space>

      </div>    return colors[status] || 'default';const { Title, Text } = Typography;  EditOutlined,



      <Row gutter={[24, 24]}>  };

        <Col span={16}>

          <Card title={<Title level={3}>Complaint Details</Title>}>  MessageOutlined,

            <Descriptions column={2} bordered>

              <Descriptions.Item label="Complaint ID">{currentComplaint.id}</Descriptions.Item>  const getPriorityColor = (priority: string) => {

              <Descriptions.Item label="Status">

                <Tag color={getStatusColor(currentComplaint.status)}>    const colors: Record<string, string> = {const ComplaintDetail: React.FC = () => {  FileOutlined,

                  {currentComplaint.status.replace('_', ' ').toUpperCase()}

                </Tag>      'low': 'green',

              </Descriptions.Item>

              <Descriptions.Item label="Priority">      'medium': 'orange',  const { id } = useParams<{ id: string }>();  EnvironmentOutlined,

                <Tag color={getPriorityColor(currentComplaint.priority)}>

                  {currentComplaint.priority.toUpperCase()}      'high': 'red',

                </Tag>

              </Descriptions.Item>      'urgent': 'magenta',  const navigate = useNavigate();  ClockCircleOutlined,

              <Descriptions.Item label="Category">{currentComplaint.category}</Descriptions.Item>

              <Descriptions.Item label="Title" span={2}>{currentComplaint.title}</Descriptions.Item>    };

              <Descriptions.Item label="Description" span={2}>

                {currentComplaint.description}    return colors[priority] || 'default';  const dispatch = useDispatch();  UserOutlined,

              </Descriptions.Item>

              <Descriptions.Item label="Created">  };

                {new Date(currentComplaint.created_at).toLocaleString()}

              </Descriptions.Item>  PhoneOutlined,

              <Descriptions.Item label="Updated">

                {new Date(currentComplaint.updated_at).toLocaleString()}  if (loading.detail || !currentComplaint) {

              </Descriptions.Item>

            </Descriptions>    return (  const { currentComplaint, loading } = useSelector((state: RootState) => state.complaints);  MailOutlined,

          </Card>

        </Col>      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>



        <Col span={8}>        <Spin size="large" />  const { user } = useSelector((state: RootState) => state.auth);  CameraOutlined,

          <Card title="Additional Information">

            <Space direction="vertical" style={{ width: '100%' }}>      </div>

              <div>

                <UserOutlined style={{ marginRight: 8 }} />    );} from '@ant-design/icons';

                <Text strong>User ID: </Text>

                <Text>{currentComplaint.user}</Text>  }

              </div>

              <div>  useEffect(() => {import { useSelector, useDispatch } from 'react-redux';

                <Text strong>Department: </Text>

                <Text>{currentComplaint.department_name || currentComplaint.department}</Text>  return (

              </div>

              {currentComplaint.incident_address && (    <div>    if (id) {import { RootState } from '@/store';

                <div>

                  <EnvironmentOutlined style={{ marginRight: 8 }} />      <div style={{ marginBottom: 16 }}>

                  <Text strong>Address: </Text>

                  <Text>{currentComplaint.incident_address}</Text>        <Button       dispatch(fetchComplaint(Number(id)) as any);import { fetchComplaint, updateComplaint } from '@/store/slices/complaintSlice';

                </div>

              )}          icon={<ArrowLeftOutlined />} 

              {(currentComplaint.incident_latitude && currentComplaint.incident_longitude) && (

                <div>          onClick={() => navigate('/complaints')}    }

                  <Text strong>Coordinates: </Text>

                  <Text>          style={{ marginRight: 16 }}

                    {currentComplaint.incident_latitude}, {currentComplaint.incident_longitude}

                  </Text>        >  }, [dispatch, id]);const { Title, Text } = Typography;

                </div>

              )}          Back to Complaints

            </Space>

          </Card>        </Button>const { TextArea } = Input;

        </Col>

      </Row>        <Space>

    </div>

  );          {(user?.is_officer || user?.is_superuser) && (  const getStatusColor = (status: string) => {const { Option } = Select;

};

            <Button 

export default ComplaintDetail;
              type="primary"     const colors: Record<string, string> = {

              icon={<EditOutlined />}

              onClick={() => navigate(`/complaints/${id}/edit`)}      'pending': 'orange',interface ComplaintDetailProps {

            >

              Edit Complaint      'in_progress': 'blue',  complaintId?: string;

            </Button>

          )}      'resolved': 'green',}

          <Button 

            icon={<MessageOutlined />}      'closed': 'gray',

            onClick={() => console.log('Add comment feature coming soon')}

          >      'rejected': 'red',const ComplaintDetail: React.FC<ComplaintDetailProps> = () => {

            Add Comment

          </Button>    };  const { id } = useParams<{ id: string }>();

        </Space>

      </div>    return colors[status] || 'default';  const navigate = useNavigate();



      <Row gutter={[24, 24]}>  };  const dispatch = useDispatch();

        <Col span={16}>

          <Card title={<Title level={3}>Complaint Details</Title>}>  const [editModalVisible, setEditModalVisible] = useState(false);

            <Descriptions column={2} bordered>

              <Descriptions.Item label="Complaint ID">{currentComplaint.id}</Descriptions.Item>  const getPriorityColor = (priority: string) => {  const [commentModalVisible, setCommentModalVisible] = useState(false);

              <Descriptions.Item label="Status">

                <Tag color={getStatusColor(currentComplaint.status)}>    const colors: Record<string, string> = {  const [form] = Form.useForm();

                  {currentComplaint.status.replace('_', ' ').toUpperCase()}

                </Tag>      'low': 'green',  const [commentForm] = Form.useForm();

              </Descriptions.Item>

              <Descriptions.Item label="Priority">      'medium': 'orange',

                <Tag color={getPriorityColor(currentComplaint.priority)}>

                  {currentComplaint.priority.toUpperCase()}      'high': 'red',    const { currentComplaint, loading } = useSelector((state: RootState) => state.complaints);

                </Tag>

              </Descriptions.Item>      'urgent': 'magenta',  const { user } = useSelector((state: RootState) => state.auth);

              <Descriptions.Item label="Category">{currentComplaint.category}</Descriptions.Item>

              <Descriptions.Item label="Title" span={2}>{currentComplaint.title}</Descriptions.Item>    };

              <Descriptions.Item label="Description" span={2}>

                {currentComplaint.description}    return colors[priority] || 'default';  useEffect(() => {

              </Descriptions.Item>

              <Descriptions.Item label="Created">  };    if (id) {

                {new Date(currentComplaint.created_at).toLocaleString()}

              </Descriptions.Item>      dispatch(fetchComplaint(Number(id)) as any);

              <Descriptions.Item label="Updated">

                {new Date(currentComplaint.updated_at).toLocaleString()}  if (loading.detail || !currentComplaint) {    }

              </Descriptions.Item>

            </Descriptions>    return (  }, [dispatch, id]);

          </Card>

        </Col>      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>



        <Col span={8}>        <Spin size="large" />  const handleUpdateComplaint = async (values: any) => {

          <Card title="Additional Information">

            <Space direction="vertical" style={{ width: '100%' }}>      </div>    try {

              <div>

                <UserOutlined style={{ marginRight: 8 }} />    );      await dispatch(updateComplaint({ id: Number(id!), data: values }) as any);

                <Text strong>User ID: </Text>

                <Text>{currentComplaint.user}</Text>  }      setEditModalVisible(false);

              </div>

              <div>      message.success('Complaint updated successfully');

                <Text strong>Department: </Text>

                <Text>{currentComplaint.department_name || currentComplaint.department}</Text>  return (    } catch (error) {

              </div>

              {currentComplaint.incident_address && (    <div>      message.error('Failed to update complaint');

                <div>

                  <EnvironmentOutlined style={{ marginRight: 8 }} />      <div style={{ marginBottom: 16 }}>    }

                  <Text strong>Address: </Text>

                  <Text>{currentComplaint.incident_address}</Text>        <Button   };

                </div>

              )}          icon={<ArrowLeftOutlined />} 

              {(currentComplaint.incident_latitude && currentComplaint.incident_longitude) && (

                <div>          onClick={() => navigate('/complaints')}  const handleAddComment = async (values: any) => {

                  <Text strong>Coordinates: </Text>

                  <Text>          style={{ marginRight: 16 }}    try {

                    {currentComplaint.incident_latitude}, {currentComplaint.incident_longitude}

                  </Text>        >      // Note: Add comment functionality needs to be implemented in the slice

                </div>

              )}          Back to Complaints      message.info('Comment functionality will be available soon');

            </Space>

          </Card>        </Button>      setCommentModalVisible(false);

        </Col>

      </Row>        <Space>      commentForm.resetFields();

    </div>

  );          {(user?.is_officer || user?.is_superuser) && (    } catch (error) {

};

            <Button       message.error('Failed to add comment');

export default ComplaintDetail;
              type="primary"     }

              icon={<EditOutlined />}  };

              onClick={() => navigate(`/complaints/${id}/edit`)}

            >  const getStatusColor = (status: string) => {

              Edit Complaint    const colors: Record<string, string> = {

            </Button>      'pending': 'orange',

          )}      'in_progress': 'blue',

          <Button       'resolved': 'green',

            icon={<MessageOutlined />}      'closed': 'gray',

            onClick={() => console.log('Add comment feature coming soon')}      'rejected': 'red',

          >    };

            Add Comment    return colors[status] || 'default';

          </Button>  };

        </Space>

      </div>  const getPriorityColor = (priority: string) => {

    const colors: Record<string, string> = {

      <Row gutter={[24, 24]}>      'low': 'green',

        <Col span={16}>      'medium': 'orange',

          <Card title={<Title level={3}>Complaint Details</Title>}>      'high': 'red',

            <Descriptions column={2} bordered>      'urgent': 'magenta',

              <Descriptions.Item label="Complaint ID">{currentComplaint.id}</Descriptions.Item>    };

              <Descriptions.Item label="Status">    return colors[priority] || 'default';

                <Tag color={getStatusColor(currentComplaint.status)}>  };

                  {currentComplaint.status.replace('_', ' ').toUpperCase()}

                </Tag>  if (loading || !currentComplaint) {

              </Descriptions.Item>    return (

              <Descriptions.Item label="Priority">      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>

                <Tag color={getPriorityColor(currentComplaint.priority)}>        <Spin size="large" />

                  {currentComplaint.priority.toUpperCase()}      </div>

                </Tag>    );

              </Descriptions.Item>  }

              <Descriptions.Item label="Category">{currentComplaint.category}</Descriptions.Item>

              <Descriptions.Item label="Title" span={2}>{currentComplaint.title}</Descriptions.Item>  return (

              <Descriptions.Item label="Description" span={2}>    <div>

                {currentComplaint.description}      <div style={{ marginBottom: 16 }}>

              </Descriptions.Item>        <Button 

              <Descriptions.Item label="Created">          icon={<ArrowLeftOutlined />} 

                {new Date(currentComplaint.created_at).toLocaleString()}          onClick={() => navigate('/complaints')}

              </Descriptions.Item>          style={{ marginRight: 16 }}

              <Descriptions.Item label="Updated">        >

                {new Date(currentComplaint.updated_at).toLocaleString()}          Back to Complaints

              </Descriptions.Item>        </Button>

            </Descriptions>        <Space>

          </Card>          {(user?.is_officer || user?.is_superuser) && (

        </Col>            <Button 

              type="primary" 

        <Col span={8}>              icon={<EditOutlined />}

          <Card title="Additional Information">              onClick={() => setEditModalVisible(true)}

            <Space direction="vertical" style={{ width: '100%' }}>            >

              <div>              Edit Complaint

                <UserOutlined style={{ marginRight: 8 }} />            </Button>

                <Text strong>User ID: </Text>          )}

                <Text>{currentComplaint.user}</Text>          <Button 

              </div>            icon={<MessageOutlined />}

              <div>            onClick={() => setCommentModalVisible(true)}

                <Text strong>Department: </Text>          >

                <Text>{currentComplaint.department_name || currentComplaint.department}</Text>            Add Comment

              </div>          </Button>

              {currentComplaint.incident_address && (        </Space>

                <div>      </div>

                  <EnvironmentOutlined style={{ marginRight: 8 }} />

                  <Text strong>Address: </Text>      <Row gutter={[24, 24]}>

                  <Text>{currentComplaint.incident_address}</Text>        <Col span={16}>

                </div>          <Card title={<Title level={3}>Complaint Details</Title>}>

              )}            <Descriptions column={2} bordered>

              {(currentComplaint.incident_latitude && currentComplaint.incident_longitude) && (              <Descriptions.Item label="Complaint ID">{currentComplaint.id}</Descriptions.Item>

                <div>              <Descriptions.Item label="Status">

                  <Text strong>Coordinates: </Text>                <Tag color={getStatusColor(currentComplaint.status)}>

                  <Text>                  {currentComplaint.status.replace('_', ' ').toUpperCase()}

                    {currentComplaint.incident_latitude}, {currentComplaint.incident_longitude}                </Tag>

                  </Text>              </Descriptions.Item>

                </div>              <Descriptions.Item label="Priority">

              )}                <Tag color={getPriorityColor(currentComplaint.priority)}>

            </Space>                  {currentComplaint.priority.toUpperCase()}

          </Card>                </Tag>

        </Col>              </Descriptions.Item>

      </Row>              <Descriptions.Item label="Category">{currentComplaint.category}</Descriptions.Item>

    </div>              <Descriptions.Item label="Title" span={2}>{currentComplaint.title}</Descriptions.Item>

  );              <Descriptions.Item label="Description" span={2}>

};                {currentComplaint.description}

              </Descriptions.Item>

export default ComplaintDetail;              <Descriptions.Item label="Created">
                {new Date(currentComplaint.created_at).toLocaleString()}
              </Descriptions.Item>
              <Descriptions.Item label="Updated">
                {new Date(currentComplaint.updated_at).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>

            {currentComplaint.media && (
              <>
                <Divider>Attachments</Divider>
                <Image
                  width={200}
                  src={currentComplaint.media}
                  style={{ objectFit: 'cover', borderRadius: 4 }}
                />
              </>
            )}
          </Card>

          </Card>
        </Col>

        <Col span={8}>
          <Card title="Complaint Information">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>User ID: </Text>
                <Text>{currentComplaint.user}</Text>
              </div>
              <div>
                <Text strong>Department: </Text>
                <Text>{currentComplaint.department_name || currentComplaint.department}</Text>
              </div>
            </Space>
          </Card>

          {(currentComplaint.incident_latitude && currentComplaint.incident_longitude) && (
            <Card title="Location Information" style={{ marginTop: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <EnvironmentOutlined style={{ marginRight: 8 }} />
                  <Text strong>Address: </Text>
                  <Text>{currentComplaint.incident_address || 'Not provided'}</Text>
                </div>
                <div>
                  <Text strong>Coordinates: </Text>
                  <Text>
                    {currentComplaint.incident_latitude}, {currentComplaint.incident_longitude}
                  </Text>
                </div>
                {currentComplaint.incident_landmark && (
                  <div>
                    <Text strong>Landmark: </Text>
                    <Text>{currentComplaint.incident_landmark}</Text>
                  </div>
                )}
              </Space>
            </Card>
          )}
        </Col>
      </Row>

      {/* Edit Modal */}
      <Modal
        title="Edit Complaint"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUpdateComplaint}
          initialValues={{
            status: currentComplaint?.status,
            priority: currentComplaint?.priority,
            notes: ''
          }}
        >
          <Form.Item name="status" label="Status">
            <Select>
              <Option value="pending">Pending</Option>
              <Option value="in_progress">In Progress</Option>
              <Option value="resolved">Resolved</Option>
              <Option value="closed">Closed</Option>
              <Option value="rejected">Rejected</Option>
            </Select>
          </Form.Item>
          <Form.Item name="priority" label="Priority">
            <Select>
              <Option value="low">Low</Option>
              <Option value="medium">Medium</Option>
              <Option value="high">High</Option>
              <Option value="urgent">Urgent</Option>
            </Select>
          </Form.Item>
          <Form.Item name="notes" label="Internal Notes">
            <TextArea rows={4} placeholder="Add internal notes..." />
          </Form.Item>
        </Form>
      </Modal>

      {/* Comment Modal */}
      <Modal
        title="Add Comment"
        open={commentModalVisible}
        onCancel={() => setCommentModalVisible(false)}
        onOk={() => commentForm.submit()}
      >
        <Form form={commentForm} layout="vertical" onFinish={handleAddComment}>
          <Form.Item
            name="comment"
            label="Comment"
            rules={[{ required: true, message: 'Please enter a comment' }]}
          >
            <TextArea rows={4} placeholder="Enter your comment..." />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ComplaintDetail;
