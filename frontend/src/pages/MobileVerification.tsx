import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { theme } from '../styles/theme';
import axios from 'axios';
import { API_URLS } from '../config/api.config';

const VerificationContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: ${theme.spacing.md};
  background: linear-gradient(135deg, ${theme.colors.primary[700]} 0%, ${theme.colors.primary[400]} 100%);
`;

const VerificationBox = styled.div`
  background: ${theme.colors.white.pure};
  padding: ${theme.spacing.xxl};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.xl};
  max-width: 500px;
  width: 100%;
  text-align: center;
`;

const Logo = styled.div`
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
  margin: 0 0 ${theme.spacing.sm} 0;
`;

const Message = styled.p`
  color: ${theme.colors.text.secondary};
  font-size: 16px;
  margin: 0 0 ${theme.spacing.xl} 0;
  line-height: 1.5;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.lg};
`;

const Input = styled.input`
  padding: ${theme.spacing.md};
  border: 2px solid ${theme.colors.text.disabled};
  border-radius: ${theme.borderRadius.md};
  font-size: 16px;
  text-align: center;
  letter-spacing: 0.5em;
  font-weight: 600;
  transition: all ${theme.transitions.fast};

  &:focus {
    outline: none;
    border-color: ${theme.colors.primary[500]};
    box-shadow: 0 0 0 3px ${theme.colors.primary[100]};
  }

  &::placeholder {
    letter-spacing: normal;
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

const ResendButton = styled.button`
  background: transparent;
  border: none;
  color: ${theme.colors.primary[600]};
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
  padding: ${theme.spacing.sm};

  &:hover:not(:disabled) {
    color: ${theme.colors.primary[700]};
  }

  &:disabled {
    color: ${theme.colors.text.disabled};
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
`;

const PhoneDisplay = styled.div`
  background: ${theme.colors.background.secondary};
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  font-size: 18px;
  font-weight: 600;
  color: ${theme.colors.text.primary};
  letter-spacing: 0.1em;
  margin-bottom: ${theme.spacing.md};
`;

const MobileVerification: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation('auth');
  const [searchParams] = useSearchParams();
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [resendCooldown, setResendCooldown] = useState(0);

  const mobile = searchParams.get('mobile') || '';

  useEffect(() => {
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCooldown]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await axios.post(API_URLS.VERIFY_MOBILE || '/api/auth/verify-mobile/', {
        mobile,
        otp
      });
      
      setSuccess('Mobile number verified successfully! Redirecting...');
      setTimeout(() => navigate('/dashboard'), 2000);
    } catch (err: any) {
      console.error('Mobile verification error:', err);
      setError(err.response?.data?.error || err.response?.data?.detail || 'Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    
    setLoading(true);
    setError('');
    
    try {
      await axios.post(API_URLS.RESEND_MOBILE_OTP || '/api/auth/resend-mobile-otp/', {
        mobile
      });
      
      setSuccess('OTP sent to your mobile number!');
      setResendCooldown(60); // 60 second cooldown
    } catch (err: any) {
      console.error('Resend error:', err);
      setError(err.response?.data?.error || 'Failed to resend OTP.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <VerificationContainer>
      <VerificationBox>
        <Logo>
          <LogoIcon>📱</LogoIcon>
          <Title>Verify Mobile Number</Title>
          <Message>
            We've sent a 6-digit OTP to your mobile number
          </Message>
          {mobile && <PhoneDisplay>{mobile}</PhoneDisplay>}
        </Logo>

        {error && <ErrorMessage>{error}</ErrorMessage>}
        {success && <SuccessMessage>{success}</SuccessMessage>}

        <Form onSubmit={handleSubmit}>
          <Input
            type="text"
            placeholder="Enter 6-digit OTP"
            value={otp}
            onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
            maxLength={6}
            required
            disabled={loading || !!success}
            autoFocus
          />

          <Button type="submit" disabled={loading || otp.length !== 6 || !!success}>
            {loading ? 'Verifying...' : 'Verify Mobile'}
          </Button>

          <div>
            <Message style={{ fontSize: '14px', marginBottom: theme.spacing.sm }}>
              Didn't receive the OTP?
            </Message>
            <ResendButton 
              type="button" 
              onClick={handleResend} 
              disabled={loading || resendCooldown > 0}
            >
              {resendCooldown > 0 
                ? `Resend in ${resendCooldown}s` 
                : 'Resend OTP'}
            </ResendButton>
          </div>
        </Form>
      </VerificationBox>
    </VerificationContainer>
  );
};

export default MobileVerification;
