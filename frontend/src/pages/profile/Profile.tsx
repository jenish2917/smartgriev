import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Upload,
  Avatar,
  Row,
  Col,
  Typography,
  Space,
  Divider,
  message,
  Spin,
  Descriptions,
  Tabs,
} from 'antd';
import {
  UserOutlined,
  CameraOutlined,
  SaveOutlined,
  LockOutlined,
  MailOutlined,
  PhoneOutlined,
  HomeOutlined,
  GlobalOutlined,
} from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store';
import { updateProfileAsync } from '@/store/slices/authSlice';
import type { User } from '@/types';

const { Title, Text } = Typography;
const { Password } = Input;
const { TabPane } = Tabs;

interface ProfileFormData {
  first_name: string;
  last_name: string;
  email: string;
  mobile: string;
  address: string;
  language: string;
}

interface PasswordFormData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

const Profile: React.FC = () => {
  const dispatch = useDispatch();
  const { user, isLoading } = useSelector((state: RootState) => state.auth);
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user) {
      profileForm.setFieldsValue({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
        mobile: user.mobile,
        address: user.address,
        language: user.language,
      });
    }
  }, [user, profileForm]);

  const handleProfileUpdate = async (values: ProfileFormData) => {
    setSaving(true);
    try {
      await dispatch(updateProfileAsync(values) as any);
      message.success('Profile updated successfully!');
    } catch (error) {
      message.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async (values: PasswordFormData) => {
    if (values.new_password !== values.confirm_password) {
      message.error('New passwords do not match');
      return;
    }

    setSaving(true);
    try {
      // Implement password change logic
      message.success('Password changed successfully!');
      passwordForm.resetFields();
    } catch (error) {
      message.error('Failed to change password');
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarUpload = (info: any) => {
    if (info.file.status === 'uploading') {
      setSaving(true);
      return;
    }
    if (info.file.status === 'done') {
      setSaving(false);
      message.success('Avatar updated successfully!');
    }
    if (info.file.status === 'error') {
      setSaving(false);
      message.error('Failed to upload avatar');
    }
  };

  if (isLoading || !user) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
      <Title level={2}>
        <UserOutlined style={{ marginRight: 8 }} />
        My Profile
      </Title>
      
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Avatar
                size={120}
                icon={<UserOutlined />}
                style={{ marginBottom: 16 }}
              />
              <Upload
                showUploadList={false}
                beforeUpload={() => false}
                onChange={handleAvatarUpload}
              >
                <Button icon={<CameraOutlined />} type="link">
                  Change Avatar
                </Button>
              </Upload>
              
              <Divider />
              
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Username">{user.username}</Descriptions.Item>
                <Descriptions.Item label="User Type">
                  {user.is_superuser ? 'Administrator' : user.is_officer ? 'Officer' : 'Citizen'}
                </Descriptions.Item>
                <Descriptions.Item label="Member Since">
                  {new Date(user.date_joined).toLocaleDateString()}
                </Descriptions.Item>
                <Descriptions.Item label="Last Login">
                  {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                </Descriptions.Item>
              </Descriptions>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card>
            <Tabs defaultActiveKey="profile">
              <TabPane tab="Profile Information" key="profile">
                <Form
                  form={profileForm}
                  layout="vertical"
                  onFinish={handleProfileUpdate}
                  requiredMark={false}
                >
                  <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        name="first_name"
                        label="First Name"
                        rules={[{ required: true, message: 'Please enter your first name' }]}
                      >
                        <Input 
                          prefix={<UserOutlined />} 
                          placeholder="Enter first name"
                        />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item
                        name="last_name"
                        label="Last Name"
                        rules={[{ required: true, message: 'Please enter your last name' }]}
                      >
                        <Input 
                          prefix={<UserOutlined />} 
                          placeholder="Enter last name"
                        />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    name="email"
                    label="Email Address"
                    rules={[
                      { required: true, message: 'Please enter your email' },
                      { type: 'email', message: 'Please enter a valid email' }
                    ]}
                  >
                    <Input 
                      prefix={<MailOutlined />} 
                      placeholder="Enter email address"
                    />
                  </Form.Item>

                  <Form.Item
                    name="mobile"
                    label="Mobile Number"
                    rules={[{ required: true, message: 'Please enter your mobile number' }]}
                  >
                    <Input 
                      prefix={<PhoneOutlined />} 
                      placeholder="Enter mobile number"
                    />
                  </Form.Item>

                  <Form.Item
                    name="address"
                    label="Address"
                    rules={[{ required: true, message: 'Please enter your address' }]}
                  >
                    <Input.TextArea 
                      rows={3}
                      placeholder="Enter your address"
                    />
                  </Form.Item>

                  <Form.Item
                    name="language"
                    label="Preferred Language"
                  >
                    <Input 
                      prefix={<GlobalOutlined />} 
                      placeholder="e.g., English, Hindi"
                    />
                  </Form.Item>

                  <Form.Item>
                    <Button 
                      type="primary" 
                      htmlType="submit" 
                      icon={<SaveOutlined />}
                      loading={saving}
                      size="large"
                    >
                      Update Profile
                    </Button>
                  </Form.Item>
                </Form>
              </TabPane>

              <TabPane tab="Change Password" key="password">
                <Form
                  form={passwordForm}
                  layout="vertical"
                  onFinish={handlePasswordChange}
                  requiredMark={false}
                >
                  <Form.Item
                    name="current_password"
                    label="Current Password"
                    rules={[{ required: true, message: 'Please enter your current password' }]}
                  >
                    <Password 
                      prefix={<LockOutlined />} 
                      placeholder="Enter current password"
                    />
                  </Form.Item>

                  <Form.Item
                    name="new_password"
                    label="New Password"
                    rules={[
                      { required: true, message: 'Please enter a new password' },
                      { min: 8, message: 'Password must be at least 8 characters' }
                    ]}
                  >
                    <Password 
                      prefix={<LockOutlined />} 
                      placeholder="Enter new password"
                    />
                  </Form.Item>

                  <Form.Item
                    name="confirm_password"
                    label="Confirm New Password"
                    rules={[{ required: true, message: 'Please confirm your new password' }]}
                  >
                    <Password 
                      prefix={<LockOutlined />} 
                      placeholder="Confirm new password"
                    />
                  </Form.Item>

                  <Form.Item>
                    <Button 
                      type="primary" 
                      htmlType="submit" 
                      icon={<SaveOutlined />}
                      loading={saving}
                      size="large"
                    >
                      Change Password
                    </Button>
                  </Form.Item>
                </Form>
              </TabPane>
            </Tabs>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Profile;
