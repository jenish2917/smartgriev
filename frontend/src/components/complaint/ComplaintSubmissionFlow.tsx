import React, { useState } from 'react';
import { Card, Button, Typography, Result, Spin, message } from 'antd';
import { CheckCircleOutlined, RobotOutlined, FormOutlined } from '@ant-design/icons';
import ComplaintCategorySelector from './ComplaintCategorySelector';
import ComplaintDetailsForm from './ComplaintDetailsForm';
import { ComplaintCategory, ComplaintSubcategory, ComplaintComponent } from '@/types/ComplaintCategories';

const { Title, Paragraph } = Typography;

interface ComplaintSubmissionState {
  step: 'method' | 'category' | 'form' | 'ai' | 'success';
  category?: ComplaintCategory;
  subcategory?: ComplaintSubcategory;
  component?: ComplaintComponent;
  complaintId?: string;
}

const ComplaintSubmissionFlow: React.FC = () => {
  const [state, setState] = useState<ComplaintSubmissionState>({ step: 'method' });
  const [loading, setLoading] = useState(false);

  const handleMethodSelect = (method: 'structured' | 'ai') => {
    if (method === 'structured') {
      setState({ ...state, step: 'category' });
    } else {
      setState({ ...state, step: 'ai' });
    }
  };

  const handleCategorySelect = (
    category: ComplaintCategory, 
    subcategory: ComplaintSubcategory, 
    component: ComplaintComponent
  ) => {
    setState({
      ...state,
      step: 'form',
      category,
      subcategory,
      component
    });
  };

  const handleFormSubmit = async (formData: any) => {
    setLoading(true);
    try {
      // Simulate API call
      const response = await fetch('/api/complaints/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        const result = await response.json();
        setState({
          ...state,
          step: 'success',
          complaintId: result.id || 'CMP-' + Date.now()
        });
        message.success('Complaint submitted successfully!');
      } else {
        throw new Error('Failed to submit complaint');
      }
    } catch (error) {
      console.error('Submission error:', error);
      message.error('Failed to submit complaint. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (state.step === 'form') {
      setState({ ...state, step: 'category' });
    } else if (state.step === 'category' || state.step === 'ai') {
      setState({ step: 'method' });
    }
  };

  const handleStartOver = () => {
    setState({ step: 'method' });
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        background: '#F5F5F5'
      }}>
        <Card style={{ textAlign: 'center', minWidth: 300 }}>
          <Spin size="large" />
          <Title level={4} style={{ marginTop: 20 }}>
            Submitting Your Complaint...
          </Title>
          <Paragraph>Please wait while we process your submission.</Paragraph>
        </Card>
      </div>
    );
  }

  // Method Selection Step
  if (state.step === 'method') {
    return (
      <div style={{ padding: '20px', background: '#F5F5F5', minHeight: '100vh' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <Card style={{ textAlign: 'center', marginBottom: 30, border: '2px solid #FF9933' }}>
            <Title level={2} style={{ color: '#FF9933', marginBottom: 16 }}>
              How would you like to submit your complaint?
            </Title>
            <Paragraph style={{ fontSize: 16, color: '#666' }}>
              Choose the method that works best for you
            </Paragraph>
          </Card>

          <div style={{ display: 'flex', gap: 30, justifyContent: 'center', flexWrap: 'wrap' }}>
            {/* Structured Method */}
            <Card
              className="feature-card"
              hoverable
              style={{
                width: 400,
                height: 300,
                borderColor: '#1890FF',
                borderWidth: 2,
                cursor: 'pointer'
              }}
              bodyStyle={{ padding: 30, textAlign: 'center' }}
              onClick={() => handleMethodSelect('structured')}
            >
              <FormOutlined style={{ fontSize: 64, color: '#1890FF', marginBottom: 20 }} />
              <Title level={3} style={{ color: '#1890FF', marginBottom: 16 }}>
                Structured Form
              </Title>
              <Paragraph style={{ fontSize: 14, color: '#666', marginBottom: 20 }}>
                Step-by-step guided process with predefined categories. 
                Best for specific, well-defined issues.
              </Paragraph>
              <div style={{ marginTop: 20 }}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>
                  ✅ Faster processing<br />
                  ✅ Accurate categorization<br />
                  ✅ Required field validation
                </div>
              </div>
            </Card>

            {/* AI Method */}
            <Card
              className="feature-card"
              hoverable
              style={{
                width: 400,
                height: 300,
                borderColor: '#52C41A',
                borderWidth: 2,
                cursor: 'pointer'
              }}
              bodyStyle={{ padding: 30, textAlign: 'center' }}
              onClick={() => handleMethodSelect('ai')}
            >
              <RobotOutlined style={{ fontSize: 64, color: '#52C41A', marginBottom: 20 }} />
              <Title level={3} style={{ color: '#52C41A', marginBottom: 16 }}>
                AI Chatbot
              </Title>
              <Paragraph style={{ fontSize: 14, color: '#666', marginBottom: 20 }}>
                Natural conversation with our AI assistant. 
                Describe your issue in your own words.
              </Paragraph>
              <div style={{ marginTop: 20 }}>
                <div style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>
                  ✅ Natural language processing<br />
                  ✅ Conversational interface<br />
                  ✅ Smart categorization
                </div>
              </div>
            </Card>
          </div>

          {/* Help Section */}
          <Card 
            style={{ 
              marginTop: 40,
              background: 'linear-gradient(135deg, #FFF8E1 0%, #F3E5F5 100%)',
              border: '2px solid #FFE082',
              textAlign: 'center'
            }}
          >
            <Title level={4} style={{ color: '#FF6B35' }}>
              🌟 New to SmartGriev?
            </Title>
            <Paragraph>
              We recommend starting with the <strong>Structured Form</strong> for faster processing.
              You can always switch to the AI Chatbot later if needed.
            </Paragraph>
            <div style={{ marginTop: 20 }}>
              <Button type="link" href="/help" target="_blank">
                📖 View Help Guide
              </Button>
              <Button type="link" href="/faq" target="_blank">
                ❓ Frequently Asked Questions
              </Button>
              <Button type="link" href="tel:1800-XXX-XXXX">
                📞 Call Support
              </Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  // Category Selection Step
  if (state.step === 'category') {
    return (
      <ComplaintCategorySelector
        onCategorySelect={handleCategorySelect}
      />
    );
  }

  // Form Step
  if (state.step === 'form' && state.category && state.subcategory && state.component) {
    return (
      <ComplaintDetailsForm
        category={state.category}
        subcategory={state.subcategory}
        component={state.component}
        onSubmit={handleFormSubmit}
        onBack={handleBack}
      />
    );
  }

  // AI Chatbot Step
  if (state.step === 'ai') {
    return (
      <div style={{ padding: '20px', background: '#F5F5F5', minHeight: '100vh' }}>
        <Card style={{ maxWidth: 800, margin: '0 auto', textAlign: 'center' }}>
          <RobotOutlined style={{ fontSize: 64, color: '#52C41A', marginBottom: 20 }} />
          <Title level={2}>AI Chatbot Coming Soon!</Title>
          <Paragraph style={{ fontSize: 16 }}>
            Our intelligent chatbot is currently under development. 
            In the meantime, please use our structured form for submitting complaints.
          </Paragraph>
          <div style={{ marginTop: 30 }}>
            <Button type="primary" size="large" onClick={() => handleMethodSelect('structured')}>
              Use Structured Form
            </Button>
            <Button style={{ marginLeft: 16 }} onClick={handleStartOver}>
              Back to Options
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // Success Step
  if (state.step === 'success') {
    return (
      <div style={{ padding: '20px', background: '#F5F5F5', minHeight: '100vh' }}>
        <div style={{ maxWidth: 600, margin: '0 auto' }}>
          <Result
            status="success"
            title="Complaint Successfully Submitted!"
            subTitle={
              <div>
                <p>Your complaint has been registered with ID: <strong>{state.complaintId}</strong></p>
                <p>Expected resolution time: <strong>{state.category?.estimatedResolutionTime}</strong></p>
                <p>Responsible department: <strong>{state.category?.responsibleDepartment}</strong></p>
              </div>
            }
            extra={[
              <Button type="primary" key="track" className="primary-button">
                Track Complaint Status
              </Button>,
              <Button key="new" onClick={handleStartOver}>
                Submit Another Complaint
              </Button>,
            ]}
          />
          
          <Card style={{ marginTop: 20 }}>
            <Title level={4}>Next Steps:</Title>
            <div style={{ textAlign: 'left' }}>
              <p>📧 Confirmation email sent to your registered address</p>
              <p>📱 SMS updates will be sent for status changes</p>
              <p>🔍 You can track progress using the complaint ID</p>
              <p>📞 For urgent matters, call our helpline: 1800-XXX-XXXX</p>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return null;
};

export default ComplaintSubmissionFlow;