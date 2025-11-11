import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../styles/theme';
import axios from 'axios';
import { API_URLS } from '../config/api.config';

const ResetContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${theme.spacing.md};
  background: linear-gradient(135deg, ${theme.colors.primary[700]} 0%, ${theme.colors.primary[400]} 100%);
`;

const ResetBox = styled.div`
  background: ${theme.colors.white.pure};
  padding: ${theme.spacing.xxl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.xl};
  max-width: 450px;
  width: 100%;
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
`;

const Title = styled.h1`
  font-family: ${theme.fonts.heading};
  font-size: 28px;
  font-weight: 700;
  color: ${theme.colors.primary[800]};
  text-align: center;
  margin: 0 0 ${theme.spacing.sm} 0;
`;

const Subtitle = styled.p`
  text-align: center;
  color: ${theme.colors.text.secondary};
  font-size: 14px;
  margin: 0 0 ${theme.spacing.xl} 0;
  line-height: 1.5;
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
  border: 2px solid ${theme.colors.text.disabled};
  border-radius: ${theme.borderRadius.md};
  font-size: 16px;
  transition: all ${theme.transitions.fast};

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary[500]};
    box-shadow: 0 0 0 3px ${theme.colors.primary[100]};
  }
`;

const Button = styled.button`
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  background: ${theme.colors.primary[500]};
  color: ${theme.colors.white.pure};
  border: none;
  border-radius: ${theme.borderRadius.md};
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover:not(:disabled) {
    background: ${theme.colors.primary[600]};
    transform: translateY(-2px);
    box-shadow: ${theme.shadows.md};
  }

  &:disabled {
    background: ${theme.colors.background.tertiary};
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  background: ${theme.colors.status.error};
  color: ${theme.colors.white.pure};
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  font-size: 14px;
`;

const SuccessMessage = styled.div`
  background: ${theme.colors.status.success};
  color: ${theme.colors.white.pure};
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  font-size: 14px;
  text-align: center;
`;

const BackLink = styled(Link)`
  text-align: center;
  color: ${theme.colors.primary[600]};
  font-size: 14px;
  text-decoration: none;
  display: block;
  margin-top: ${theme.spacing.md};

  &:hover {
    text-decoration: underline;
  }
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

const PasswordResetConfirm: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);

  const token = searchParams.get('token') || '';
  const uidb64 = searchParams.get('uid') || '';

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

    if (name === 'newPassword') {
      setPasswordStrength(calculatePasswordStrength(value));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.newPassword !== formData.confirmPassword) {
      setError('Passwords do not match!');
      setLoading(false);
      return;
    }

    if (formData.newPassword.length < 8) {
      setError('Password must be at least 8 characters long!');
      setLoading(false);
      return;
    }

    try {
      await axios.post(API_URLS.PASSWORD_RESET_CONFIRM, {
        token,
        uidb64,
        new_password: formData.newPassword
      });

      setSuccess(true);
      setTimeout(() => navigate('/login'), 3000);
    } catch (err: any) {
      console.error('Password reset confirm error:', err);
      setError(err.response?.data?.error || err.response?.data?.detail || 'Failed to reset password. The link may have expired.');
    } finally {
      setLoading(false);
    }
  };

  if (!token || !uidb64) {
    return (
      <ResetContainer>
        <ResetBox>
          <Logo>
            <LogoIcon>⚠️</LogoIcon>
            <Title>Invalid Reset Link</Title>
            <Subtitle>
              This password reset link is invalid or has expired.
            </Subtitle>
          </Logo>
          <ErrorMessage>
            Please request a new password reset link.
          </ErrorMessage>
          <BackLink to="/forgot-password">Request New Link</BackLink>
        </ResetBox>
      </ResetContainer>
    );
  }

  return (
    <ResetContainer>
      <ResetBox>
        <Logo>
          <LogoIcon>🔐</LogoIcon>
          <Title>Create New Password</Title>
          <Subtitle>
            Enter your new password below
          </Subtitle>
        </Logo>

        {error && <ErrorMessage>{error}</ErrorMessage>}
        
        {success ? (
          <>
            <SuccessMessage>
              ✅ Password reset successful!<br/>
              Redirecting to login...
            </SuccessMessage>
          </>
        ) : (
          <Form onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="newPassword">New Password</Label>
              <Input
                type="password"
                id="newPassword"
                name="newPassword"
                placeholder="Enter new password"
                value={formData.newPassword}
                onChange={handleChange}
                required
                minLength={8}
              />
              <PasswordStrength $strength={passwordStrength} />
              <small style={{ color: theme.colors.text.secondary, fontSize: '12px' }}>
                Password must be at least 8 characters with uppercase, lowercase, and numbers
              </small>
            </FormGroup>

            <FormGroup>
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                placeholder="Confirm new password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </FormGroup>

            <Button type="submit" disabled={loading}>
              {loading ? 'Resetting...' : 'Reset Password'}
            </Button>
          </Form>
        )}

        <BackLink to="/login">← Back to Login</BackLink>
      </ResetBox>
    </ResetContainer>
  );
};

export default PasswordResetConfirm;
