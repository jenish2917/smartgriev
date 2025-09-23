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

  const classifyComplaint = async () => {
    if (!description.trim()) {
      setError('Please enter a complaint description');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const token = localStorage.getItem('token');
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch('/api/complaints/classify/', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          title: title.trim(),
          text: description.trim(),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Classification failed');
      }
    } catch (err) {
      setError('Network error occurred');
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
            onClick={classifyComplaint}
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
          <div style={{ textAlign: 'center', marginTop: 20 }}>
            <Spin size="large" />
            <div style={{ marginTop: 10 }}>
              <Text>Analyzing complaint with AI...</Text>
            </div>
          </div>
        )}

        {result && (
          <Card 
            style={{ 
              marginTop: 24,
              borderRadius: 12,
              border: '2px solid #138808',
              boxShadow: '0 4px 16px rgba(19,136,8,0.2)'
            }} 
            title={
              <span style={{ color: '#138808', fontSize: 18, fontWeight: 'bold' }}>
                🎯 Classification Results
              </span>
            }
          >
            <div style={{ marginBottom: 20 }}>
              <Text strong style={{ fontSize: 16 }}>Classified Department: </Text>
              <Tag 
                className="info-state"
                style={{ 
                  fontSize: 14,
                  fontWeight: 'bold',
                  padding: '6px 12px'
                }}
              >
                {result.classification.department_name}
              </Tag>
            </div>

            <div style={{ marginBottom: 20 }}>
              <Text strong style={{ fontSize: 16 }}>Confidence Level: </Text>
              <Tag 
                className={result.classification.confidence >= 0.8 ? 'success-state' : result.classification.confidence >= 0.6 ? 'warning-state' : 'error-state'}
                style={{ 
                  fontSize: 14,
                  fontWeight: 'bold',
                  padding: '6px 12px'
                }}
              >
                {(result.classification.confidence * 100).toFixed(1)}%
              </Tag>
            </div>

            <div style={{ marginBottom: 20 }}>
              <Text strong style={{ fontSize: 16 }}>AI Reasoning: </Text>
              <div style={{ 
                background: 'linear-gradient(135deg, #F5F5F5 0%, #E8F5E8 100%)', 
                padding: 16, 
                borderRadius: 8, 
                marginTop: 8,
                border: '1px solid #D9D9D9'
              }}>
                <Text style={{ fontSize: 15, color: '#333' }}>{result.classification.reasoning}</Text>
              </div>
            </div>

            {result.suggested_department && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>Suggested Department: </Text>
                <Card size="small" style={{ marginTop: 8 }}>
                  <Text strong>{result.suggested_department.name}</Text>
                  <br />
                  <Text type="secondary">{result.suggested_department.description}</Text>
                </Card>
              </div>
            )}

            <Divider />

            <div>
              <Text strong style={{ fontSize: 16 }}>All Available Departments:</Text>
              <div style={{ marginTop: 12 }}>
                {result.all_departments.map((dept) => (
                  <Tag 
                    key={dept.id} 
                    className={dept.id === result.suggested_department?.id ? 'success-state' : 'neutral-state'}
                    style={{ 
                      marginBottom: 8, 
                      marginRight: 8,
                      padding: '6px 12px',
                      fontSize: 13,
                      fontWeight: dept.id === result.suggested_department?.id ? 'bold' : 'normal'
                    }}
                  >
                    {dept.name}
                  </Tag>
                ))}
              </div>
            </div>
          </Card>
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