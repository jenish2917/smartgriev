import React, { useState, useRef, useCallback } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Upload,
  message,
  Space,
  Typography,
  Tag,
  Progress,
  Alert,
  Row,
  Col,
  Divider,
  Select,
  Modal,
  Steps,
} from 'antd';
import {
  CloudUploadOutlined,
  AudioOutlined,
  CameraOutlined,
  SendOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  HomeOutlined,
  PhoneOutlined,
} from '@ant-design/icons';
import { apiService, validateFile, handleApiError } from '@/services/api';
import type { ComplaintData, ComplaintResponse, Department } from '@/services/api';
import { AxiosError } from 'axios';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { Step } = Steps;
const { Option } = Select;

interface MultiModalComplaintFormProps {
  onSubmitSuccess?: (response: ComplaintResponse) => void;
  userAuthenticated?: boolean;
}

interface FormData {
  text: string;
  location: string;
  audioFile?: File;
  imageFile?: File;
}

export const MultiModalComplaintForm: React.FC<MultiModalComplaintFormProps> = ({
  onSubmitSuccess,
  userAuthenticated = false,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [submissionResult, setSubmissionResult] = useState<ComplaintResponse | null>(null);
  const [processingStatus, setProcessingStatus] = useState<{
    textProcessed: boolean;
    audioProcessed: boolean;
    imageProcessed: boolean;
    departmentClassified: boolean;
  }>({
    textProcessed: false,
    audioProcessed: false,
    imageProcessed: false,
    departmentClassified: false,
  });

  const audioInputRef = useRef<HTMLInputElement>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);

  // Load departments on component mount
  React.useEffect(() => {
    loadDepartments();
  }, []);

  const loadDepartments = async () => {
    try {
      const response = await apiService.getDepartments();
      setDepartments(response);
    } catch (error) {
      console.error('Failed to load departments:', error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];

      recorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setRecordedBlob(blob);
        
        // Create a file from the blob
        const audioFile = new File([blob], 'recorded_audio.wav', { type: 'audio/wav' });
        form.setFieldsValue({ audioFile });
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      message.error('Failed to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const handleFileUpload = (type: 'audio' | 'image') => (file: File) => {
    const error = validateFile(file);
    if (error) {
      message.error(error);
      return false;
    }

    if (type === 'audio') {
      form.setFieldsValue({ audioFile: file });
    } else {
      form.setFieldsValue({ imageFile: file });
    }

    message.success(`${type} file uploaded successfully`);
    return false; // Prevent default upload
  };

  const simulateProcessingSteps = (response: ComplaintResponse) => {
    // Simulate processing steps for better UX
    const steps = [
      { key: 'textProcessed', delay: 500 },
      { key: 'audioProcessed', delay: 1000 },
      { key: 'imageProcessed', delay: 1500 },
      { key: 'departmentClassified', delay: 2000 },
    ];

    steps.forEach(({ key, delay }) => {
      setTimeout(() => {
        setProcessingStatus(prev => ({ ...prev, [key]: true }));
      }, delay);
    });
  };

  const onFinish = async (values: FormData) => {
    if (!userAuthenticated) {
      Modal.confirm({
        title: 'Authentication Required',
        content: 'You need to register or login to submit a complaint. Would you like to continue?',
        onOk: () => {
          // Navigate to auth page
          message.info('Please register or login to continue');
        },
      });
      return;
    }

    setLoading(true);
    setCurrentStep(1);

    try {
      const complaintData: ComplaintData = {
        title: values.text || 'Voice/Audio Complaint',
        description: values.text || 'Multi-modal complaint submission',
        priority: 'medium',
        text: values.text,
        location: values.location,
        audio_file: values.audioFile || undefined,
        image_file: values.imageFile || undefined,
      };

      // Start processing simulation
      simulateProcessingSteps({} as ComplaintResponse);

      const response = await apiService.submitComplaint(complaintData);
      
      setSubmissionResult(response);
      setCurrentStep(2);
      
      message.success('Complaint submitted successfully!');
      
      if (onSubmitSuccess) {
        onSubmitSuccess(response);
      }

    } catch (error) {
      const errorMessage = handleApiError(error as AxiosError);
      message.error(`Failed to submit complaint: ${errorMessage}`);
      setCurrentStep(0);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'blue';
      case 'low': return 'green';
      default: return 'default';
    }
  };

  const renderSubmissionForm = () => (
    <Card title="Submit Your Complaint" className="w-full">
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        requiredMark={false}
      >
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Form.Item
              label="Describe Your Issue"
              name="text"
              rules={[
                { required: true, message: 'Please describe your complaint' },
                { min: 10, message: 'Please provide more details (minimum 10 characters)' }
              ]}
            >
              <TextArea
                rows={4}
                placeholder="Describe your complaint in detail. You can write in Hindi or English. For example: 'बिजली नहीं आ रही है पिछले 2 दिन से' or 'Power outage in my area for 2 days'"
                showCount
                maxLength={1000}
              />
            </Form.Item>
          </Col>

          <Col span={24}>
            <Form.Item
              label="Location"
              name="location"
              rules={[{ required: true, message: 'Please provide your location' }]}
            >
              <Input
                prefix={<HomeOutlined />}
                placeholder="Enter your address or area (e.g., Sector 15, Noida, UP)"
              />
            </Form.Item>
          </Col>

          <Col span={24}>
            <Divider orientation="left">
              <Space>
                <CloudUploadOutlined />
                Additional Evidence (Optional)
              </Space>
            </Divider>
          </Col>

          <Col md={12} xs={24}>
            <Card size="small" title="📸 Upload Image">
              <Form.Item name="imageFile">
                <Upload.Dragger
                  accept="image/*"
                  showUploadList={false}
                  beforeUpload={handleFileUpload('image')}
                >
                  <p className="ant-upload-drag-icon">
                    <CameraOutlined />
                  </p>
                  <p className="ant-upload-text">Upload Image Evidence</p>
                  <p className="ant-upload-hint">
                    Photos of the issue (JPEG, PNG, WebP - Max 10MB)
                  </p>
                </Upload.Dragger>
              </Form.Item>
            </Card>
          </Col>

          <Col md={12} xs={24}>
            <Card size="small" title="🎤 Audio Recording">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Upload.Dragger
                  accept="audio/*"
                  showUploadList={false}
                  beforeUpload={handleFileUpload('audio')}
                >
                  <p className="ant-upload-drag-icon">
                    <AudioOutlined />
                  </p>
                  <p className="ant-upload-text">Upload Audio File</p>
                  <p className="ant-upload-hint">
                    WAV, MP3, M4A files (Max 10MB)
                  </p>
                </Upload.Dragger>
                
                <Divider>OR</Divider>
                
                <Space style={{ width: '100%', justifyContent: 'center' }}>
                  {!isRecording ? (
                    <Button
                      type="primary"
                      icon={<AudioOutlined />}
                      onClick={startRecording}
                      size="large"
                    >
                      Start Recording
                    </Button>
                  ) : (
                    <Button
                      danger
                      icon={<LoadingOutlined />}
                      onClick={stopRecording}
                      size="large"
                    >
                      Stop Recording
                    </Button>
                  )}
                </Space>
                
                {recordedBlob && (
                  <Alert
                    message="Audio recorded successfully"
                    type="success"
                    showIcon
                  />
                )}
              </Space>
            </Card>
          </Col>

          <Col span={24}>
            <Divider />
            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SendOutlined />}
                size="large"
                loading={loading}
                block
              >
                Submit Complaint
              </Button>
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Card>
  );

  const renderProcessingStatus = () => (
    <Card title="Processing Your Complaint" className="w-full">
      <Space direction="vertical" style={{ width: '100%' }}>
        <Progress
          percent={Object.values(processingStatus).filter(Boolean).length * 25}
          status="active"
        />
        
        <Space direction="vertical">
          <div>
            {processingStatus.textProcessed ? (
              <CheckCircleOutlined style={{ color: 'green' }} />
            ) : (
              <LoadingOutlined />
            )}{' '}
            Processing text and enhancing with AI...
          </div>
          
          <div>
            {processingStatus.audioProcessed ? (
              <CheckCircleOutlined style={{ color: 'green' }} />
            ) : (
              <LoadingOutlined />
            )}{' '}
            Converting audio to text...
          </div>
          
          <div>
            {processingStatus.imageProcessed ? (
              <CheckCircleOutlined style={{ color: 'green' }} />
            ) : (
              <LoadingOutlined />
            )}{' '}
            Analyzing image content...
          </div>
          
          <div>
            {processingStatus.departmentClassified ? (
              <CheckCircleOutlined style={{ color: 'green' }} />
            ) : (
              <LoadingOutlined />
            )}{' '}
            Classifying to appropriate department...
          </div>
        </Space>
      </Space>
    </Card>
  );

  const renderSubmissionResult = () => (
    <Card title="Complaint Submitted Successfully" className="w-full">
      <Space direction="vertical" style={{ width: '100%' }}>
        <Alert
          message="Your complaint has been submitted and processed!"
          description={`Complaint ID: ${submissionResult?.complaint_id}`}
          type="success"
          showIcon
        />
        
        <Row gutter={[16, 16]}>
          <Col span={12}>
            <Card size="small">
              <Text strong>Department:</Text>
              <br />
              <Tag color="blue">{submissionResult?.department?.name}</Tag>
            </Card>
          </Col>
          
          <Col span={12}>
            <Card size="small">
              <Text strong>Urgency Level:</Text>
              <br />
              <Tag color={getUrgencyColor(submissionResult?.urgency_level || '')}>
                {submissionResult?.urgency_level?.toUpperCase()}
              </Tag>
            </Card>
          </Col>
          
          <Col span={24}>
            <Card size="small">
              <Text strong>Estimated Resolution:</Text>
              <br />
              <Text>{submissionResult?.estimated_resolution_days} days</Text>
            </Card>
          </Col>
          
          <Col span={24}>
            <Card size="small">
              <Text strong>Enhanced Description:</Text>
              <br />
              <Paragraph ellipsis={{ rows: 3, expandable: true }}>
                {submissionResult?.processed_text}
              </Paragraph>
            </Card>
          </Col>
        </Row>
        
        <Button type="primary" onClick={() => {
          setCurrentStep(0);
          setSubmissionResult(null);
          form.resetFields();
        }}>
          Submit Another Complaint
        </Button>
      </Space>
    </Card>
  );

  return (
    <div className="max-w-4xl mx-auto p-4">
      <Steps current={currentStep} className="mb-6">
        <Step title="Compose" description="Describe your complaint" />
        <Step title="Processing" description="AI analysis in progress" />
        <Step title="Submitted" description="Complaint processed" />
      </Steps>

      {currentStep === 0 && renderSubmissionForm()}
      {currentStep === 1 && renderProcessingStatus()}
      {currentStep === 2 && renderSubmissionResult()}
    </div>
  );
};

export default MultiModalComplaintForm;