import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../styles/theme';

const NavbarContainer = styled.nav`
  background: linear-gradient(135deg, ${theme.colors.primary[700]} 0%, ${theme.colors.primary[500]} 100%);
  box-shadow: ${theme.shadows.md};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 70px;
`;

const NavbarContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 ${theme.spacing.lg};
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const LogoSection = styled(Link)`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  text-decoration: none;
  transition: transform ${theme.transitions.fast};

  &:hover {
    transform: scale(1.05);
  }
`;

const Logo = styled.div`
  width: 50px;
  height: 50px;
  background: ${theme.colors.white.pure};
  border-radius: ${theme.borderRadius.lg};
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 24px;
  color: ${theme.colors.primary[600]};
  box-shadow: ${theme.shadows.md};
`;

const LogoText = styled.div`
  display: flex;
  flex-direction: column;
`;

const LogoTitle = styled.span`
  font-family: ${theme.fonts.heading};
  font-size: 24px;
  font-weight: 700;
  color: ${theme.colors.white.pure};
  letter-spacing: -0.5px;
`;

const LogoSubtitle = styled.span`
  font-size: 11px;
  color: ${theme.colors.primary[100]};
  font-weight: 500;
  letter-spacing: 1px;
  text-transform: uppercase;
`;

const NavLinks = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
  align-items: center;

  @media (max-width: 768px) {
    display: none;
  }
`;

const NavLink = styled(Link)<{ $isActive?: boolean }>`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  color: ${props => props.$isActive ? theme.colors.white.pure : theme.colors.primary[100]};
  text-decoration: none;
  font-weight: ${props => props.$isActive ? '600' : '500'};
  border-radius: ${theme.borderRadius.md};
  transition: all ${theme.transitions.fast};
  background: ${props => props.$isActive ? 'rgba(255, 255, 255, 0.15)' : 'transparent'};

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: ${theme.colors.white.pure};
  }
`;

const AuthButtons = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
  align-items: center;
`;

const Button = styled.button<{ $variant?: 'primary' | 'outline' }>`
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.md};
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  border: 2px solid ${theme.colors.white.pure};
  
  ${props => props.$variant === 'outline' ? `
    background: transparent;
    color: ${theme.colors.white.pure};
    
    &:hover {
      background: ${theme.colors.white.pure};
      color: ${theme.colors.primary[600]};
    }
  ` : `
    background: ${theme.colors.white.pure};
    color: ${theme.colors.primary[600]};
    
    &:hover {
      background: ${theme.colors.primary[50]};
      transform: translateY(-2px);
      box-shadow: ${theme.shadows.lg};
    }
  `}
`;

const UserMenu = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
`;

const UserAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: ${theme.borderRadius.full};
  background: ${theme.colors.white.pure};
  color: ${theme.colors.primary[600]};
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  cursor: pointer;
  transition: all ${theme.transitions.fast};

  &:hover {
    transform: scale(1.1);
    box-shadow: ${theme.shadows.lg};
  }
`;

const UserName = styled.span`
  color: ${theme.colors.white.pure};
  font-weight: 600;
  font-size: 14px;
`;

const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  color: ${theme.colors.white.pure};
  font-size: 24px;
  cursor: pointer;

  @media (max-width: 768px) {
    display: block;
  }
`;

interface NavbarProps {
  user?: {
    name: string;
    email: string;
  } | null;
}

const Navbar: React.FC<NavbarProps> = ({ user }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    // Clear all auth data
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Trigger user state update in App.tsx
    try {
      window.dispatchEvent(new CustomEvent('userChange', { detail: null }));
    } catch (eventError) {
      console.error('Error dispatching user change event:', eventError);
    }
    
    // Navigate to login
    navigate('/login');
  };

  return (
    <NavbarContainer>
      <NavbarContent>
        <LogoSection to="/">
          <Logo>SG</Logo>
          <LogoText>
            <LogoTitle>SmartGriev</LogoTitle>
            <LogoSubtitle>Citizen Complaint System</LogoSubtitle>
          </LogoText>
        </LogoSection>

        <NavLinks>
          <NavLink to="/" $isActive={isActive('/')}>Home</NavLink>
          {user && (
            <>
              <NavLink to="/dashboard" $isActive={isActive('/dashboard')}>Dashboard</NavLink>
              <NavLink to="/chatbot" $isActive={isActive('/chatbot')}>AI Chatbot</NavLink>
              <NavLink to="/multimodal-submit" $isActive={isActive('/multimodal-submit')}>Submit Complaint</NavLink>
              <NavLink to="/my-complaints" $isActive={isActive('/my-complaints')}>My Complaints</NavLink>
            </>
          )}
        </NavLinks>

        {user ? (
          <UserMenu>
            <UserName>{user.name}</UserName>
            <UserAvatar title={user.email}>
              {user.name.charAt(0).toUpperCase()}
            </UserAvatar>
            <Button onClick={handleLogout} $variant="outline">Logout</Button>
          </UserMenu>
        ) : (
          <AuthButtons>
            <Button onClick={() => navigate('/login')} $variant="outline">Login</Button>
            <Button onClick={() => navigate('/register')} $variant="primary">Sign Up</Button>
          </AuthButtons>
        )}

        <MobileMenuButton onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
          ☰
        </MobileMenuButton>
      </NavbarContent>
    </NavbarContainer>
  );
};

export default Navbar;
