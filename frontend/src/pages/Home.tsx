import React from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../styles/theme';

const HomeContainer = styled.div`
  min-height: 100vh;
  padding-top: 70px;
  background: linear-gradient(180deg, ${theme.colors.white.pure} 0%, ${theme.colors.primary[50]} 100%);
`;

const HeroSection = styled.section`
  padding: ${theme.spacing.xxl} ${theme.spacing.lg};
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing.xxl};
  align-items: center;

  @media (max-width: 968px) {
    grid-template-columns: 1fr;
    text-align: center;
    padding: ${theme.spacing.xl} ${theme.spacing.md};
    gap: ${theme.spacing.xl};
  }

  @media (max-width: 480px) {
    padding: ${theme.spacing.lg} ${theme.spacing.sm};
  }
`;

const HeroContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.lg};
`;

const HeroTitle = styled.h1`
  font-family: ${theme.fonts.heading};
  font-size: 56px;
  font-weight: 800;
  color: ${theme.colors.primary[800]};
  line-height: 1.2;
  margin: 0;

  @media (max-width: 968px) {
    font-size: 44px;
  }

  @media (max-width: 768px) {
    font-size: 36px;
  }

  @media (max-width: 480px) {
    font-size: 28px;
  }
`;

const HeroSubtitle = styled.p`
  font-size: 20px;
  color: ${theme.colors.text.secondary};
  line-height: 1.6;
  margin: 0;

  @media (max-width: 768px) {
    font-size: 18px;
  }

  @media (max-width: 480px) {
    font-size: 16px;
  }
`;

const HeroButtons = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  margin-top: ${theme.spacing.lg};

  @media (max-width: 968px) {
    justify-content: center;
  }

  @media (max-width: 768px) {
    flex-direction: column;
  }

  @media (max-width: 480px) {
    gap: ${theme.spacing.sm};
  }
`;

const Button = styled.button<{ $variant?: 'primary' | 'outline' }>`
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.lg};
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all ${theme.transitions.normal};
  border: 2px solid ${theme.colors.primary[500]};
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  justify-content: center;
  
  ${props => props.$variant === 'outline' ? `
    background: transparent;
    color: ${theme.colors.primary[600]};
    
    &:hover {
      background: ${theme.colors.primary[500]};
      color: ${theme.colors.white.pure};
      transform: translateY(-3px);
      box-shadow: ${theme.shadows.lg};
    }
  ` : `
    background: ${theme.colors.primary[500]};
    color: ${theme.colors.white.pure};
    
    &:hover {
      background: ${theme.colors.primary[700]};
      transform: translateY(-3px);
      box-shadow: ${theme.shadows.xl};
    }
  `}

  @media (max-width: 768px) {
    width: 100%;
    padding: ${theme.spacing.md};
    min-height: 50px;
  }

  @media (max-width: 480px) {
    font-size: 15px;
    min-height: 48px;
  }

  &:active {
    transform: scale(0.98);
  }
`;

const HeroImage = styled.div`
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const ChatbotPreview = styled.div`
  width: 100%;
  max-width: 500px;
  height: 600px;
  background: ${theme.colors.white.pure};
  border-radius: ${theme.borderRadius.xl};
  box-shadow: ${theme.shadows.xl};
  padding: ${theme.spacing.lg};
  display: flex;
  flex-direction: column;
  border: 3px solid ${theme.colors.primary[200]};

  @media (max-width: 968px) {
    max-width: 100%;
    height: 500px;
  }

  @media (max-width: 768px) {
    height: 450px;
    padding: ${theme.spacing.md};
  }

  @media (max-width: 480px) {
    height: 400px;
    padding: ${theme.spacing.sm};
    border-width: 2px;
  }
`;

const ChatbotHeader = styled.div`
  background: linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[400]} 100%);
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  color: ${theme.colors.white.pure};
  margin-bottom: ${theme.spacing.md};
`;

const ChatbotTitle = styled.h3`
  margin: 0;
  font-size: 20px;
  font-weight: 700;
`;

const ChatbotSubtitle = styled.p`
  margin: 5px 0 0 0;
  font-size: 14px;
  opacity: 0.9;
`;

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
  padding: ${theme.spacing.md};
`;

const Message = styled.div<{ $isBot?: boolean }>`
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.md};
  max-width: 80%;
  align-self: ${props => props.$isBot ? 'flex-start' : 'flex-end'};
  
  ${props => props.$isBot ? `
    background: ${theme.colors.primary[50]};
    color: ${theme.colors.text.primary};
  ` : `
    background: ${theme.colors.primary[500]};
    color: ${theme.colors.white.pure};
  `}
`;

const CTASection = styled.section`
  padding: ${theme.spacing.xxl} ${theme.spacing.lg};
  background: linear-gradient(135deg, ${theme.colors.primary[600]} 0%, ${theme.colors.primary[400]} 100%);
  text-align: center;

  @media (max-width: 768px) {
    padding: ${theme.spacing.xl} ${theme.spacing.md};
  }

  @media (max-width: 480px) {
    padding: ${theme.spacing.lg} ${theme.spacing.sm};
  }
`;

const CTATitle = styled.h2`
  font-family: ${theme.fonts.heading};
  font-size: 40px;
  font-weight: 700;
  color: ${theme.colors.white.pure};
  margin-bottom: ${theme.spacing.md};

  @media (max-width: 768px) {
    font-size: 32px;
  }

  @media (max-width: 480px) {
    font-size: 26px;
  }
`;

const CTADescription = styled.p`
  font-size: 18px;
  color: ${theme.colors.primary[50]};
  margin-bottom: ${theme.spacing.xl};
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;

  @media (max-width: 768px) {
    font-size: 16px;
    max-width: 90%;
  }

  @media (max-width: 480px) {
    font-size: 15px;
  }
`;

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <HomeContainer>
      <HeroSection>
        <HeroContent>
          <HeroTitle>
            Smart Grievance Management System
          </HeroTitle>
          <HeroSubtitle>
            Submit and track your complaints effortlessly with AI-powered assistance. 
            Get instant responses, multimodal submissions, and real-time updates.
          </HeroSubtitle>
          <HeroButtons>
            <Button onClick={() => navigate('/chatbot')} $variant="primary">
              🤖 Try AI Chatbot
            </Button>
            <Button onClick={() => navigate('/multimodal-submit')} $variant="outline">
              📝 Submit Complaint
            </Button>
          </HeroButtons>
        </HeroContent>

        <HeroImage>
          <ChatbotPreview>
            <ChatbotHeader>
              <ChatbotTitle>🤖 SmartGriev AI Assistant</ChatbotTitle>
              <ChatbotSubtitle>Powered by Advanced AI</ChatbotSubtitle>
            </ChatbotHeader>
            <ChatMessages>
              <Message $isBot>
                👋 Hello! I'm your SmartGriev AI assistant. How can I help you today?
              </Message>
              <Message>
                I need to report a road damage issue
              </Message>
              <Message $isBot>
                I can help you with that! Let me guide you through the complaint submission process. 
                First, could you provide the location of the damage?
              </Message>
              <Message>
                Main Street, near City Hall
              </Message>
              <Message $isBot>
                ✅ Great! I've identified this as a Public Works issue. Would you like to upload 
                a photo or video of the damage?
              </Message>
            </ChatMessages>
          </ChatbotPreview>
        </HeroImage>
      </HeroSection>

      <CTASection>
        <CTATitle>Ready to Get Started?</CTATitle>
        <CTADescription>
          Join thousands of citizens using SmartGriev to make their voices heard 
          and create positive change in their communities.
        </CTADescription>
        <Button onClick={() => navigate('/register')} $variant="primary" style={{ 
          background: theme.colors.white.pure, 
          color: theme.colors.primary[600],
          border: 'none'
        }}>
          Create Free Account →
        </Button>
      </CTASection>
    </HomeContainer>
  );
};

export default Home;
