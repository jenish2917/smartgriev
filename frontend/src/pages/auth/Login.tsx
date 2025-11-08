import React from 'react';
import { Form, Input, Button, Typography, Alert, Checkbox } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const { Title, Text } = Typography;

interface LoginFormData {
  username: string;
  password: string;
  remember: boolean;
}

const Login: React.FC = () => {
  const { t } = useTranslation('auth');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const onFinish = async (values: LoginFormData) => {
    setLoading(true);
    setError(null);
    
    try {
      // Implement login logic here
      console.log('Login values:', values);
      // await dispatch(loginAsync({ username: values.username, password: values.password }));
    } catch (err) {
      setError(t('loginError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Title level={3} style={{ textAlign: 'center', marginBottom: '24px' }}>
        {t('login')}
      </Title>

      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginBottom: '16px' }}
        />
      )}

      <Form
        name="login"
        onFinish={onFinish}
        layout="vertical"
        requiredMark={false}
      >
        <Form.Item
          name="username"
          rules={[
            { required: true, message: t('invalidCredentials') },
            { min: 3, message: t('invalidFormat') },
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder={t('username')}
            size="large"
          />
        </Form.Item>

        <Form.Item
          name="password"
          rules={[
            { required: true, message: t('invalidCredentials') },
            { min: 6, message: t('invalidFormat') },
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder={t('password')}
            size="large"
          />
        </Form.Item>

        <Form.Item>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>{t('rememberMe')}</Checkbox>
            </Form.Item>
            <Link to="/forgot-password">{t('forgotPassword')}</Link>
          </div>
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            size="large"
            loading={loading}
            style={{ width: '100%' }}
          >
            {t('loginButton')}
          </Button>
        </Form.Item>

        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">
            {t('dontHaveAccount')} <Link to="/register">{t('signUpHere')}</Link>
          </Text>
        </div>
      </Form>
    </div>
  );
};

export default Login;
