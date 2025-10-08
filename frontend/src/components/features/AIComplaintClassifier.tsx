import React, { useState } from 'react';
import { Button, Card, Input, Typography, Alert, Spin, Tag, Divider, Menu } from 'antd';
import { RobotOutlined, SendOutlined, HomeOutlined, LoginOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface ClassificationResult {
  classification: {
    department: string;
    department_name: string;
    confidence: number;
    reasoning: string;
    department_icon?: string;
    department_color?: string;
    department_description?: string;
    urgency_level?: 'low' | 'medium' | 'high' | 'critical';
    estimated_resolution_days?: number;
    method?: 'ai_enhanced' | 'keyword' | 'fallback_enhanced';
    from_cache?: boolean;
    secondary_departments?: string[];
    required_documents?: string[];
    escalation_needed?: boolean;
  };
  suggested_department?: {
    id: number;
    name: string;
    description: string;
  };
  all_departments: Array<{
    id: number;
    name: string;
    description: string;
  }>;
}

const AIComplaintClassifier: React.FC = () => {
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [error, setError] = useState<string>('');

  const topMenuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Home',
    },
    {
      key: '/ai-test',
      icon: <RobotOutlined />,
      label: 'AI Test',
    },
    {
      key: '/login',
      icon: <LoginOutlined />,
      label: 'Login',
    },
  ];

  const classifyComplaint = async (retryCount = 0) => {
    if (!description.trim()) {
      setError('Please enter a complaint description');
      return;
    }

    // Validate input length
    if (description.length < 10) {
      setError('Please provide a more detailed complaint description (at least 10 characters)');
      return;
    }

    if (description.length > 5000) {
      setError('Complaint description is too long (maximum 5000 characters)');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const token = localStorage.getItem('token');
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Use the correct API endpoint with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const response = await fetch('http://127.0.0.1:8000/api/complaints/classify/', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          title: title.trim(),
          text: description.trim(),
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        
        // Validate response structure
        if (data && data.classification) {
          setResult(data);
        } else {
          setError('Invalid response format from AI classification service');
        }
      } else if (response.status === 429) {
        // Rate limiting - retry after delay
        if (retryCount < 2) {
          setTimeout(() => {
            classifyComplaint(retryCount + 1);
          }, 2000 * (retryCount + 1));
          return;
        } else {
          setError('Service is currently busy. Please try again in a few minutes.');
        }
      } else if (response.status === 401) {
        setError('Authentication required. Please log in to use AI classification.');
      } else if (response.status >= 500) {
        // Server error - retry once
        if (retryCount < 1) {
          setTimeout(() => {
            classifyComplaint(retryCount + 1);
          }, 3000);
          return;
        } else {
          setError('AI classification service is temporarily unavailable. Please try again later.');
        }
      } else {
        try {
          const errorData = await response.json();
          setError(errorData.error || errorData.detail || `Classification failed (${response.status})`);
        } catch {
          setError(`Classification service error (${response.status})`);
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        setError('Request timed out. Please check your connection and try again.');
      } else if (err.message?.includes('Failed to fetch')) {
        setError('Unable to connect to AI service. Please check if the backend is running.');
      } else {
        setError(`Network error: ${err.message || 'Unknown error occurred'}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'green';
    if (confidence >= 0.6) return 'orange';
    return 'red';
  };

  return (
    <div style={{ background: '#F5F5F5', minHeight: '100vh' }}>
      {/* Government Header */}
      <div className="gov-header">
        <div className="gov-logo">
          🇮🇳
        </div>
        <Typography.Title level={2} style={{ color: 'white', margin: '0 0 8px 0' }}>
          AI Classification Test
        </Typography.Title>
        <Typography.Text style={{ color: 'white', fontSize: 16 }}>
          Digital India Initiative - AI-Powered Complaint Classification System
        </Typography.Text>
      </div>

      {/* Top Navigation */}
      <div style={{ 
        background: 'white', 
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)', 
        padding: '0 20px',
        marginBottom: 20
      }}>
        <Menu
          mode="horizontal"
          selectedKeys={[location.pathname]}
          style={{ 
            border: 'none', 
            fontSize: 16,
            background: 'linear-gradient(90deg, #FF9933 0%, #138808 100%)',
            borderRadius: '0 0 8px 8px'
          }}
        >
          {topMenuItems.map(item => (
            <Menu.Item key={item.key} icon={item.icon} style={{ color: 'white', fontWeight: '600' }}>
              <Link to={item.key} style={{ color: 'white' }}>{item.label}</Link>
            </Menu.Item>
          ))}
        </Menu>
      </div>

      <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 20px' }}>
      <Card 
        style={{ 
          borderRadius: 12,
          boxShadow: '0 8px 24px rgba(0,0,0,0.1)',
          border: '2px solid #FF9933'
        }}
        bodyStyle={{ padding: 32 }}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ color: '#FF9933', marginBottom: 8 }}>
            <RobotOutlined /> AI Complaint Classification
          </Title>
          <Text type="secondary" style={{ fontSize: 16 }}>
            Test the AI classification system powered by <Text strong style={{ color: '#138808' }}>Groq API</Text> with <Text strong style={{ color: '#000080' }}>Llama3-8B-8192</Text> model
          </Text>
        </div>

        <Divider />

        <div style={{ marginBottom: 20 }}>
          <Text strong style={{ fontSize: 16, color: '#333' }}>Complaint Title (Optional):</Text>
          <Input
            placeholder="Enter complaint title..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{ marginTop: 8, height: 40, borderRadius: 6 }}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <Text strong style={{ fontSize: 16, color: '#333' }}>Complaint Description:</Text>
          <TextArea
            placeholder="Describe the complaint in detail..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={5}
            style={{ 
              marginTop: 8,
              borderRadius: 6,
              fontSize: 16
            }}
          />
        </div>

        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Button
            className="primary-button"
            type="primary"
            icon={<SendOutlined />}
            onClick={() => classifyComplaint()}
            loading={loading}
            disabled={!description.trim()}
            size="large"
            style={{
              height: 50,
              fontSize: 16,
              fontWeight: 'bold',
              borderRadius: 8,
              paddingLeft: 24,
              paddingRight: 24
            }}
          >
            🤖 Classify Complaint with AI
          </Button>
        </div>

        {error && (
          <Alert
            message="Error"
            description={error}
            type="error"
            showIcon
            style={{ marginTop: 16 }}
          />
        )}

        {loading && (
          <Card style={{ 
            background: 'linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%)',
            border: '2px solid #0EA5E9',
            borderRadius: 16,
            marginTop: 20
          }}>
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <div style={{ 
                width: 80, 
                height: 80, 
                background: 'linear-gradient(135deg, #FF671F, #FFD700)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
                animation: 'pulse 2s infinite'
              }}>
                <RobotOutlined style={{ fontSize: 32, color: 'white' }} />
              </div>
              <Spin size="large" />
              <div style={{ marginTop: 20 }}>
                <Title level={4} style={{ color: '#1E3A8A', margin: 0, marginBottom: 8 }}>
                  🤖 AI Analysis in Progress
                </Title>
                <Text style={{ fontSize: 16, color: '#64748B' }}>
                  Our advanced AI system is analyzing your complaint using Groq Llama3 model...
                </Text>
                <div style={{ marginTop: 12 }}>
                  <Text style={{ fontSize: 14, color: '#94A3B8' }}>
                    This may take 5-15 seconds for optimal accuracy
                  </Text>
                </div>
              </div>
            </div>
          </Card>
        )}

        {result && (
          <div style={{ marginTop: 24 }}>
            {/* Main Classification Result */}
            <Card
              style={{
                background: 'linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%)',
                border: '2px solid #0EA5E9',
                borderRadius: 16,
                marginBottom: 20
              }}
              bodyStyle={{ padding: 24 }}
            >
              <div style={{ textAlign: 'center', marginBottom: 20 }}>
                <div style={{ fontSize: 48, marginBottom: 12 }}>
                  {result.classification.department_icon || '🏛️'}
                </div>
                <Title level={3} style={{ 
                  color: result.classification.department_color || '#0369A1',
                  margin: 0,
                  marginBottom: 8
                }}>
                  {result.classification.department_name}
                </Title>
                <Text style={{ 
                  fontSize: 16, 
                  color: '#64748B',
                  display: 'block',
                  marginBottom: 16
                }}>
                  {result.classification.department_description || 'Government department for handling citizen complaints'}
                </Text>
                
                <div style={{ display: 'flex', justifyContent: 'center', gap: 12, flexWrap: 'wrap' }}>
                  <Tag 
                    color="blue" 
                    style={{ 
                      fontSize: 14, 
                      padding: '8px 16px',
                      borderRadius: 20,
                      border: 'none',
                      background: 'linear-gradient(135deg, #3B82F6, #1D4ED8)'
                    }}
                  >
                    🎯 Confidence: {Math.round(result.classification.confidence * 100)}%
                  </Tag>
                  
                  {result.classification.urgency_level && (
                    <Tag 
                      color={
                        result.classification.urgency_level === 'critical' ? 'red' :
                        result.classification.urgency_level === 'high' ? 'orange' :
                        result.classification.urgency_level === 'medium' ? 'blue' : 'green'
                      }
                      style={{ 
                        fontSize: 14, 
                        padding: '8px 16px',
                        borderRadius: 20,
                        textTransform: 'capitalize'
                      }}
                    >
                      ⚡ {result.classification.urgency_level} Priority
                    </Tag>
                  )}
                  
                  {result.classification.estimated_resolution_days && (
                    <Tag 
                      color="purple" 
                      style={{ 
                        fontSize: 14, 
                        padding: '8px 16px',
                        borderRadius: 20
                      }}
                    >
                      📅 {result.classification.estimated_resolution_days} days
                    </Tag>
                  )}
                </div>
              </div>
            </Card>

            {/* AI Reasoning Section */}
            <Card
              title={
                <span style={{ fontSize: 18, color: '#1E40AF' }}>
                  🧠 AI Analysis & Reasoning
                </span>
              }
              style={{
                marginBottom: 20,
                borderRadius: 12,
                border: '1px solid #E5E7EB'
              }}
              bodyStyle={{ padding: 20 }}
            >
              <div style={{ 
                background: 'linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)', 
                padding: 20, 
                borderRadius: 12, 
                border: '1px solid #E2E8F0',
                marginBottom: 16
              }}>
                <Text style={{ 
                  fontSize: 16, 
                  lineHeight: 1.6,
                  color: '#374151',
                  fontStyle: 'italic'
                }}>
                  "{result.classification.reasoning}"
                </Text>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
                <Text style={{ color: '#6B7280', fontSize: 14 }}>
                  Classification Method: <strong style={{ color: '#1F2937' }}>
                    {result.classification.method === 'ai_enhanced' ? '🤖 AI Enhanced' :
                     result.classification.method === 'keyword' ? '🔍 Keyword Matching' :
                     result.classification.method === 'fallback_enhanced' ? '🛡️ Intelligent Fallback' : 
                     '🤖 AI Powered'}
                  </strong>
                </Text>
                
                {result.classification.from_cache && (
                  <Tag color="cyan" style={{ fontSize: 12 }}>
                    ⚡ From Cache
                  </Tag>
                )}
              </div>
            </Card>

            {/* Additional Information */}
            {((result.classification.secondary_departments && result.classification.secondary_departments.length > 0) || 
              (result.classification.required_documents && result.classification.required_documents.length > 0)) && (
              <Card
                title={
                  <span style={{ fontSize: 18, color: '#059669' }}>
                    📋 Additional Information
                  </span>
                }
                style={{
                  marginBottom: 20,
                  borderRadius: 12,
                  border: '1px solid #D1FAE5'
                }}
                bodyStyle={{ padding: 20 }}
              >
                {result.classification.secondary_departments && result.classification.secondary_departments.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <Text strong style={{ display: 'block', marginBottom: 8, color: '#374151' }}>
                      🔗 Related Departments:
                    </Text>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {result.classification.secondary_departments.map((dept: string, index: number) => (
                        <Tag key={index} color="geekblue" style={{ fontSize: 12, padding: '4px 8px' }}>
                          {dept}
                        </Tag>
                      ))}
                    </div>
                  </div>
                )}
                
                {result.classification.required_documents && result.classification.required_documents.length > 0 && (
                  <div style={{ marginBottom: 16 }}>
                    <Text strong style={{ display: 'block', marginBottom: 8, color: '#374151' }}>
                      📄 Required Documents:
                    </Text>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {result.classification.required_documents.map((doc: string, index: number) => (
                        <Tag key={index} color="orange" style={{ fontSize: 12, padding: '4px 8px' }}>
                          📄 {doc}
                        </Tag>
                      ))}
                    </div>
                  </div>
                )}
                
                {result.classification.escalation_needed && (
                  <Alert
                    message="⚠️ Escalation Recommended"
                    description="This complaint may require immediate attention or escalation to higher authorities."
                    type="warning"
                    showIcon
                    style={{ marginTop: 12 }}
                  />
                )}
              </Card>
            )}

            {/* All Departments Overview */}
            {result.all_departments && result.all_departments.length > 0 && (
              <Card
                title={
                  <span style={{ fontSize: 18, color: '#7C3AED' }}>
                    🏛️ All Available Departments
                  </span>
                }
                style={{
                  borderRadius: 12,
                  border: '1px solid #E9D5FF'
                }}
                bodyStyle={{ padding: 20 }}
              >
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 12 }}>
                  {result.all_departments.map((dept: any) => (
                    <div
                      key={dept.id}
                      style={{
                        padding: 12,
                        borderRadius: 8,
                        background: dept.name === result.classification.department_name ? 
                          'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)' : '#F9FAFB',
                        border: dept.name === result.classification.department_name ? 
                          '2px solid #3B82F6' : '1px solid #E5E7EB',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      <Text style={{ 
                        fontSize: 14, 
                        fontWeight: dept.name === result.classification.department_name ? 'bold' : 'normal',
                        color: dept.name === result.classification.department_name ? '#1E40AF' : '#374151'
                      }}>
                        {dept.name === result.classification.department_name && '🎯 '}
                        {dept.name}
                      </Text>
                      {dept.description && (
                        <Text style={{ 
                          display: 'block', 
                          fontSize: 12, 
                          color: '#6B7280',
                          marginTop: 4
                        }}>
                          {dept.description}
                        </Text>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        )}

        <Divider />

        <Card 
          size="small" 
          style={{ 
            background: 'linear-gradient(135deg, #FFF8E1 0%, #F3E5F5 100%)',
            border: '1px solid #FFE082',
            borderRadius: 8
          }}
        >
          <Title level={4} style={{ color: '#FF9933', marginBottom: 16 }}>
            🚀 How AI Classification Works:
          </Title>
          <ul style={{ fontSize: 15, lineHeight: '1.8' }}>
            <li>Powered by <strong style={{ color: '#138808' }}>Groq API</strong> with <strong style={{ color: '#000080' }}>Llama3-8B-8192</strong> model</li>
            <li>Analyzes complaint text and suggests the most appropriate government department</li>
            <li>Automatically assigns complaints to departments during creation process</li>
            <li>Supports 5 key departments: <strong>Infrastructure, Healthcare, Education, Transportation, Utilities</strong></li>
            <li>Provides confidence scores and detailed reasoning for transparency</li>
          </ul>
        </Card>
      </Card>
      </div>
    </div>
  );
};

export default AIComplaintClassifier;