import React, { useState } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  Button, 
  Upload, 
  Select, 
  DatePicker, 
  Row, 
  Col,
  Steps,
  Typography,
  Alert,
  Tag,
  Space,
  Divider,
  Progress,
  Tooltip
} from 'antd';
import { 
  UploadOutlined, 
  EnvironmentOutlined,
  CameraOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import { ComplaintCategory, ComplaintSubcategory, ComplaintComponent } from '@/types/ComplaintCategories';

const { Title, Text, Paragraph } = Typography;
const { TextArea: AntTextArea } = Input;

interface Props {
  category: ComplaintCategory;
  subcategory: ComplaintSubcategory;
  component: ComplaintComponent;
  onSubmit: (formData: any) => void;
  onBack: () => void;
}

const ComplaintDetailsForm: React.FC<Props> = ({ 
  category, 
  subcategory, 
  component, 
  onSubmit, 
  onBack 
}) => {
  const [form] = Form.useForm();
  const [currentStep, setCurrentStep] = useState(0);
  const [fileList, setFileList] = useState<any[]>([]);
  const [formProgress, setFormProgress] = useState(0);

  const calculateProgress = (changedValues: any, allValues: any) => {
    const totalFields = component.requiredFields.length + component.optionalFields.length;
    const filledFields = Object.values(allValues).filter(value => 
      value !== undefined && value !== null && value !== ''
    ).length;
    
    const progress = Math.round((filledFields / totalFields) * 100);
    setFormProgress(Math.min(progress, 100));
  };

  const handleFormChange = (changedValues: any, allValues: any) => {
    calculateProgress(changedValues, allValues);
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

  const renderField = (fieldName: string, isRequired: boolean) => {
    const fieldKey = fieldName.toLowerCase().replace(/\s+/g, '_');
    
    // Special field handling
    if (fieldName.toLowerCase().includes('location') || fieldName.toLowerCase().includes('address')) {
      return (
        <Form.Item
          name={fieldKey}
          label={
            <span>
              <EnvironmentOutlined style={{ marginRight: 8, color: '#1890FF' }} />
              {fieldName}
              {isRequired && <span style={{ color: '#FF4D4F' }}> *</span>}
            </span>
          }
          rules={isRequired ? [{ required: true, message: `Please provide ${fieldName}` }] : []}
        >
          <Input.TextArea 
            rows={3}
            placeholder={`Enter detailed ${fieldName.toLowerCase()}`}
            style={{ borderColor: isRequired ? '#FF9933' : undefined }}
          />
        </Form.Item>
      );
    }

    if (fieldName.toLowerCase().includes('date') || fieldName.toLowerCase().includes('time')) {
      return (
        <Form.Item
          name={fieldKey}
          label={
            <span>
              {fieldName}
              {isRequired && <span style={{ color: '#FF4D4F' }}> *</span>}
            </span>
          }
          rules={isRequired ? [{ required: true, message: `Please select ${fieldName}` }] : []}
        >
          <DatePicker 
            showTime={fieldName.toLowerCase().includes('time')}
            style={{ width: '100%', borderColor: isRequired ? '#FF9933' : undefined }}
            placeholder={`Select ${fieldName.toLowerCase()}`}
          />
        </Form.Item>
      );
    }

    if (fieldName.toLowerCase().includes('priority') || fieldName.toLowerCase().includes('urgency')) {
      return (
        <Form.Item
          name={fieldKey}
          label={
            <span>
              {fieldName}
              {isRequired && <span style={{ color: '#FF4D4F' }}> *</span>}
            </span>
          }
          rules={isRequired ? [{ required: true, message: `Please select ${fieldName}` }] : []}
        >
          <Select 
            placeholder={`Select ${fieldName.toLowerCase()}`}
            style={{ borderColor: isRequired ? '#FF9933' : undefined }}
          >
            <Select.Option value="low">Low</Select.Option>
            <Select.Option value="medium">Medium</Select.Option>
            <Select.Option value="high">High</Select.Option>
            <Select.Option value="urgent">Urgent</Select.Option>
          </Select>
        </Form.Item>
      );
    }

    if (fieldName.toLowerCase().includes('description') || fieldName.toLowerCase().includes('details')) {
      return (
        <Form.Item
          name={fieldKey}
          label={
            <span>
              <FileTextOutlined style={{ marginRight: 8, color: '#1890FF' }} />
              {fieldName}
              {isRequired && <span style={{ color: '#FF4D4F' }}> *</span>}
            </span>
          }
          rules={isRequired ? [
            { required: true, message: `Please provide ${fieldName}` },
            { min: 20, message: 'Please provide at least 20 characters for a detailed description' }
          ] : []}
        >
          <Input.TextArea 
            rows={4}
            placeholder={`Provide detailed ${fieldName.toLowerCase()}...`}
            style={{ borderColor: isRequired ? '#FF9933' : undefined }}
            showCount
            maxLength={1000}
          />
        </Form.Item>
      );
    }

    // Default text input
    return (
      <Form.Item
        name={fieldKey}
        label={
          <span>
            {fieldName}
            {isRequired && <span style={{ color: '#FF4D4F' }}> *</span>}
          </span>
        }
        rules={isRequired ? [{ required: true, message: `Please provide ${fieldName}` }] : []}
      >
        <Input 
          placeholder={`Enter ${fieldName.toLowerCase()}`}
          style={{ borderColor: isRequired ? '#FF9933' : undefined }}
        />
      </Form.Item>
    );
  };

  const handleSubmit = async (values: any) => {
    try {
      const formData = {
        ...values,
        category: category.id,
        subcategory: subcategory.id,
        component: component.id,
        attachments: fileList,
        metadata: {
          categoryName: category.name,
          subcategoryName: subcategory.name,
          componentName: component.name,
          severity: component.severity,
          priority: category.priority,
          estimatedResolutionTime: category.estimatedResolutionTime,
          responsibleDepartment: category.responsibleDepartment
        }
      };
      
      onSubmit(formData);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  return (
    <div style={{ padding: '20px', background: '#F5F5F5', minHeight: '100vh' }}>
      {/* Header */}
      <Card style={{ marginBottom: 20, borderColor: getSeverityColor(component.severity), borderWidth: 2 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span style={{ fontSize: 32, marginRight: 16 }}>{component.icon}</span>
            <div>
              <Title level={3} style={{ margin: 0, color: getSeverityColor(component.severity) }}>
                {component.name}
              </Title>
              <div style={{ marginTop: 8 }}>
                <Tag color={category.color}>{category.name}</Tag>
                <Tag color="blue">{subcategory.name}</Tag>
                <Tag color={getSeverityColor(component.severity)} style={{ fontWeight: 'bold' }}>
                  {component.severity.toUpperCase()}
                </Tag>
              </div>
            </div>
          </div>
          <Button onClick={onBack}>
            Change Selection
          </Button>
        </div>
        
        {/* Progress Bar */}
        <div style={{ marginTop: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <Text strong>Form Completion</Text>
            <Text>{formProgress}%</Text>
          </div>
          <Progress 
            percent={formProgress} 
            strokeColor={{
              '0%': '#FF9933',
              '100%': '#138808',
            }}
            trailColor="#E0E0E0"
          />
        </div>
      </Card>

      {/* Form */}
      <Card>
        <Title level={4} style={{ marginBottom: 20 }}>
          📝 Complaint Details
        </Title>
        
        {/* Examples Section */}
        <Alert
          message="Examples of this issue:"
          description={
            <div style={{ marginTop: 8 }}>
              {component.examples.map((example, index) => (
                <Tag key={index} style={{ margin: '2px 4px 2px 0' }}>
                  {example}
                </Tag>
              ))}
            </div>
          }
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          onValuesChange={handleFormChange}
        >
          {/* Required Fields Section */}
          {component.requiredFields.length > 0 && (
            <>
              <Title level={5} style={{ color: '#FF4D4F', marginBottom: 16 }}>
                <ExclamationCircleOutlined /> Required Information
              </Title>
              <Row gutter={[16, 16]}>
                {component.requiredFields.map((field, index) => (
                  <Col xs={24} sm={12} key={`required-${index}`}>
                    {renderField(field, true)}
                  </Col>
                ))}
              </Row>
              <Divider />
            </>
          )}

          {/* Optional Fields Section */}
          {component.optionalFields.length > 0 && (
            <>
              <Title level={5} style={{ color: '#1890FF', marginBottom: 16 }}>
                <InfoCircleOutlined /> Additional Information (Optional)
              </Title>
              <Row gutter={[16, 16]}>
                {component.optionalFields.map((field, index) => (
                  <Col xs={24} sm={12} key={`optional-${index}`}>
                    {renderField(field, false)}
                  </Col>
                ))}
              </Row>
              <Divider />
            </>
          )}

          {/* File Upload Section */}
          {(subcategory.requiresEvidence || component.severity === 'critical' || component.severity === 'high') && (
            <>
              <Title level={5} style={{ marginBottom: 16 }}>
                <CameraOutlined /> Evidence & Attachments
                {subcategory.requiresEvidence && <span style={{ color: '#FF4D4F' }}> *</span>}
              </Title>
              
              <Form.Item
                name="attachments"
                rules={subcategory.requiresEvidence ? [
                  { required: true, message: 'Please upload at least one piece of evidence' }
                ] : []}
              >
                <Upload.Dragger
                  multiple
                  listType="picture-card"
                  fileList={fileList}
                  onChange={({ fileList }) => setFileList(fileList)}
                  beforeUpload={() => false} // Prevent auto upload
                  accept="image/*,.pdf,.doc,.docx"
                >
                  <p className="ant-upload-drag-icon">
                    <UploadOutlined style={{ fontSize: 48, color: '#1890FF' }} />
                  </p>
                  <p className="ant-upload-text">
                    Click or drag files to upload
                  </p>
                  <p className="ant-upload-hint">
                    Support for images, PDF, and documents
                  </p>
                </Upload.Dragger>
              </Form.Item>
              
              <Alert
                message="Evidence Guidelines"
                description={
                  <ul style={{ margin: 0, paddingLeft: 16 }}>
                    <li>Photos should be clear and show the issue clearly</li>
                    <li>Include timestamps if possible</li>
                    <li>Multiple angles help with assessment</li>
                    <li>Documents should be legible and relevant</li>
                  </ul>
                }
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
              />
            </>
          )}

          {/* Submission Section */}
          <Card 
            style={{ 
              background: 'linear-gradient(135deg, #E8F5E8 0%, #F0F8FF 100%)',
              border: '2px solid #52C41A',
              marginTop: 24
            }}
          >
            <div style={{ textAlign: 'center' }}>
              <CheckCircleOutlined style={{ fontSize: 32, color: '#52C41A', marginBottom: 16 }} />
              <Title level={4} style={{ marginBottom: 16 }}>
                Ready to Submit?
              </Title>
              <Paragraph style={{ marginBottom: 20 }}>
                Expected Resolution Time: <strong>{category.estimatedResolutionTime}</strong><br />
                Responsible Department: <strong>{category.responsibleDepartment}</strong>
              </Paragraph>
              
              <Space size="large">
                <Button size="large" onClick={onBack}>
                  Review Selection
                </Button>
                <Button 
                  type="primary" 
                  size="large"
                  htmlType="submit"
                  className="primary-button"
                  style={{ minWidth: 150, fontWeight: 'bold' }}
                >
                  Submit Complaint
                </Button>
              </Space>
            </div>
          </Card>
        </Form>
      </Card>
    </div>
  );
};

export default ComplaintDetailsForm;