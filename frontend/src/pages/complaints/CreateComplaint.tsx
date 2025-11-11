import React, { useState, useEffect } from 'react';
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
import axios from 'axios';
import { API_URLS } from '@/config/api.config';

const { Option } = Select;
const { TextArea } = Input;
const { Dragger } = Upload;

interface CreateComplaintFormData {
  title: string;
  description: string;
  category: string;
  department: number;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  urgency_level: 'low' | 'medium' | 'high' | 'critical'; // NEW
  location?: string;
  incident_latitude?: number; // NEW
  incident_longitude?: number; // NEW
  incident_address?: string; // NEW
  incident_landmark?: string; // NEW
  gps_accuracy?: number; // NEW
  location_method?: 'gps' | 'manual' | 'address' | 'plus_code'; // NEW
  plus_code?: string; // NEW
  area_type?: 'residential' | 'commercial' | 'industrial' | 'public' | 'road' | 'park' | 'other'; // NEW
  submitted_language?: string; // NEW
  audio_file?: File; // NEW
  image_file?: File; // NEW
  expectedResolutionDate?: string;
  attachments?: File[];
}

const CreateComplaint: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [useGPS, setUseGPS] = useState(false);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [categories, setCategories] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [loadingMetadata, setLoadingMetadata] = useState(true);
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { t } = useTranslation('complaints');

  // Fetch categories and departments from API on component mount
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [categoriesRes, departmentsRes] = await Promise.all([
          axios.get(API_URLS.COMPLAINT_CATEGORIES),
          axios.get(API_URLS.COMPLAINT_DEPARTMENTS)
        ]);
        
        setCategories(categoriesRes.data.categories || []);
        setDepartments(departmentsRes.data.departments || []);
      } catch (error) {
        console.error('Error fetching metadata:', error);
        message.error('Failed to load categories/departments. Using defaults.');
        // Fallback to hardcoded values if API fails
        setCategories([
          { id: 1, name: 'Infrastructure' },
          { id: 2, name: 'Public Services' },
          { id: 3, name: 'Environment' },
          { id: 4, name: 'Transportation' },
          { id: 5, name: 'Health & Safety' },
          { id: 6, name: 'Education' },
          { id: 7, name: 'Other' }
        ]);
        setDepartments([
          { id: 1, name: 'Public Works' },
          { id: 2, name: 'Health Department' },
          { id: 3, name: 'Transportation' },
          { id: 4, name: 'Environmental Services' },
          { id: 5, name: 'Municipal Services' },
          { id: 6, name: 'Other' }
        ]);
      } finally {
        setLoadingMetadata(false);
      }
    };

    fetchMetadata();
  }, []);

  const priorities = [
    { value: 'low', label: 'Low', color: '#52c41a' },
    { value: 'medium', label: 'Medium', color: '#faad14' },
    { value: 'high', label: 'High', color: '#fa8c16' },
    { value: 'urgent', label: 'Urgent', color: '#f5222d' }
  ];

  const urgencyLevels = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' }
  ];

  const areaTypes = [
    { value: 'residential', label: 'Residential Area' },
    { value: 'commercial', label: 'Commercial Area' },
    { value: 'industrial', label: 'Industrial Area' },
    { value: 'public', label: 'Public Space' },
    { value: 'road', label: 'Road/Highway' },
    { value: 'park', label: 'Park/Garden' },
    { value: 'other', label: 'Other' }
  ];

  const languages = [
    { value: 'en', label: 'English' },
    { value: 'hi', label: 'हिन्दी (Hindi)' },
    { value: 'mr', label: 'मराठी (Marathi)' },
    { value: 'ta', label: 'தமிழ் (Tamil)' },
    { value: 'te', label: 'తెలుగు (Telugu)' },
    { value: 'bn', label: 'বাংলা (Bengali)' },
    { value: 'gu', label: 'ગુજરાતી (Gujarati)' },
    { value: 'kn', label: 'ಕನ್ನಡ (Kannada)' },
    { value: 'ml', label: 'മലയാളം (Malayalam)' },
    { value: 'pa', label: 'ਪੰਜਾਬੀ (Punjabi)' },
    { value: 'ur', label: 'اردو (Urdu)' },
    { value: 'or', label: 'ଓଡ଼ିଆ (Odia)' }
  ];

  const getCurrentLocation = () => {
    setGpsLoading(true);
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude, accuracy } = position.coords;
          form.setFieldsValue({
            incident_latitude: latitude,
            incident_longitude: longitude,
            gps_accuracy: accuracy,
            location_method: 'gps'
          });
          message.success(`Location captured: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
          setGpsLoading(false);
        },
        (error) => {
          message.error(`GPS Error: ${error.message}`);
          setGpsLoading(false);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    } else {
      message.error('Geolocation is not supported by your browser');
      setGpsLoading(false);
    }
  };

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
                <Select placeholder={t('create.categoryPlaceholder')} loading={loadingMetadata}>
                  {categories.map(category => (
                    <Option key={category.id || category.name || category} value={category.name || category}>
                      {category.name || category}
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
                <Select placeholder={t('create.departmentPlaceholder')} loading={loadingMetadata}>
                  {departments.map(dept => (
                    <Option key={dept.id} value={dept.id}>
                      {dept.name} {dept.zone ? `- ${dept.zone}` : ''}
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
                name="urgency_level"
                label="Urgency Level"
                rules={[{ required: true, message: 'Please select urgency level' }]}
              >
                <Select placeholder="Select urgency level">
                  {urgencyLevels.map(level => (
                    <Option key={level.value} value={level.value}>
                      {level.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col xs={24} lg={12}>
              <Form.Item
                name="submitted_language"
                label="Complaint Language"
                initialValue="en"
              >
                <Select placeholder="Select language">
                  {languages.map(lang => (
                    <Option key={lang.value} value={lang.value}>
                      {lang.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col xs={24} lg={12}>
              <Form.Item
                name="area_type"
                label="Area Type"
              >
                <Select placeholder="Select area type">
                  {areaTypes.map(type => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col xs={24}>
              <Card title="📍 Location Details" size="small" style={{ marginBottom: 16 }}>
                <Row gutter={[16, 16]}>
                  <Col xs={24}>
                    <Space>
                      <Button
                        type="primary"
                        onClick={getCurrentLocation}
                        loading={gpsLoading}
                        icon={<span>📍</span>}
                      >
                        Get Current GPS Location
                      </Button>
                    </Space>
                  </Col>

                  <Col xs={24} lg={12}>
                    <Form.Item
                      name="incident_latitude"
                      label="Latitude"
                    >
                      <Input type="number" step="0.000001" placeholder="19.0760" />
                    </Form.Item>
                  </Col>

                  <Col xs={24} lg={12}>
                    <Form.Item
                      name="incident_longitude"
                      label="Longitude"
                    >
                      <Input type="number" step="0.000001" placeholder="72.8777" />
                    </Form.Item>
                  </Col>

                  <Col xs={24} lg={12}>
                    <Form.Item
                      name="incident_address"
                      label="Incident Address"
                    >
                      <Input placeholder="Full address of incident location" />
                    </Form.Item>
                  </Col>

                  <Col xs={24} lg={12}>
                    <Form.Item
                      name="incident_landmark"
                      label="Nearby Landmark"
                    >
                      <Input placeholder="Nearby landmark for reference" />
                    </Form.Item>
                  </Col>

                  <Col xs={24} lg={12}>
                    <Form.Item
                      name="plus_code"
                      label="Plus Code (Optional)"
                    >
                      <Input placeholder="e.g., 7JMM23GQ+2G" />
                    </Form.Item>
                  </Col>

                  <Col xs={24} lg={12}>
                    <Form.Item
                      name="gps_accuracy"
                      label="GPS Accuracy (meters)"
                    >
                      <Input type="number" disabled placeholder="Auto-filled from GPS" />
                    </Form.Item>
                  </Col>
                </Row>
              </Card>
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

            <Col xs={24} lg={12}>
              <Form.Item
                name="audio_file"
                label="🎤 Audio Recording (Optional)"
              >
                <Upload
                  accept="audio/*"
                  maxCount={1}
                  beforeUpload={() => false}
                >
                  <Button icon={<InboxOutlined />}>
                    Upload Audio File
                  </Button>
                </Upload>
              </Form.Item>
            </Col>

            <Col xs={24} lg={12}>
              <Form.Item
                name="image_file"
                label="📷 Image/Photo (Optional)"
              >
                <Upload
                  accept="image/*"
                  maxCount={1}
                  beforeUpload={() => false}
                  listType="picture"
                >
                  <Button icon={<InboxOutlined />}>
                    Upload Image File
                  </Button>
                </Upload>
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