import React, { useState } from 'react';
import { Card, Button, Typography, Space, Tag, Steps, Row, Col, Collapse, Alert, Tooltip } from 'antd';
import { 
  ArrowRightOutlined, 
  CheckCircleOutlined, 
  InfoCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  EnvironmentOutlined,
  CameraOutlined
} from '@ant-design/icons';
import { COMPLAINT_CATEGORIES, ComplaintCategory, ComplaintSubcategory, ComplaintComponent } from '@/types/ComplaintCategories';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface Props {
  onCategorySelect: (category: ComplaintCategory, subcategory: ComplaintSubcategory, component: ComplaintComponent) => void;
}

const ComplaintCategorySelector: React.FC<Props> = ({ onCategorySelect }) => {
  const [selectedCategory, setSelectedCategory] = useState<ComplaintCategory | null>(null);
  const [selectedSubcategory, setSelectedSubcategory] = useState<ComplaintSubcategory | null>(null);
  const [currentStep, setCurrentStep] = useState(0);

  const handleCategorySelect = (category: ComplaintCategory) => {
    setSelectedCategory(category);
    setSelectedSubcategory(null);
    setCurrentStep(1);
  };

  const handleSubcategorySelect = (subcategory: ComplaintSubcategory) => {
    setSelectedSubcategory(subcategory);
    setCurrentStep(2);
  };

  const handleComponentSelect = (component: ComplaintComponent) => {
    if (selectedCategory && selectedSubcategory) {
      onCategorySelect(selectedCategory, selectedSubcategory, component);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return '#FF4D4F';
      case 'high': return '#FA8C16';
      case 'medium': return '#1890FF';
      case 'low': return '#52C41A';
      default: return '#1890FF';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#A0202C';
      case 'high': return '#FF4D4F';
      case 'medium': return '#FA8C16';
      case 'low': return '#52C41A';
      default: return '#1890FF';
    }
  };

  return (
    <div style={{ padding: '20px', background: '#F5F5F5', minHeight: '100vh' }}>
      {/* Progress Steps */}
      <Card style={{ marginBottom: 20, border: '2px solid #FF9933' }}>
        <Title level={3} style={{ textAlign: 'center', marginBottom: 20, color: '#FF9933' }}>
          🎯 Complaint Classification System
        </Title>
        <Steps current={currentStep} style={{ marginBottom: 20 }}>
          <Steps.Step title="Category" description="Select main category" />
          <Steps.Step title="Subcategory" description="Choose specific area" />
          <Steps.Step title="Component" description="Select exact issue" />
        </Steps>
      </Card>

      {/* Step 1: Category Selection */}
      {currentStep === 0 && (
        <div>
          <Title level={3} style={{ textAlign: 'center', marginBottom: 30 }}>
            🎯 Select Complaint Category
          </Title>
          <Row gutter={[20, 20]}>
            {COMPLAINT_CATEGORIES.map((category) => (
              <Col xs={24} sm={12} lg={8} key={category.id}>
                <Card
                  className="feature-card"
                  hoverable
                  onClick={() => handleCategorySelect(category)}
                  style={{
                    height: '100%',
                    borderColor: category.color,
                    borderWidth: 2,
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                  bodyStyle={{ padding: 20 }}
                >
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 48, marginBottom: 16 }}>
                      {category.icon}
                    </div>
                    <Title level={4} style={{ marginBottom: 12, color: category.color }}>
                      {category.name}
                    </Title>
                    <Paragraph style={{ fontSize: 14, color: '#666', marginBottom: 16 }}>
                      {category.description}
                    </Paragraph>
                    
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                      <Tag 
                        color={getPriorityColor(category.priority)}
                        style={{ fontWeight: 'bold' }}
                      >
                        {category.priority.toUpperCase()} Priority
                      </Tag>
                      
                      <div style={{ fontSize: 12, color: '#888' }}>
                        <ClockCircleOutlined /> {category.estimatedResolutionTime}
                      </div>
                      
                      <div style={{ fontSize: 12, color: '#888' }}>
                        <UserOutlined /> {category.responsibleDepartment}
                      </div>
                    </Space>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}

      {/* Step 2: Subcategory Selection */}
      {currentStep === 1 && selectedCategory && (
        <div>
          <Card style={{ marginBottom: 20, borderColor: selectedCategory.color, borderWidth: 2 }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
              <span style={{ fontSize: 32, marginRight: 16 }}>{selectedCategory.icon}</span>
              <div>
                <Title level={3} style={{ margin: 0, color: selectedCategory.color }}>
                  {selectedCategory.name}
                </Title>
                <Text type="secondary">{selectedCategory.description}</Text>
              </div>
              <Button 
                onClick={() => setCurrentStep(0)}
                style={{ marginLeft: 'auto' }}
              >
                Change Category
              </Button>
            </div>
          </Card>

          <Title level={3} style={{ textAlign: 'center', marginBottom: 30 }}>
            🎯 Select Specific Area
          </Title>
          
          <Row gutter={[20, 20]}>
            {selectedCategory.subcategories.map((subcategory) => (
              <Col xs={24} sm={12} lg={12} key={subcategory.id}>
                <Card
                  className="feature-card"
                  hoverable
                  onClick={() => handleSubcategorySelect(subcategory)}
                  style={{
                    height: '100%',
                    borderColor: selectedCategory.color,
                    borderWidth: 2,
                    cursor: 'pointer'
                  }}
                  bodyStyle={{ padding: 20 }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                    <span style={{ fontSize: 32, marginRight: 16 }}>{subcategory.icon}</span>
                    <div style={{ flex: 1 }}>
                      <Title level={4} style={{ marginBottom: 8, color: selectedCategory.color }}>
                        {subcategory.name}
                      </Title>
                      <Paragraph style={{ fontSize: 14, color: '#666', marginBottom: 16 }}>
                        {subcategory.description}
                      </Paragraph>
                      
                      <Space wrap>
                        {subcategory.requiresLocation && (
                          <Tag icon={<EnvironmentOutlined />} color="blue">Location Required</Tag>
                        )}
                        {subcategory.requiresEvidence && (
                          <Tag icon={<CameraOutlined />} color="green">Evidence Required</Tag>
                        )}
                      </Space>
                      
                      <div style={{ marginTop: 12 }}>
                        <Text strong style={{ fontSize: 12 }}>Common Issues:</Text>
                        <div style={{ marginTop: 4 }}>
                          {subcategory.commonIssues.slice(0, 3).map((issue, index) => (
                            <Tag key={index} style={{ margin: '2px', fontSize: '11px' }}>
                              {issue}
                            </Tag>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}

      {/* Step 3: Component Selection */}
      {currentStep === 2 && selectedSubcategory && (
        <div>
          <Card style={{ marginBottom: 20, borderColor: selectedCategory?.color, borderWidth: 2 }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20 }}>
              <span style={{ fontSize: 24, marginRight: 12 }}>{selectedSubcategory.icon}</span>
              <div>
                <Title level={4} style={{ margin: 0, color: selectedCategory?.color }}>
                  {selectedSubcategory.name}
                </Title>
                <Text type="secondary">{selectedSubcategory.description}</Text>
              </div>
              <Button 
                onClick={() => setCurrentStep(1)}
                style={{ marginLeft: 'auto' }}
              >
                Change Subcategory
              </Button>
            </div>
          </Card>

          <Title level={3} style={{ textAlign: 'center', marginBottom: 30 }}>
            🎯 Select Exact Issue
          </Title>
          
          <Row gutter={[20, 20]}>
            {selectedSubcategory.components.map((component) => (
              <Col xs={24} sm={12} lg={8} key={component.id}>
                <Card
                  className="feature-card"
                  hoverable
                  style={{
                    height: '100%',
                    borderColor: getSeverityColor(component.severity),
                    borderWidth: 2,
                    cursor: 'pointer'
                  }}
                  bodyStyle={{ padding: 20 }}
                  actions={[
                    <Button 
                      type="primary"
                      className="primary-button"
                      icon={<ArrowRightOutlined />}
                      onClick={() => handleComponentSelect(component)}
                      style={{ fontWeight: 'bold' }}
                    >
                      Select This Issue
                    </Button>
                  ]}
                >
                  <div style={{ textAlign: 'center', marginBottom: 16 }}>
                    <span style={{ fontSize: 32 }}>{component.icon}</span>
                    <Title level={5} style={{ marginTop: 8, marginBottom: 8 }}>
                      {component.name}
                    </Title>
                    <Tag 
                      color={getSeverityColor(component.severity)}
                      style={{ fontWeight: 'bold', marginBottom: 12 }}
                    >
                      {component.severity.toUpperCase()}
                    </Tag>
                  </div>
                  
                  <Paragraph style={{ fontSize: 13, color: '#666', marginBottom: 16 }}>
                    {component.description}
                  </Paragraph>
                  
                  <Collapse size="small" ghost>
                    <Panel header={<Text strong>Examples & Details</Text>} key="1">
                      <div style={{ fontSize: 12 }}>
                        <div style={{ marginBottom: 8 }}>
                          <Text strong>Examples:</Text>
                          <ul style={{ margin: '4px 0', paddingLeft: 16 }}>
                            {component.examples.map((example, index) => (
                              <li key={index}>{example}</li>
                            ))}
                          </ul>
                        </div>
                        
                        <div style={{ marginBottom: 8 }}>
                          <Text strong>Required Information:</Text>
                          <div style={{ marginTop: 4 }}>
                            {component.requiredFields.map((field, index) => (
                              <Tag key={index} color="red" style={{ margin: '1px', fontSize: '10px' }}>
                                {field}
                              </Tag>
                            ))}
                          </div>
                        </div>
                        
                        {component.optionalFields.length > 0 && (
                          <div>
                            <Text strong>Optional Information:</Text>
                            <div style={{ marginTop: 4 }}>
                              {component.optionalFields.map((field, index) => (
                                <Tag key={index} color="blue" style={{ margin: '1px', fontSize: '10px' }}>
                                  {field}
                                </Tag>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </Panel>
                  </Collapse>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}

      {/* Help Section */}
      <Card 
        style={{ 
          marginTop: 30,
          background: 'linear-gradient(135deg, #FFF8E1 0%, #F3E5F5 100%)',
          border: '2px solid #FFE082'
        }}
      >
        <Alert
          message="💡 Need Help Choosing?"
          description={
            <div>
              <p>If you're unsure about the category, you can:</p>
              <ul>
                <li>🤖 Use our <strong>AI Chatbot</strong> for guided selection</li>
                <li>📞 Call our helpline: <strong>1800-XXX-XXXX</strong></li>
                <li>💬 Use the <strong>AI Classification Tool</strong> to auto-categorize</li>
                <li>📧 Email us at: <strong>support@smartgriev.gov.in</strong></li>
              </ul>
            </div>
          }
          type="info"
          showIcon
        />
      </Card>
    </div>
  );
};

export default ComplaintCategorySelector;