import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { theme } from '../styles/theme';
import axios from 'axios';

const RegisterContainer = styled.div`
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

const RegisterBox = styled.div`
  margin: auto;
  background: ${theme.colors.white.pure};
  padding: ${theme.spacing.xxl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.xl};
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;

  @media (max-width: 768px) {
    padding: ${theme.spacing.xl};
    max-width: 100%;
    max-height: 95vh;
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
  width: 70px;
  height: 70px;
  background: ${theme.colors.primary[500]};
  border-radius: ${theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
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
  gap: ${theme.spacing.md};
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing.md};

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
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
  opacity: ${props => props.$loading ? 0.7 : 1};
  margin-top: ${theme.spacing.md};
  min-height: 48px;

  &:hover {
    background: ${theme.colors.primary[700]};
    transform: ${props => props.$loading ? 'none' : 'translateY(-2px)'};
    box-shadow: ${props => props.$loading ? 'none' : theme.shadows.lg};
  }

  @media (max-width: 480px) {
    min-height: 50px;
  }

  &:active {
    transform: scale(0.98);
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

const LoginLink = styled.div`
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

const PasswordStrength = styled.div<{ $strength: number }>`
  height: 4px;
  background: ${props => {
    if (props.$strength < 2) return theme.colors.status.error;
    if (props.$strength < 4) return theme.colors.status.warning;
    return theme.colors.status.success;
  }};
  border-radius: ${theme.borderRadius.sm};
  margin-top: ${theme.spacing.xs};
  transition: all ${theme.transitions.fast};
`;

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation('auth');
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    phone: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [passwordStrength, setPasswordStrength] = useState(0);

  const calculatePasswordStrength = (password: string): number => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    return strength;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    setError('');

    if (name === 'password') {
      setPasswordStrength(calculatePasswordStrength(value));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match!');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long!');
      setLoading(false);
      return;
    }

    try {
      const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : `http://${window.location.hostname}:8000`;
      
      const response = await axios.post(`${apiUrl}/api/auth/register/`, {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirmPassword,
        first_name: formData.firstName,
        last_name: formData.lastName,
        mobile: formData.phone || '', // Backend expects 'mobile', not 'phone'
        address: '', // Optional field
        language: 'en' // Default language
      });

      setSuccess(t('register.success'));
      setTimeout(() => navigate('/login'), 2000);
    } catch (err: any) {
      console.error('Registration error:', err);
      // More detailed error handling
      if (err.response?.data) {
        const errorData = err.response.data;
        if (errorData.email) {
          setError(errorData.email[0]);
        } else if (errorData.username) {
          setError(errorData.username[0]);
        } else if (errorData.mobile) {
          setError(errorData.mobile[0]);
        } else if (errorData.password) {
          setError(errorData.password[0]);
        } else if (errorData.detail) {
          setError(errorData.detail);
        } else {
          setError(t('register.error'));
        }
      } else {
        setError(t('register.error'));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <RegisterContainer>
      <RegisterBox>
        <Logo>
          <LogoIcon>SG</LogoIcon>
          <Title>{t('register.title')}</Title>
          <Subtitle>{t('register.subtitle')}</Subtitle>
        </Logo>

        {error && <ErrorMessage>{error}</ErrorMessage>}
        {success && <SuccessMessage>{success}</SuccessMessage>}

        <Form onSubmit={handleSubmit}>
          <FormRow>
            <FormGroup>
              <Label htmlFor="firstName">{t('register.firstName')}</Label>
              <Input
                type="text"
                id="firstName"
                name="firstName"
                placeholder={t('register.firstNamePlaceholder')}
                value={formData.firstName}
                onChange={handleChange}
                required
              />
            </FormGroup>

            <FormGroup>
              <Label htmlFor="lastName">{t('register.lastName')}</Label>
              <Input
                type="text"
                id="lastName"
                name="lastName"
                placeholder={t('register.lastNamePlaceholder')}
                value={formData.lastName}
                onChange={handleChange}
                required
              />
            </FormGroup>
          </FormRow>

          <FormGroup>
            <Label htmlFor="email">{t('register.email')}</Label>
            <Input
              type="email"
              id="email"
              name="email"
              placeholder={t('register.emailPlaceholder')}
              value={formData.email}
              onChange={handleChange}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="username">{t('register.username')}</Label>
            <Input
              type="text"
              id="username"
              name="username"
              placeholder={t('register.usernamePlaceholder')}
              value={formData.username}
              onChange={handleChange}
              required
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="phone">{t('register.phone')}</Label>
            <Input
              type="tel"
              id="phone"
              name="phone"
              placeholder={t('register.phonePlaceholder')}
              value={formData.phone}
              onChange={handleChange}
            />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="password">{t('register.password')}</Label>
            <Input
              type="password"
              id="password"
              name="password"
              placeholder={t('register.passwordPlaceholder')}
              value={formData.password}
              onChange={handleChange}
              required
            />
            <PasswordStrength $strength={passwordStrength} />
          </FormGroup>

          <FormGroup>
            <Label htmlFor="confirmPassword">{t('register.confirmPassword')}</Label>
            <Input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              placeholder={t('register.confirmPasswordPlaceholder')}
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </FormGroup>

          <Button type="submit" $loading={loading}>
            {loading ? `🔄 ${t('register.creating')}` : `✨ ${t('register.createAccount')}`}
          </Button>
        </Form>

        <Divider>
          <span>{t('common.or')}</span>
        </Divider>

        <LoginLink>
          {t('register.haveAccount')} <Link to="/login">{t('login.signIn')}</Link>
        </LoginLink>
      </RegisterBox>
    </RegisterContainer>
  );
};

export default Register;
