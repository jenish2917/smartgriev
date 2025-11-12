import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { theme } from '../styles/theme';
import LanguageSwitcher from './common/LanguageSwitcher';

const NavbarContainer = styled.nav`
  background: linear-gradient(135deg, ${theme.colors.primary[700]} 0%, ${theme.colors.primary[500]} 100%);
  box-shadow: ${theme.shadows.md};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 70px;

  @media (max-width: 768px) {
    height: 60px;
  }
`;

const NavbarContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 ${theme.spacing.lg};
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;

  @media (max-width: 768px) {
    padding: 0 ${theme.spacing.md};
  }
`;

const LogoSection = styled(Link)`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  text-decoration: none;
  transition: transform ${theme.transitions.fast};
  z-index: 1001;

  &:hover {
    transform: scale(1.05);
  }

  @media (max-width: 768px) {
    gap: ${theme.spacing.sm};
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

  @media (max-width: 768px) {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
`;

const LogoText = styled.div`
  display: flex;
  flex-direction: column;

  @media (max-width: 480px) {
    display: none;
  }
`;

const LogoTitle = styled.span`
  font-family: ${theme.fonts.heading};
  font-size: 24px;
  font-weight: 700;
  color: ${theme.colors.white.pure};
  letter-spacing: -0.5px;

  @media (max-width: 768px) {
    font-size: 20px;
  }
`;

const LogoSubtitle = styled.span`
  font-size: 11px;
  color: ${theme.colors.primary[100]};
  font-weight: 500;
  letter-spacing: 1px;
  text-transform: uppercase;

  @media (max-width: 768px) {
    font-size: 9px;
  }
`;

const DesktopNavLinks = styled.div`
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

const DesktopAuthButtons = styled.div`
  display: flex;
  gap: ${theme.spacing.sm};
  align-items: center;

  @media (max-width: 768px) {
    display: none;
  }
`;

const Button = styled.button<{ $variant?: 'primary' | 'outline' }>`
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.md};
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  border: 2px solid ${theme.colors.white.pure};
  white-space: nowrap;
  
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

  @media (max-width: 768px) {
    padding: ${theme.spacing.sm} ${theme.spacing.md};
    font-size: 13px;
  }
`;

const UserMenu = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};

  @media (max-width: 768px) {
    gap: ${theme.spacing.sm};
  }
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

  @media (max-width: 768px) {
    width: 36px;
    height: 36px;
    font-size: 14px;
  }
`;

const UserName = styled.span`
  color: ${theme.colors.white.pure};
  font-weight: 600;
  font-size: 14px;

  @media (max-width: 768px) {
    display: none;
  }
`;

const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  color: ${theme.colors.white.pure};
  font-size: 28px;
  cursor: pointer;
  padding: ${theme.spacing.sm};
  z-index: 1001;
  transition: transform ${theme.transitions.fast};

  &:hover {
    transform: scale(1.1);
  }

  &:active {
    transform: scale(0.95);
  }

  @media (max-width: 768px) {
    display: flex;
    align-items: center;
    justify-content: center;
  }
`;

const MobileMenu = styled.div<{ $isOpen: boolean }>`
  display: none;

  @media (max-width: 768px) {
    display: block;
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    background: ${theme.colors.white.pure};
    box-shadow: ${theme.shadows.xl};
    transform: translateY(${props => props.$isOpen ? '0' : '-100%'});
    opacity: ${props => props.$isOpen ? '1' : '0'};
    visibility: ${props => props.$isOpen ? 'visible' : 'hidden'};
    transition: all ${theme.transitions.normal};
    max-height: calc(100vh - 60px);
    overflow-y: auto;
    z-index: 999;
  }
`;

const MobileMenuContent = styled.div`
  padding: ${theme.spacing.lg};
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.md};
`;

const MobileNavLink = styled(Link)<{ $isActive?: boolean }>`
  padding: ${theme.spacing.md};
  color: ${props => props.$isActive ? theme.colors.primary[600] : theme.colors.text.secondary};
  text-decoration: none;
  font-weight: ${props => props.$isActive ? '600' : '500'};
  border-radius: ${theme.borderRadius.md};
  background: ${props => props.$isActive ? theme.colors.primary[50] : 'transparent'};
  border-left: 3px solid ${props => props.$isActive ? theme.colors.primary[600] : 'transparent'};
  transition: all ${theme.transitions.fast};
  font-size: 16px;

  &:hover {
    background: ${theme.colors.primary[50]};
    color: ${theme.colors.primary[600]};
  }

  &:active {
    transform: scale(0.98);
  }
`;

const MobileUserInfo = styled.div`
  padding: ${theme.spacing.md};
  background: ${theme.colors.primary[50]};
  border-radius: ${theme.borderRadius.md};
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.sm};
`;

const MobileUserAvatar = styled.div`
  width: 50px;
  height: 50px;
  border-radius: ${theme.borderRadius.full};
  background: ${theme.colors.primary[600]};
  color: ${theme.colors.white.pure};
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 20px;
`;

const MobileUserDetails = styled.div`
  flex: 1;
`;

const MobileUserName = styled.div`
  font-weight: 600;
  color: ${theme.colors.primary[600]};
  font-size: 16px;
`;

const MobileUserEmail = styled.div`
  font-size: 14px;
  color: ${theme.colors.text.secondary};
`;

const MobileDivider = styled.div`
  height: 1px;
  background: ${theme.colors.primary[200]};
  margin: ${theme.spacing.sm} 0;
`;

const MobileButton = styled.button<{ $variant?: 'primary' | 'outline' }>`
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.md};
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all ${theme.transitions.fast};
  border: 2px solid ${theme.colors.primary[600]};
  width: 100%;
  margin-top: ${theme.spacing.sm};
  
  ${props => props.$variant === 'outline' ? `
    background: transparent;
    color: ${theme.colors.primary[600]};
    
    &:hover {
      background: ${theme.colors.primary[50]};
    }
  ` : `
    background: ${theme.colors.primary[600]};
    color: ${theme.colors.white.pure};
    
    &:hover {
      background: ${theme.colors.primary[700]};
    }
  `}

  &:active {
    transform: scale(0.98);
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
  const { t } = useTranslation('common');

  // Treat a route as active when it exactly matches OR when the current
  // location starts with the route (handles nested routes like /complaints/123)
  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [mobileMenuOpen]);

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
    
    // Close mobile menu
    setMobileMenuOpen(false);
    
    // Navigate to login
    navigate('/login');
  };

  const handleMobileNavigation = (path: string) => {
    setMobileMenuOpen(false);
    navigate(path);
  };

  return (
    <>
      <NavbarContainer>
        <NavbarContent>
          <LogoSection to="/" onClick={() => setMobileMenuOpen(false)}>
            <Logo>SG</Logo>
            <LogoText>
              <LogoTitle>SmartGriev</LogoTitle>
              <LogoSubtitle>Citizen Complaint System</LogoSubtitle>
            </LogoText>
          </LogoSection>

          {/* Desktop Navigation */}
          <DesktopNavLinks>
            <NavLink to="/" $isActive={isActive('/')}>{t('home')}</NavLink>
            {user && (
              <>
                <NavLink to="/dashboard" $isActive={isActive('/dashboard')}>{t('dashboard')}</NavLink>
                <NavLink to="/multimodal-submit" $isActive={isActive('/multimodal-submit')}>{t('submitComplaint')}</NavLink>
                <NavLink to="/my-complaints" $isActive={isActive('/my-complaints')}>{t('myComplaints', 'My Complaints')}</NavLink>
              </>
            )}
          </DesktopNavLinks>

          {/* Desktop Auth Section */}
          {user ? (
            <DesktopAuthButtons>
              <LanguageSwitcher />
              <UserMenu>
                <UserName>{user.name}</UserName>
                <UserAvatar title={user.email}>
                  {user.name.charAt(0).toUpperCase()}
                </UserAvatar>
                <Button onClick={handleLogout} $variant="outline">{t('logout')}</Button>
              </UserMenu>
            </DesktopAuthButtons>
          ) : (
            <DesktopAuthButtons>
              <LanguageSwitcher />
              <Button onClick={() => navigate('/login')} $variant="outline">{t('login', 'Login')}</Button>
              <Button onClick={() => navigate('/register')} $variant="primary">{t('signup', 'Sign Up')}</Button>
            </DesktopAuthButtons>
          )}

          {/* Mobile Menu Button */}
          <MobileMenuButton 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            {mobileMenuOpen ? '✕' : '☰'}
          </MobileMenuButton>
        </NavbarContent>
      </NavbarContainer>

      {/* Mobile Menu */}
      <MobileMenu $isOpen={mobileMenuOpen}>
        <MobileMenuContent>
          {/* User Info (if logged in) */}
          {user && (
            <>
              <MobileUserInfo>
                <MobileUserAvatar>
                  {user.name.charAt(0).toUpperCase()}
                </MobileUserAvatar>
                <MobileUserDetails>
                  <MobileUserName>{user.name}</MobileUserName>
                  <MobileUserEmail>{user.email}</MobileUserEmail>
                </MobileUserDetails>
              </MobileUserInfo>
              <MobileDivider />
            </>
          )}

          {/* Navigation Links */}
          <MobileNavLink to="/" $isActive={isActive('/')}>
            🏠 {t('home')}
          </MobileNavLink>

          {user && (
            <>
              <MobileNavLink to="/dashboard" $isActive={isActive('/dashboard')}>
                📊 {t('dashboard')}
              </MobileNavLink>
              <MobileNavLink to="/multimodal-submit" $isActive={isActive('/multimodal-submit')}>
                📝 {t('submitComplaint')}
              </MobileNavLink>
              <MobileNavLink to="/my-complaints" $isActive={isActive('/my-complaints')}>
                📋 {t('myComplaints', 'My Complaints')}
              </MobileNavLink>
            </>
          )}

          <MobileDivider />

          {/* Language Switcher */}
          <div style={{ padding: '8px 0' }}>
            <LanguageSwitcher />
          </div>

          <MobileDivider />

          {/* Auth Buttons */}
          {user ? (
            <MobileButton onClick={handleLogout} $variant="outline">
              🚪 {t('logout')}
            </MobileButton>
          ) : (
            <>
              <MobileButton onClick={() => handleMobileNavigation('/login')} $variant="outline">
                🔐 {t('login', 'Login')}
              </MobileButton>
              <MobileButton onClick={() => handleMobileNavigation('/register')} $variant="primary">
                ✨ {t('signup', 'Sign Up')}
              </MobileButton>
            </>
          )}
        </MobileMenuContent>
      </MobileMenu>
    </>
  );
};

export default Navbar;
