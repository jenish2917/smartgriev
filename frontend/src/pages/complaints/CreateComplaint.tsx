import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import {
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Card,
  Row,
  Col,
  Upload,
  message,
  Space,
} from 'antd';
import { InboxOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import BasePage from '@/components/common/BaseComponent';
import { createComplaint } from '@/store/slices/complaintSlice';
import { AppDispatch } from '@/store';

const { Option } = Select;
const { TextArea } = Input;
const { Dragger } = Upload;

interface CreateComplaintFormData {
  title: string;
  description: string;
  category: string;
  department: number;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  location?: string;
  expectedResolutionDate?: string;
  attachments?: File[];
}

const CreateComplaint: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();

  const categories = [
    'Infrastructure',
    'Public Services',
    'Environment',
    'Transportation',
    'Health & Safety',
    'Education',
    'Other'
  ];

  const departments = [
    { id: 1, name: 'Public Works' },
    { id: 2, name: 'Health Department' },
    { id: 3, name: 'Transportation' },
    { id: 4, name: 'Environmental Services' },
    { id: 5, name: 'Municipal Services' },
    { id: 6, name: 'Other' }
  ];

  const priorities = [
    { value: 'low', label: 'Low', color: '#52c41a' },
    { value: 'medium', label: 'Medium', color: '#faad14' },
    { value: 'high', label: 'High', color: '#fa8c16' },
    { value: 'urgent', label: 'Urgent', color: '#f5222d' }
  ];

  const handleSubmit = async (values: CreateComplaintFormData) => {
    setLoading(true);
    try {
      await dispatch(createComplaint(values)).unwrap();
      message.success('Complaint submitted successfully!');
      navigate('/complaints');
    } catch (error) {
      message.error('Failed to submit complaint. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: true,
    beforeUpload: () => false, // Prevent auto upload
    onChange: (info: any) => {
      const { status } = info.file;
      if (status === 'done') {
        message.success(`${info.file.name} file uploaded successfully.`);
      } else if (status === 'error') {
        message.error(`${info.file.name} file upload failed.`);
      }
    },
  };

  return (
    <BasePage
      title="Create New Complaint"
      loading={loading}
      error={null}
    >
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/complaints')}
          >
            Back to Complaints
          </Button>
        </Space>

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          requiredMark={false}
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Form.Item
                name="title"
                label="Complaint Title"
                rules={[
                  { required: true, message: 'Please enter a title' },
                  { min: 10, message: 'Title must be at least 10 characters' }
                ]}
              >
                <Input placeholder="Brief summary of your complaint" />
              </Form.Item>
            </Col>

            <Col xs={24} lg={12}>
              <Form.Item
                name="category"
                label="Category"
                rules={[{ required: true, message: 'Please select a category' }]}
              >
                <Select placeholder="Select complaint category">
                  {categories.map(category => (
                    <Option key={category} value={category}>
                      {category}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col xs={24} lg={12}>
              <Form.Item
                name="department"
                label="Department"
                rules={[{ required: true, message: 'Please select a department' }]}
              >
                <Select placeholder="Select responsible department">
                  {departments.map(dept => (
                    <Option key={dept.id} value={dept.id}>
                      {dept.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col xs={24} lg={12}>
              <Form.Item
                name="priority"
                label="Priority"
                rules={[{ required: true, message: 'Please select priority' }]}
              >
                <Select placeholder="Select priority level">
                  {priorities.map(priority => (
                    <Option key={priority.value} value={priority.value}>
                      <span style={{ color: priority.color }}>
                        {priority.label}
                      </span>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col xs={24} lg={12}>
              <Form.Item
                name="location"
                label="Location (Optional)"
              >
                <Input placeholder="Specific location or address" />
              </Form.Item>
            </Col>

            <Col xs={24}>
              <Form.Item
                name="description"
                label="Detailed Description"
                rules={[
                  { required: true, message: 'Please provide a description' },
                  { min: 50, message: 'Description must be at least 50 characters' }
                ]}
              >
                <TextArea
                  rows={6}
                  placeholder="Provide detailed information about your complaint, including when it occurred, what happened, and any relevant context..."
                />
              </Form.Item>
            </Col>

            <Col xs={24}>
              <Form.Item
                name="expectedResolutionDate"
                label="Expected Resolution Date (Optional)"
              >
                <DatePicker
                  style={{ width: '100%' }}
                  placeholder="When do you expect this to be resolved?"
                />
              </Form.Item>
            </Col>

            <Col xs={24}>
              <Form.Item
                name="attachments"
                label="Attachments (Optional)"
              >
                <Dragger {...uploadProps}>
                  <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                  </p>
                  <p className="ant-upload-text">
                    Click or drag files to this area to upload
                  </p>
                  <p className="ant-upload-hint">
                    Support for images, documents, and other relevant files.
                    Maximum 10MB per file.
                  </p>
                </Dragger>
              </Form.Item>
            </Col>

            <Col xs={24}>
              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    loading={loading}
                    size="large"
                  >
                    Submit Complaint
                  </Button>
                  <Button
                    onClick={() => form.resetFields()}
                    disabled={loading}
                    size="large"
                  >
                    Reset Form
                  </Button>
                </Space>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>
    </BasePage>
  );
};

export default CreateComplaint;