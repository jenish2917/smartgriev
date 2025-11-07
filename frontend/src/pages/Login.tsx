import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../styles/theme';
import axios from 'axios';

const LoginContainer = styled.div`
  min-height: 100vh;
  display: flex;
  padding-top: 70px;
  background: linear-gradient(135deg, ${theme.colors.primary[700]} 0%, ${theme.colors.primary[400]} 100%);
  padding-left: ${theme.spacing.md};
  padding-right: ${theme.spacing.md};

  @media (max-width: 768px) {
    padding-top: 60px;
    padding-left: ${theme.spacing.sm};
    padding-right: ${theme.spacing.sm};
  }
`;

const LoginBox = styled.div`
  margin: auto;
  background: ${theme.colors.white.pure};
  padding: ${theme.spacing.xxl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.xl};
  max-width: 450px;
  width: 100%;

  @media (max-width: 768px) {
    padding: ${theme.spacing.xl};
    max-width: 100%;
  }

  @media (max-width: 480px) {
    padding: ${theme.spacing.lg};
    border-radius: ${theme.borderRadius.lg};
  }
`;

const Logo = styled.div`
  text-align: center;
  margin-bottom: ${theme.spacing.xl};
`;

const LogoIcon = styled.div`
  width: 80px;
  height: 80px;
  background: ${theme.colors.primary[500]};
  border-radius: ${theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: ${theme.colors.white.pure};
  margin: 0 auto ${theme.spacing.md} auto;
  font-weight: 900;

  @media (max-width: 480px) {
    width: 60px;
    height: 60px;
    font-size: 30px;
  }
`;

const Title = styled.h1`
  font-family: ${theme.fonts.heading};
  font-size: 28px;
  font-weight: 700;
  color: ${theme.colors.primary[800]};
  text-align: center;
  margin: 0 0 ${theme.spacing.sm} 0;

  @media (max-width: 480px) {
    font-size: 24px;
  }
`;

const Subtitle = styled.p`
  text-align: center;
  color: ${theme.colors.text.secondary};
  font-size: 14px;
  margin: 0 0 ${theme.spacing.xl} 0;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.lg};
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.sm};
`;

const Label = styled.label`
  font-weight: 600;
  color: ${theme.colors.primary[800]};
  font-size: 14px;
`;

const Input = styled.input`
  padding: ${theme.spacing.md};
  border: 2px solid ${theme.colors.primary[200]};
  border-radius: ${theme.borderRadius.md};
  font-size: 16px;
  transition: all ${theme.transitions.fast};
  min-height: 48px;

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary[500]};
    box-shadow: 0 0 0 3px ${theme.colors.primary[100]};
  }

  @media (max-width: 480px) {
    font-size: 16px; /* Prevent zoom on iOS */
    min-height: 50px;
  }
`;

const Button = styled.button<{ $loading?: boolean }>`
  padding: ${theme.spacing.md};
  background: ${theme.colors.primary[500]};
  color: ${theme.colors.white.pure};
  border: none;
  border-radius: ${theme.borderRadius.md};
  font-weight: 600;
  font-size: 16px;
  cursor: ${props => props.$loading ? 'not-allowed' : 'pointer'};
  transition: all ${theme.transitions.fast};
  min-height: 48px;

  @media (max-width: 480px) {
    min-height: 50px;
  }

  &:active {
    transform: scale(0.98);
  }
  opacity: ${props => props.$loading ? 0.7 : 1};

  &:hover {
    background: ${theme.colors.primary[700]};
    transform: ${props => props.$loading ? 'none' : 'translateY(-2px)'};
    box-shadow: ${props => props.$loading ? 'none' : theme.shadows.lg};
  }
`;

const ForgotPassword = styled(Link)`
  text-align: center;
  color: ${theme.colors.primary[600]};
  font-size: 14px;
  text-decoration: none;
  margin-top: ${theme.spacing.sm};

  &:hover {
    text-decoration: underline;
  }
`;

const Divider = styled.div`
  text-align: center;
  position: relative;
  margin: ${theme.spacing.lg} 0;

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: ${theme.colors.primary[200]};
  }

  span {
    position: relative;
    background: ${theme.colors.white.pure};
    padding: 0 ${theme.spacing.md};
    color: ${theme.colors.text.secondary};
    font-size: 14px;
  }
`;

const SignupLink = styled.div`
  text-align: center;
  color: ${theme.colors.text.secondary};
  font-size: 14px;

  a {
    color: ${theme.colors.primary[600]};
    font-weight: 600;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
`;

const ErrorMessage = styled.div`
  background: ${theme.colors.status.error};
  color: ${theme.colors.white.pure};
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  font-size: 14px;
  text-align: center;
`;

const SuccessMessage = styled.div`
  background: ${theme.colors.status.success};
  color: ${theme.colors.white.pure};
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  font-size: 14px;
  text-align: center;
`;

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : `http://${window.location.hostname}:8000`;
      
      const response = await axios.post(`${apiUrl}/api/auth/login/`, {
        username: formData.email,  // API expects username, we use email field
        password: formData.password
      });

      // Store token
      localStorage.setItem('token', response.data.access);
      
      // Store user data with proper structure for Navbar
      const userData = {
        name: response.data.user?.username || response.data.user?.first_name || formData.email.split('@')[0],
        email: response.data.user?.email || formData.email,
        username: response.data.user?.username || formData.email,
        ...response.data.user
      };
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Trigger user state update in App.tsx
      try {
        window.dispatchEvent(new CustomEvent('userChange', { detail: userData }));
      } catch (eventError) {
        console.error('Error dispatching user change event:', eventError);
      }
      
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LoginContainer>
      <LoginBox>
        <Logo>
          <LogoIcon>SG</LogoIcon>
          <Title>Welcome Back!</Title>
          <Subtitle>Sign in to continue to SmartGriev</Subtitle>
        </Logo>

        {error && <ErrorMessage>{error}</ErrorMessage>}

        <Form onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="email">Email / Username</Label>
            <Input
              type="text"
              id="email"
              name="email"
              placeholder="Enter your email or username"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="password">Password</Label>
            <Input
              type="password"
              id="password"
              name="password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </FormGroup>

          <Button type="submit" $loading={loading}>
            {loading ? '🔄 Signing in...' : '🔐 Sign In'}
          </Button>

          <ForgotPassword to="/forgot-password">
            Forgot your password?
          </ForgotPassword>
        </Form>

        <Divider>
          <span>OR</span>
        </Divider>

        <SignupLink>
          Don't have an account? <Link to="/register">Sign up now</Link>
        </SignupLink>
      </LoginBox>
    </LoginContainer>
  );
};

export default Login;
