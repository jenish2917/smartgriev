import React from 'react';
import { Layout, Row, Col, Typography, Space, Divider, Button } from 'antd';
import { 
  PhoneOutlined,
  MailOutlined,
  GlobalOutlined,
  EnvironmentOutlined,
  FacebookOutlined,
  TwitterOutlined,
  LinkedinOutlined,
  YoutubeOutlined,
  FileTextOutlined,
  QuestionCircleOutlined,
  SecurityScanOutlined,
  TeamOutlined,
  BookOutlined,
  SafetyCertificateOutlined
} from '@ant-design/icons';
import { Link } from 'react-router-dom';

const { Footer } = Layout;
const { Title, Text, Paragraph } = Typography;

const AppFooter: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <Footer style={{ 
      background: 'linear-gradient(135deg, #000080 0%, #1a237e 100%)',
      color: 'white',
      padding: 0
    }}>
      {/* Main Footer Content */}
      <div style={{ 
        maxWidth: 1200, 
        margin: '0 auto', 
        padding: '40px 20px 20px'
      }}>
        <Row gutter={[32, 32]}>
          {/* Government Info */}
          <Col xs={24} sm={12} lg={6}>
            <div style={{ marginBottom: 24 }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center',
                marginBottom: 16
              }}>
                <div style={{ 
                  fontSize: 32,
                  marginRight: 12,
                  background: 'white',
                  borderRadius: '50%',
                  width: 48,
                  height: 48,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  🇮🇳
                </div>
                <div>
                  <Title level={4} style={{ 
                    margin: 0, 
                    color: 'white',
                    fontWeight: 'bold'
                  }}>
                    SmartGriev
                  </Title>
                  <Text style={{ 
                    fontSize: 12, 
                    color: '#B3C7F7'
                  }}>
                    Digital India Initiative
                  </Text>
                </div>
              </div>
              
              <Paragraph style={{ 
                color: '#E3F2FD', 
                fontSize: 14,
                lineHeight: 1.6
              }}>
                Empowering citizens through AI-powered grievance management. 
                Part of the Government of India's Digital India mission to 
                provide transparent and efficient public services.
              </Paragraph>
              
              <div style={{ marginTop: 16 }}>
                <Space>
                  <Button 
                    type="text" 
                    icon={<FacebookOutlined />} 
                    style={{ color: 'white' }}
                    size="large"
                  />
                  <Button 
                    type="text" 
                    icon={<TwitterOutlined />} 
                    style={{ color: 'white' }}
                    size="large"
                  />
                  <Button 
                    type="text" 
                    icon={<LinkedinOutlined />} 
                    style={{ color: 'white' }}
                    size="large"
                  />
                  <Button 
                    type="text" 
                    icon={<YoutubeOutlined />} 
                    style={{ color: 'white' }}
                    size="large"
                  />
                </Space>
              </div>
            </div>
          </Col>

          {/* Quick Links */}
          <Col xs={24} sm={12} lg={6}>
            <Title level={5} style={{ color: 'white', marginBottom: 16 }}>
              Quick Links
            </Title>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              gap: 8
            }}>
              <Link to="/complaint-flow" style={{ color: '#E3F2FD', fontSize: 14 }}>
                <FileTextOutlined style={{ marginRight: 8 }} />
                Submit New Complaint
              </Link>
              <Link to="/complaint-dashboard" style={{ color: '#E3F2FD', fontSize: 14 }}>
                <TeamOutlined style={{ marginRight: 8 }} />
                Track Your Complaints
              </Link>
              <Link to="/ai-test" style={{ color: '#E3F2FD', fontSize: 14 }}>
                <SecurityScanOutlined style={{ marginRight: 8 }} />
                AI Classification Tool
              </Link>
              <Link to="/help" style={{ color: '#E3F2FD', fontSize: 14 }}>
                <QuestionCircleOutlined style={{ marginRight: 8 }} />
                Help & Support
              </Link>
              <Link to="/faq" style={{ color: '#E3F2FD', fontSize: 14 }}>
                <BookOutlined style={{ marginRight: 8 }} />
                Frequently Asked Questions
              </Link>
              <Link to="/tutorials" style={{ color: '#E3F2FD', fontSize: 14 }}>
                <SafetyCertificateOutlined style={{ marginRight: 8 }} />
                User Tutorials
              </Link>
            </div>
          </Col>

          {/* Government Services */}
          <Col xs={24} sm={12} lg={6}>
            <Title level={5} style={{ color: 'white', marginBottom: 16 }}>
              Government Services
            </Title>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              gap: 8
            }}>
              <a 
                href="https://www.india.gov.in/" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: '#E3F2FD', fontSize: 14 }}
              >
                India.gov.in Portal
              </a>
              <a 
                href="https://digitalindia.gov.in/" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: '#E3F2FD', fontSize: 14 }}
              >
                Digital India Programme
              </a>
              <a 
                href="https://www.mygov.in/" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: '#E3F2FD', fontSize: 14 }}
              >
                MyGov Platform
              </a>
              <a 
                href="https://cpgrams.gov.in/" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: '#E3F2FD', fontSize: 14 }}
              >
                CPGRAMS Portal
              </a>
              <a 
                href="https://www.rtionline.gov.in/" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: '#E3F2FD', fontSize: 14 }}
              >
                RTI Online
              </a>
              <a 
                href="https://www.pgportal.gov.in/" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: '#E3F2FD', fontSize: 14 }}
              >
                Public Grievance Portal
              </a>
            </div>
          </Col>

          {/* Contact Information */}
          <Col xs={24} sm={12} lg={6}>
            <Title level={5} style={{ color: 'white', marginBottom: 16 }}>
              Contact Us
            </Title>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              gap: 12
            }}>
              <div style={{ color: '#E3F2FD', fontSize: 14 }}>
                <PhoneOutlined style={{ marginRight: 8, color: '#FF9933' }} />
                <strong>Helpline:</strong><br />
                <span style={{ marginLeft: 20 }}>1800-XXX-XXXX (Toll Free)</span><br />
                <span style={{ marginLeft: 20 }}>+91-11-XXXX-XXXX</span>
              </div>
              
              <div style={{ color: '#E3F2FD', fontSize: 14 }}>
                <MailOutlined style={{ marginRight: 8, color: '#FF9933' }} />
                <strong>Email:</strong><br />
                <span style={{ marginLeft: 20 }}>support@smartgriev.gov.in</span><br />
                <span style={{ marginLeft: 20 }}>grievance@nic.in</span>
              </div>
              
              <div style={{ color: '#E3F2FD', fontSize: 14 }}>
                <EnvironmentOutlined style={{ marginRight: 8, color: '#FF9933' }} />
                <strong>Address:</strong><br />
                <span style={{ marginLeft: 20 }}>
                  Electronics Niketan,<br />
                  6, CGO Complex, Lodhi Road,<br />
                  New Delhi - 110003
                </span>
              </div>
              
              <div style={{ color: '#E3F2FD', fontSize: 14 }}>
                <GlobalOutlined style={{ marginRight: 8, color: '#FF9933' }} />
                <strong>Website:</strong><br />
                <span style={{ marginLeft: 20 }}>www.smartgriev.gov.in</span>
              </div>
            </div>
          </Col>
        </Row>
      </div>

      {/* Bottom Bar */}
      <div style={{ 
        background: 'rgba(0, 0, 0, 0.3)',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <div style={{ 
          maxWidth: 1200, 
          margin: '0 auto', 
          padding: '16px 20px'
        }}>
          <Row justify="space-between" align="middle">
            <Col xs={24} sm={12}>
              <Text style={{ color: '#B3C7F7', fontSize: 12 }}>
                © {currentYear} Government of India. All rights reserved. | 
                Developed under Digital India Initiative
              </Text>
            </Col>
            <Col xs={24} sm={12} style={{ textAlign: 'right' }}>
              <Space size="large" wrap>
                <Link to="/privacy-policy" style={{ color: '#B3C7F7', fontSize: 12 }}>
                  Privacy Policy
                </Link>
                <Link to="/terms-of-service" style={{ color: '#B3C7F7', fontSize: 12 }}>
                  Terms of Service
                </Link>
                <Link to="/accessibility" style={{ color: '#B3C7F7', fontSize: 12 }}>
                  Accessibility
                </Link>
                <Link to="/sitemap" style={{ color: '#B3C7F7', fontSize: 12 }}>
                  Sitemap
                </Link>
              </Space>
            </Col>
          </Row>
        </div>
      </div>

      {/* Government Compliance Info */}
      <div style={{ 
        background: '#FF9933',
        color: '#000080',
        textAlign: 'center',
        padding: '8px 20px',
        fontSize: 11,
        fontWeight: 'bold'
      }}>
        <Space size="large" wrap>
          <span>🔒 Secure Government Portal</span>
          <span>•</span>
          <span>✓ STQC Certified</span>
          <span>•</span>
          <span>🛡️ ISO 27001 Compliant</span>
          <span>•</span>
          <span>📱 Mobile Responsive</span>
          <span>•</span>
          <span>♿ GIGW Guidelines Compliant</span>
        </Space>
      </div>
    </Footer>
  );
};

export default AppFooter;