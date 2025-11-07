import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../styles/theme';
import axios from 'axios';

const DashboardContainer = styled.div`
  min-height: 100vh;
  padding-top: 70px;
  background: ${theme.colors.background.secondary};
`;

const DashboardHeader = styled.div`
  background: linear-gradient(135deg, ${theme.colors.primary[700]} 0%, ${theme.colors.primary[500]} 100%);
  padding: ${theme.spacing.xxl} ${theme.spacing.lg};
  color: ${theme.colors.white.pure};

  @media (max-width: 768px) {
    padding: ${theme.spacing.xl} ${theme.spacing.md};
  }

  @media (max-width: 480px) {
    padding: ${theme.spacing.lg} ${theme.spacing.sm};
  }
`;

const HeaderContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
`;

const WelcomeText = styled.h1`
  font-family: ${theme.fonts.heading};
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 ${theme.spacing.sm} 0;

  @media (max-width: 768px) {
    font-size: 28px;
  }

  @media (max-width: 480px) {
    font-size: 24px;
  }
`;

const SubText = styled.p`
  font-size: 16px;
  opacity: 0.9;
  margin: 0;

  @media (max-width: 768px) {
    font-size: 15px;
  }

  @media (max-width: 480px) {
    font-size: 14px;
  }
`;

const DashboardContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: ${theme.spacing.xl} ${theme.spacing.lg};

  @media (max-width: 768px) {
    padding: ${theme.spacing.lg} ${theme.spacing.md};
  }

  @media (max-width: 480px) {
    padding: ${theme.spacing.md} ${theme.spacing.sm};
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.xxl};

  @media (max-width: 968px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 768px) {
    gap: ${theme.spacing.md};
    margin-bottom: ${theme.spacing.xl};
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: ${theme.spacing.sm};
  }
`;

const StatCard = styled.div<{ $color?: string }>`
  background: ${theme.colors.white.pure};
  padding: ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.md};
  border-left: 4px solid ${props => props.$color || theme.colors.primary[500]};
  transition: all ${theme.transitions.fast};

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${theme.shadows.lg};
  }

  @media (max-width: 768px) {
    padding: ${theme.spacing.lg};
  }

  @media (max-width: 480px) {
    padding: ${theme.spacing.md};
  }
`;

const StatIcon = styled.div<{ $bgColor?: string }>`
  width: 50px;
  height: 50px;
  background: ${props => props.$bgColor || theme.colors.primary[50]};
  border-radius: ${theme.borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: ${theme.spacing.md};
`;

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: ${theme.colors.primary[800]};
  margin-bottom: ${theme.spacing.xs};
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: ${theme.colors.text.secondary};
  font-weight: 500;
`;

const QuickActionsSection = styled.div`
  margin-bottom: ${theme.spacing.xxl};
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: ${theme.colors.primary[800]};
  margin-bottom: ${theme.spacing.lg};

  @media (max-width: 768px) {
    font-size: 20px;
    margin-bottom: ${theme.spacing.md};
  }

  @media (max-width: 480px) {
    font-size: 18px;
  }
`;

const QuickActionsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: ${theme.spacing.lg};

  @media (max-width: 968px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: ${theme.spacing.md};
  }

  @media (max-width: 480px) {
    gap: ${theme.spacing.sm};
  }
`;

const ActionCard = styled.div`
  background: ${theme.colors.white.pure};
  padding: ${theme.spacing.xl};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.md};
  cursor: pointer;
  transition: all ${theme.transitions.normal};
  border: 2px solid transparent;
  min-height: 160px;

  &:hover {
    transform: translateY(-6px);
    box-shadow: ${theme.shadows.xl};
    border-color: ${theme.colors.primary[400]};
  }

  @media (max-width: 768px) {
    padding: ${theme.spacing.lg};
    min-height: 140px;
  }

  @media (max-width: 480px) {
    padding: ${theme.spacing.md};
    min-height: 120px;
  }

  &:active {
    transform: scale(0.98);
  }
`;

const ActionIcon = styled.div`
  font-size: 48px;
  margin-bottom: ${theme.spacing.md};
`;

const ActionTitle = styled.h3`
  font-size: 20px;
  font-weight: 700;
  color: ${theme.colors.primary[700]};
  margin-bottom: ${theme.spacing.sm};
`;

const ActionDescription = styled.p`
  font-size: 14px;
  color: ${theme.colors.text.secondary};
  line-height: 1.6;
`;

const RecentComplaintsSection = styled.div`
  margin-bottom: ${theme.spacing.xxl};
`;

const ComplaintsTable = styled.div`
  background: ${theme.colors.white.pure};
  border-radius: ${theme.borderRadius.lg};
  box-shadow: ${theme.shadows.md};
  overflow: hidden;

  @media (max-width: 768px) {
    overflow: visible;
  }
`;

const TableHeader = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr 1fr;
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  background: ${theme.colors.primary[50]};
  font-weight: 600;
  color: ${theme.colors.primary[800]};
  font-size: 14px;
  border-bottom: 2px solid ${theme.colors.primary[200]};

  @media (max-width: 768px) {
    display: none;
  }
`;

const TableRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr 1fr 1fr 1fr;
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-bottom: 1px solid ${theme.colors.primary[100]};
  transition: background ${theme.transitions.fast};
  cursor: pointer;

  &:hover {
    background: ${theme.colors.primary[50]};
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: ${theme.spacing.sm};
    padding: ${theme.spacing.md};
    border-radius: ${theme.borderRadius.md};
    margin-bottom: ${theme.spacing.sm};
    background: ${theme.colors.white.pure};
    box-shadow: ${theme.shadows.sm};
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: ${theme.shadows.md};
    }
  }
`;

const StatusBadge = styled.span<{ $status?: string }>`
  padding: 4px 12px;
  border-radius: ${theme.borderRadius.full};
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
  
  ${props => {
    switch (props.$status) {
      case 'pending':
        return `background: ${theme.colors.status.warning}; color: white;`;
      case 'in_progress':
        return `background: ${theme.colors.status.info}; color: white;`;
      case 'resolved':
        return `background: ${theme.colors.status.success}; color: white;`;
      default:
        return `background: ${theme.colors.primary[100]}; color: ${theme.colors.primary[800]};`;
    }
  }}
`;

interface DashboardStats {
  total: number;
  pending: number;
  in_progress: number;
  resolved: number;
}

interface Complaint {
  id: number;
  title: string;
  status: string;
  priority: string;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    total: 0,
    pending: 0,
    in_progress: 0,
    resolved: 0
  });
  const [recentComplaints, setRecentComplaints] = useState<Complaint[]>([]);
  const [userName, setUserName] = useState('User');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      // Fetch complaints
      const response = await axios.get('http://127.0.0.1:8000/api/complaints/my-complaints/', {
        headers: { Authorization: `Bearer ${token}` }
      });

      const complaints = response.data;
      setRecentComplaints(complaints.slice(0, 5));

      // Calculate stats
      setStats({
        total: complaints.length,
        pending: complaints.filter((c: Complaint) => c.status === 'pending').length,
        in_progress: complaints.filter((c: Complaint) => c.status === 'in_progress').length,
        resolved: complaints.filter((c: Complaint) => c.status === 'resolved').length,
      });

      // Get user info
      const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
      setUserName(userInfo.name || userInfo.username || 'User');
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  return (
    <DashboardContainer>
      <DashboardHeader>
        <HeaderContent>
          <WelcomeText>Welcome back, {userName}! 👋</WelcomeText>
          <SubText>Here's what's happening with your complaints today</SubText>
        </HeaderContent>
      </DashboardHeader>

      <DashboardContent>
        <StatsGrid>
          <StatCard $color={theme.colors.primary[500]}>
            <StatIcon $bgColor={theme.colors.primary[50]}>📊</StatIcon>
            <StatValue>{stats.total}</StatValue>
            <StatLabel>Total Complaints</StatLabel>
          </StatCard>

          <StatCard $color={theme.colors.status.warning}>
            <StatIcon $bgColor="#FFF3E0">⏳</StatIcon>
            <StatValue>{stats.pending}</StatValue>
            <StatLabel>Pending</StatLabel>
          </StatCard>

          <StatCard $color={theme.colors.status.info}>
            <StatIcon $bgColor="#E3F2FD">🔄</StatIcon>
            <StatValue>{stats.in_progress}</StatValue>
            <StatLabel>In Progress</StatLabel>
          </StatCard>

          <StatCard $color={theme.colors.status.success}>
            <StatIcon $bgColor="#E8F5E9">✅</StatIcon>
            <StatValue>{stats.resolved}</StatValue>
            <StatLabel>Resolved</StatLabel>
          </StatCard>
        </StatsGrid>

        <QuickActionsSection>
          <SectionTitle>Quick Actions</SectionTitle>
          <QuickActionsGrid>
            <ActionCard onClick={() => navigate('/chatbot')}>
              <ActionIcon>🤖</ActionIcon>
              <ActionTitle>AI Chatbot</ActionTitle>
              <ActionDescription>
                Get instant help from our AI assistant. Ask questions, submit complaints, or track status.
              </ActionDescription>
            </ActionCard>

            <ActionCard onClick={() => navigate('/multimodal-submit')}>
              <ActionIcon>📝</ActionIcon>
              <ActionTitle>Submit New Complaint</ActionTitle>
              <ActionDescription>
                Create a new complaint with image or audio evidence using our multimodal system.
              </ActionDescription>
            </ActionCard>

            <ActionCard onClick={() => navigate('/my-complaints')}>
              <ActionIcon>📋</ActionIcon>
              <ActionTitle>View All Complaints</ActionTitle>
              <ActionDescription>
                See all your submitted complaints, track their status, and view AI analysis results.
              </ActionDescription>
            </ActionCard>
          </QuickActionsGrid>
        </QuickActionsSection>

        <RecentComplaintsSection>
          <SectionTitle>Recent Complaints</SectionTitle>
          <ComplaintsTable>
            <TableHeader>
              <div>ID</div>
              <div>Title</div>
              <div>Status</div>
              <div>Priority</div>
              <div>Date</div>
            </TableHeader>
            {recentComplaints.length > 0 ? (
              recentComplaints.map(complaint => (
                <TableRow key={complaint.id} onClick={() => navigate(`/my-complaints`)}>
                  <div>#{complaint.id}</div>
                  <div>{complaint.title}</div>
                  <div><StatusBadge $status={complaint.status}>{complaint.status}</StatusBadge></div>
                  <div>{complaint.priority}</div>
                  <div>{new Date(complaint.created_at).toLocaleDateString()}</div>
                </TableRow>
              ))
            ) : (
              <div style={{ padding: theme.spacing.xl, textAlign: 'center', color: theme.colors.text.secondary }}>
                No complaints yet. Start by submitting your first complaint!
              </div>
            )}
          </ComplaintsTable>
        </RecentComplaintsSection>
      </DashboardContent>
    </DashboardContainer>
  );
};

export default Dashboard;
