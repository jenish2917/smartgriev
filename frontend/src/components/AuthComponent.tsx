import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  message,
  Space,
  Typography,
  Tabs,
  Row,
  Col,
  Steps,
  Alert,
  Divider,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  PhoneOutlined,
  MailOutlined,
  SafetyOutlined,
  GoogleOutlined,
  LoginOutlined,
  UserAddOutlined,
} from '@ant-design/icons';
import { apiService, handleApiError } from '@/services/api';
import type { AuthRequest, AuthResponse } from '@/services/api';
import { AxiosError } from 'axios';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { Step } = Steps;

interface AuthComponentProps {
  onAuthSuccess?: (response: AuthResponse) => void;
  defaultTab?: 'login' | 'register';
}

interface LoginFormData {
  identifier: string;
  password: string;
}

interface RegisterFormData {
  first_name: string;
  last_name: string;
  phone_number: string;
  email: string;
  password: string;
  confirm_password: string;
}

interface OTPFormData {
  otp_code: string;
}

export const AuthComponent: React.FC<AuthComponentProps> = ({
  onAuthSuccess,
  defaultTab = 'login',
}) => {
  const [loginForm] = Form.useForm();
  const [registerForm] = Form.useForm();
  const [otpForm] = Form.useForm();
  
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(defaultTab);
  const [authStep, setAuthStep] = useState(0); // 0: form, 1: otp
  const [pendingAuth, setPendingAuth] = useState<{
    user_id: string;
    otp_type: string;
    contact: string;
  } | null>(null);

  const handleLogin = async (values: LoginFormData) => {
    setLoading(true);
    try {
      const response = await apiService.login({
        username: values.identifier,
        password: values.password,
      });

      if (response.success) {
        if (response.requires_otp) {
          setPendingAuth({
            user_id: response.user_id!,
            otp_type: 'login',
            contact: response.otp_sent_to || values.identifier,
          });
          setAuthStep(1);
          message.success(`OTP sent to ${response.otp_sent_to}`);
        } else {
          message.success('Login successful!');
          if (onAuthSuccess) {
            onAuthSuccess(response);
          }
        }
      } else {
        message.error(response.message);
      }
    } catch (error) {
      message.error(handleApiError(error as AxiosError));
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values: RegisterFormData) => {
    if (values.password !== values.confirm_password) {
      message.error('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.register({
        first_name: values.first_name,
        last_name: values.last_name,
        phone: values.phone_number,
        email: values.email,
        password: values.password,
      });

      if (response.success) {
        setPendingAuth({
          user_id: response.user_id!,
          otp_type: 'registration',
          contact: response.otp_sent_to || values.email,
        });
        setAuthStep(1);
        message.success(`Registration successful! OTP sent to ${response.otp_sent_to}`);
      } else {
        message.error(response.message);
      }
    } catch (error) {
      message.error(handleApiError(error as AxiosError));
    } finally {
      setLoading(false);
    }
  };

  const handleOTPVerification = async (values: OTPFormData) => {
    if (!pendingAuth) return;

    setLoading(true);
    try {
      const response = await apiService.verifyOTP({
        phone: pendingAuth.contact,
        otp: values.otp_code,
      });

      if (response.success) {
        message.success('Verification successful!');
        if (onAuthSuccess) {
          onAuthSuccess(response);
        }
      } else {
        message.error(response.message);
      }
    } catch (error) {
      message.error(handleApiError(error as AxiosError));
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    if (!pendingAuth) return;

    setLoading(true);
    try {
      const response = await apiService.sendOTP({
        phone: pendingAuth.contact,
      });

      if (response.success) {
        message.success('OTP resent successfully!');
      } else {
        message.error(response.message);
      }
    } catch (error) {
      message.error(handleApiError(error as AxiosError));
    } finally {
      setLoading(false);
    }
  };

  const resetAuth = () => {
    setAuthStep(0);
    setPendingAuth(null);
    loginForm.resetFields();
    registerForm.resetFields();
    otpForm.resetFields();
  };

  const renderLoginForm = () => (
    <Form
      form={loginForm}
      layout="vertical"
      onFinish={handleLogin}
      requiredMark={false}
    >
      <Form.Item
        label="Phone Number, Email, or Username"
        name="identifier"
        rules={[{ required: true, message: 'Please enter your login credentials' }]}
      >
        <Input
          prefix={<UserOutlined />}
          placeholder="Enter phone number, email, or username"
          size="large"
        />
      </Form.Item>

      <Form.Item
        label="Password"
        name="password"
        rules={[{ required: true, message: 'Please enter your password' }]}
      >
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="Enter your password"
          size="large"
        />
      </Form.Item>

      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          icon={<LoginOutlined />}
          size="large"
          loading={loading}
          block
        >
          Login
        </Button>
      </Form.Item>
    </Form>
  );

  const renderRegisterForm = () => (
    <Form
      form={registerForm}
      layout="vertical"
      onFinish={handleRegister}
      requiredMark={false}
    >
      <Row gutter={[12, 0]}>
        <Col span={12}>
          <Form.Item
            label="First Name"
            name="first_name"
            rules={[{ required: true, message: 'Please enter your first name' }]}
          >
            <Input placeholder="First Name" size="large" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            label="Last Name"
            name="last_name"
            rules={[{ required: true, message: 'Please enter your last name' }]}
          >
            <Input placeholder="Last Name" size="large" />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item
        label="Phone Number"
        name="phone_number"
        rules={[
          { required: true, message: 'Please enter your phone number' },
          { pattern: /^\+?[1-9]\d{9,14}$/, message: 'Please enter a valid phone number' }
        ]}
      >
        <Input
          prefix={<PhoneOutlined />}
          placeholder="+91 9876543210"
          size="large"
        />
      </Form.Item>

      <Form.Item
        label="Email Address"
        name="email"
        rules={[
          { required: true, message: 'Please enter your email' },
          { type: 'email', message: 'Please enter a valid email' }
        ]}
      >
        <Input
          prefix={<MailOutlined />}
          placeholder="your.email@example.com"
          size="large"
        />
      </Form.Item>

      <Form.Item
        label="Password"
        name="password"
        rules={[
          { required: true, message: 'Please enter a password' },
          { min: 8, message: 'Password must be at least 8 characters' }
        ]}
      >
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="Enter password (min 8 characters)"
          size="large"
        />
      </Form.Item>

      <Form.Item
        label="Confirm Password"
        name="confirm_password"
        rules={[{ required: true, message: 'Please confirm your password' }]}
      >
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="Confirm your password"
          size="large"
        />
      </Form.Item>

      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          icon={<UserAddOutlined />}
          size="large"
          loading={loading}
          block
        >
          Register
        </Button>
      </Form.Item>
    </Form>
  );

  const renderOTPForm = () => (
    <div>
      <Alert
        message="OTP Verification Required"
        description={`We've sent a 6-digit verification code to ${pendingAuth?.contact}`}
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Form
        form={otpForm}
        layout="vertical"
        onFinish={handleOTPVerification}
        requiredMark={false}
      >
        <Form.Item
          label="Enter OTP Code"
          name="otp_code"
          rules={[
            { required: true, message: 'Please enter the OTP code' },
            { len: 6, message: 'OTP must be 6 digits' },
            { pattern: /^\d{6}$/, message: 'OTP must contain only numbers' }
          ]}
        >
          <Input
            prefix={<SafetyOutlined />}
            placeholder="Enter 6-digit OTP"
            maxLength={6}
            size="large"
            style={{ textAlign: 'center', letterSpacing: '0.5em' }}
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            icon={<SafetyOutlined />}
            size="large"
            loading={loading}
            block
          >
            Verify OTP
          </Button>
        </Form.Item>

        <Form.Item>
          <Space style={{ width: '100%', justifyContent: 'center' }}>
            <Button type="link" onClick={handleResendOTP} loading={loading}>
              Resend OTP
            </Button>
            <Button type="link" onClick={resetAuth}>
              Back to Login
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </div>
  );

  const renderGoogleAuth = () => (
    <div>
      <Divider>OR</Divider>
      <Button
        icon={<GoogleOutlined />}
        size="large"
        block
        onClick={() => {
          message.info('Google OAuth integration coming soon!');
        }}
      >
        Continue with Google
      </Button>
    </div>
  );

  if (authStep === 1) {
    return (
      <div className="max-w-md mx-auto p-4">
        <Card>
          <Steps current={1} size="small" style={{ marginBottom: 24 }}>
            <Step title="Credentials" />
            <Step title="Verification" />
          </Steps>
          {renderOTPForm()}
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto p-4">
      <Card>
        <div className="text-center mb-6">
          <Title level={3}>SmartGriev</Title>
          <Text type="secondary">Secure Citizen Complaint System</Text>
        </div>

        <Tabs
          activeKey={activeTab}
          onChange={(activeKey) => setActiveTab(activeKey as 'login' | 'register')}
          centered
          size="large"
        >
          <TabPane tab="Login" key="login">
            {renderLoginForm()}
            {renderGoogleAuth()}
            <div className="text-center mt-4">
              <Text type="secondary">
                Don't have an account?{' '}
                <Button type="link" onClick={() => setActiveTab('register')}>
                  Register here
                </Button>
              </Text>
            </div>
          </TabPane>

          <TabPane tab="Register" key="register">
            {renderRegisterForm()}
            {renderGoogleAuth()}
            <div className="text-center mt-4">
              <Text type="secondary">
                Already have an account?{' '}
                <Button type="link" onClick={() => setActiveTab('login')}>
                  Login here
                </Button>
              </Text>
            </div>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default AuthComponent;