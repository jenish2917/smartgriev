import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Switch,
  Select,
  Row,
  Col,
  Typography,
  Space,
  Divider,
  Alert,
  Tabs,
  Upload,
  Avatar,
  message,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  BellOutlined,
  GlobalOutlined,
  SecurityScanOutlined,
  MobileOutlined,
  MailOutlined,
  CameraOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import type { TabsProps } from 'antd';

const { Title, Text } = Typography;
const { Password } = Input;

interface UserSettings {
  // Profile
  first_name: string;
  last_name: string;
  email: string;
  mobile: string;
  address: string;
  language: string;
  
  // Notifications
  email_notifications: boolean;
  sms_notifications: boolean;
  push_notifications: boolean;
  complaint_updates: boolean;
  system_alerts: boolean;
  
  // Privacy
  profile_visibility: 'public' | 'private';
  data_sharing: boolean;
  analytics_tracking: boolean;
  
  // Security
  two_factor_enabled: boolean;
  login_alerts: boolean;
  session_timeout: number;
}

const Settings: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [loading, setLoading] = useState(false);
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [notificationForm] = Form.useForm();
  const [securityForm] = Form.useForm();

  const [settings, setSettings] = useState<UserSettings>({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    mobile: user?.mobile || '',
    address: user?.address || '',
    language: user?.language || 'en',
    email_notifications: true,
    sms_notifications: false,
    push_notifications: true,
    complaint_updates: true,
    system_alerts: true,
    profile_visibility: 'private',
    data_sharing: false,
    analytics_tracking: true,
    two_factor_enabled: false,
    login_alerts: true,
    session_timeout: 30,
  });

  const languageOptions = [
    { value: 'en', label: 'English' },
    { value: 'hi', label: 'हिंदी (Hindi)' },
    { value: 'mr', label: 'मराठी (Marathi)' },
    { value: 'gu', label: 'ગુજરાતી (Gujarati)' },
    { value: 'ta', label: 'தமிழ் (Tamil)' },
    { value: 'te', label: 'తెలుగు (Telugu)' },
    { value: 'kn', label: 'ಕನ್ನಡ (Kannada)' },
    { value: 'ml', label: 'മലയാളം (Malayalam)' },
    { value: 'bn', label: 'বাংলা (Bengali)' },
    { value: 'pa', label: 'ਪੰਜਾਬੀ (Punjabi)' },
  ];

  useEffect(() => {
    // Initialize forms with current settings
    profileForm.setFieldsValue(settings);
    notificationForm.setFieldsValue(settings);
    securityForm.setFieldsValue(settings);
  }, [settings, profileForm, notificationForm, securityForm]);

  const handleProfileSave = async (values: any) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSettings(prev => ({ ...prev, ...values }));
      message.success('Profile updated successfully');
    } catch (error) {
      message.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (values: any) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      message.success('Password changed successfully');
      passwordForm.resetFields();
    } catch (error) {
      message.error('Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationSave = async (values: any) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSettings(prev => ({ ...prev, ...values }));
      message.success('Notification preferences saved');
    } catch (error) {
      message.error('Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleSecuritySave = async (values: any) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSettings(prev => ({ ...prev, ...values }));
      message.success('Security settings updated');
    } catch (error) {
      message.error('Failed to update security settings');
    } finally {
      setLoading(false);
    }
  };

  const uploadProps = {
    name: 'avatar',
    listType: 'picture-card' as const,
    className: 'avatar-uploader',
    showUploadList: false,
    beforeUpload: (file: any) => {
      const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
      if (!isJpgOrPng) {
        message.error('You can only upload JPG/PNG file!');
      }
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        message.error('Image must smaller than 2MB!');
      }
      return isJpgOrPng && isLt2M;
    },
    onChange: (info: any) => {
      if (info.file.status === 'done') {
        message.success('Avatar uploaded successfully');
      }
    },
  };

  const tabItems: TabsProps['items'] = [
    {
      key: 'profile',
      label: 'Profile',
      icon: <UserOutlined />,
      children: (
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <Card>
              <Space direction="vertical" align="center" style={{ width: '100%' }}>
                <Upload {...uploadProps}>
                  <Avatar size={120} icon={<UserOutlined />} />
                  <div style={{ marginTop: 8 }}>
                    <Button icon={<CameraOutlined />} type="text">
                      Change Photo
                    </Button>
                  </div>
                </Upload>
                <div style={{ textAlign: 'center' }}>
                  <Title level={4} style={{ margin: 0 }}>
                    {settings.first_name} {settings.last_name}
                  </Title>
                  <Text type="secondary">{settings.email}</Text>
                  {user?.is_officer && (
                    <div style={{ marginTop: 8 }}>
                      <Text strong style={{ color: '#FF6600' }}>
                        Government Officer
                      </Text>
                    </div>
                  )}
                </div>
              </Space>
            </Card>
          </Col>
          <Col xs={24} md={16}>
            <Card title="Personal Information">
              <Form
                form={profileForm}
                layout="vertical"
                onFinish={handleProfileSave}
              >
                <Row gutter={16}>
                  <Col xs={24} md={12}>
                    <Form.Item
                      label="First Name"
                      name="first_name"
                      rules={[{ required: true, message: 'Please enter your first name' }]}
                    >
                      <Input />
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={12}>
                    <Form.Item
                      label="Last Name"
                      name="last_name"
                      rules={[{ required: true, message: 'Please enter your last name' }]}
                    >
                      <Input />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col xs={24} md={12}>
                    <Form.Item
                      label="Email"
                      name="email"
                      rules={[
                        { required: true, message: 'Please enter your email' },
                        { type: 'email', message: 'Please enter a valid email' }
                      ]}
                    >
                      <Input prefix={<MailOutlined />} />
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={12}>
                    <Form.Item
                      label="Mobile Number"
                      name="mobile"
                      rules={[{ required: true, message: 'Please enter your mobile number' }]}
                    >
                      <Input prefix={<MobileOutlined />} />
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item
                  label="Address"
                  name="address"
                >
                  <Input.TextArea rows={3} />
                </Form.Item>

                <Form.Item
                  label="Preferred Language"
                  name="language"
                >
                  <Select options={languageOptions} />
                </Form.Item>

                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                    Save Changes
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: 'security',
      label: 'Security',
      icon: <LockOutlined />,
      children: (
        <Row gutter={[24, 24]}>
          <Col xs={24} md={12}>
            <Card title="Change Password">
              <Form
                form={passwordForm}
                layout="vertical"
                onFinish={handlePasswordChange}
              >
                <Form.Item
                  label="Current Password"
                  name="current_password"
                  rules={[{ required: true, message: 'Please enter your current password' }]}
                >
                  <Password />
                </Form.Item>

                <Form.Item
                  label="New Password"
                  name="new_password"
                  rules={[
                    { required: true, message: 'Please enter a new password' },
                    { min: 8, message: 'Password must be at least 8 characters' }
                  ]}
                >
                  <Password />
                </Form.Item>

                <Form.Item
                  label="Confirm New Password"
                  name="confirm_password"
                  dependencies={['new_password']}
                  rules={[
                    { required: true, message: 'Please confirm your new password' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('new_password') === value) {
                          return Promise.resolve();
                        }
                        return Promise.reject(new Error('Passwords do not match'));
                      },
                    }),
                  ]}
                >
                  <Password />
                </Form.Item>

                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading}>
                    Change Password
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card title="Security Settings">
              <Form
                form={securityForm}
                layout="vertical"
                onFinish={handleSecuritySave}
              >
                <Form.Item
                  label="Two-Factor Authentication"
                  name="two_factor_enabled"
                  valuePropName="checked"
                >
                  <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                </Form.Item>

                <Form.Item
                  label="Login Alerts"
                  name="login_alerts"
                  valuePropName="checked"
                >
                  <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                </Form.Item>

                <Form.Item
                  label="Session Timeout (minutes)"
                  name="session_timeout"
                >
                  <Select>
                    <Select.Option value={15}>15 minutes</Select.Option>
                    <Select.Option value={30}>30 minutes</Select.Option>
                    <Select.Option value={60}>1 hour</Select.Option>
                    <Select.Option value={120}>2 hours</Select.Option>
                  </Select>
                </Form.Item>

                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} icon={<SecurityScanOutlined />}>
                    Update Security
                  </Button>
                </Form.Item>
              </Form>

              <Divider />

              <Alert
                message="Security Recommendations"
                description={
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    <li>Enable two-factor authentication for enhanced security</li>
                    <li>Use a strong, unique password</li>
                    <li>Regularly review your account activity</li>
                    <li>Don't share your login credentials</li>
                  </ul>
                }
                type="info"
                showIcon
              />
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: 'notifications',
      label: 'Notifications',
      icon: <BellOutlined />,
      children: (
        <Card title="Notification Preferences">
          <Form
            form={notificationForm}
            layout="vertical"
            onFinish={handleNotificationSave}
          >
            <Row gutter={[24, 24]}>
              <Col xs={24} md={12}>
                <div>
                  <Title level={5}>Delivery Methods</Title>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Form.Item
                      label="Email Notifications"
                      name="email_notifications"
                      valuePropName="checked"
                    >
                      <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                    </Form.Item>

                    <Form.Item
                      label="SMS Notifications"
                      name="sms_notifications"
                      valuePropName="checked"
                    >
                      <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                    </Form.Item>

                    <Form.Item
                      label="Push Notifications"
                      name="push_notifications"
                      valuePropName="checked"
                    >
                      <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                    </Form.Item>
                  </Space>
                </div>
              </Col>
              <Col xs={24} md={12}>
                <div>
                  <Title level={5}>Notification Types</Title>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Form.Item
                      label="Complaint Updates"
                      name="complaint_updates"
                      valuePropName="checked"
                    >
                      <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                    </Form.Item>

                    <Form.Item
                      label="System Alerts"
                      name="system_alerts"
                      valuePropName="checked"
                    >
                      <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                    </Form.Item>
                  </Space>
                </div>
              </Col>
            </Row>

            <Divider />

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} icon={<BellOutlined />}>
                Save Preferences
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'privacy',
      label: 'Privacy',
      icon: <GlobalOutlined />,
      children: (
        <Card title="Privacy Settings">
          <Alert
            message="Data Privacy"
            description="Control how your data is used and shared within the SmartGriev system."
            type="info"
            showIcon
            style={{ marginBottom: 24 }}
          />

          <Form
            layout="vertical"
            initialValues={settings}
            onFinish={(values) => {
              setSettings(prev => ({ ...prev, ...values }));
              message.success('Privacy settings updated');
            }}
          >
            <Form.Item
              label="Profile Visibility"
              name="profile_visibility"
            >
              <Select>
                <Select.Option value="public">Public - Visible to all users</Select.Option>
                <Select.Option value="private">Private - Only visible to officials</Select.Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="Data Sharing"
              name="data_sharing"
              valuePropName="checked"
            >
              <Switch 
                checkedChildren="Allow" 
                unCheckedChildren="Block"
              />
            </Form.Item>
            <Text type="secondary" style={{ marginTop: -16, display: 'block', marginBottom: 16 }}>
              Allow anonymized data to be used for improving government services
            </Text>

            <Form.Item
              label="Analytics Tracking"
              name="analytics_tracking"
              valuePropName="checked"
            >
              <Switch 
                checkedChildren="Enable" 
                unCheckedChildren="Disable"
              />
            </Form.Item>
            <Text type="secondary" style={{ marginTop: -16, display: 'block', marginBottom: 16 }}>
              Help improve the platform by sharing usage analytics
            </Text>

            <Form.Item>
              <Button type="primary" htmlType="submit" icon={<GlobalOutlined />}>
                Update Privacy Settings
              </Button>
            </Form.Item>
          </Form>

          <Divider />

          <div>
            <Title level={5}>Data Management</Title>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button type="default">
                Download My Data
              </Button>
              <Button type="default">
                Request Data Deletion
              </Button>
              <Text type="secondary">
                You can request a copy of your data or request deletion in accordance with data protection regulations.
              </Text>
            </Space>
          </div>
        </Card>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={2} className="gov-title">
          Account Settings
        </Title>
        <Text className="gov-subtitle">
          Manage your profile, security, and preferences
        </Text>
      </div>

      <Card>
        <Tabs
          defaultActiveKey="profile"
          items={tabItems}
          tabPosition="left"
        />
      </Card>
    </div>
  );
};

export default Settings;
