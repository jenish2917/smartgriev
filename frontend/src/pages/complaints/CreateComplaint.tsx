import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation('complaints');

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
      message.success(t('create.successMessage'));
      navigate('/complaints');
    } catch (error) {
      message.error(t('create.errorMessage'));
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
      title={t('create.title')}
      loading={loading}
      error={null}
    >
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/complaints')}
          >
            {t('create.backButton')}
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
                label={t('create.titleLabel')}
                rules={[
                  { required: true, message: t('create.titleRequired') },
                  { min: 10, message: t('create.titleMinLength') }
                ]}
              >
                <Input placeholder={t('create.titlePlaceholder')} />
              </Form.Item>
            </Col>

            <Col xs={24} lg={12}>
              <Form.Item
                name="category"
                label={t('create.categoryLabel')}
                rules={[{ required: true, message: t('create.categoryRequired') }]}
              >
                <Select placeholder={t('create.categoryPlaceholder')}>
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
                label={t('create.departmentLabel')}
                rules={[{ required: true, message: t('create.departmentRequired') }]}
              >
                <Select placeholder={t('create.departmentPlaceholder')}>
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
                label={t('create.priorityLabel')}
                rules={[{ required: true, message: t('create.priorityRequired') }]}
              >
                <Select placeholder={t('create.priorityPlaceholder')}>
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
                label={t('create.locationLabel')}
              >
                <Input placeholder={t('create.locationPlaceholder')} />
              </Form.Item>
            </Col>

            <Col xs={24}>
              <Form.Item
                name="description"
                label={t('create.descriptionLabel')}
                rules={[
                  { required: true, message: t('create.descriptionRequired') },
                  { min: 50, message: t('create.descriptionMinLength') }
                ]}
              >
                <TextArea
                  rows={6}
                  placeholder={t('create.descriptionPlaceholder')}
                />
              </Form.Item>
            </Col>

            <Col xs={24}>
              <Form.Item
                name="expectedResolutionDate"
                label={t('create.expectedDateLabel')}
              >
                <DatePicker
                  style={{ width: '100%' }}
                  placeholder={t('create.expectedDatePlaceholder')}
                />
              </Form.Item>
            </Col>

            <Col xs={24}>
              <Form.Item
                name="attachments"
                label={t('create.attachmentsLabel')}
              >
                <Dragger {...uploadProps}>
                  <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                  </p>
                  <p className="ant-upload-text">
                    {t('create.uploadText')}
                  </p>
                  <p className="ant-upload-hint">
                    {t('create.uploadHint')}
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
                    {t('create.submitButton')}
                  </Button>
                  <Button
                    onClick={() => form.resetFields()}
                    disabled={loading}
                    size="large"
                  >
                    {t('create.resetButton')}
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