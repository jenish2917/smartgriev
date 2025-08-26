import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Typography,
  Space,
  Button,
  Tag,
  Progress,
  Row,
  Col,
  Statistic,
  Select,
  Modal,
  Form,
  Input,
  Upload,
  Alert,
  Tabs,
  List,
  Tooltip,
} from 'antd';
import {
  ExperimentOutlined,
  RobotOutlined,
  CloudUploadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  DownloadOutlined,
  DeleteOutlined,
  SettingOutlined,
  EyeOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { TabsProps } from 'antd/es/tabs';
import { Line, Column } from '@ant-design/plots';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface MLModel {
  id: string;
  name: string;
  model_type: 'sentiment' | 'classification' | 'ner' | 'clustering';
  version: string;
  accuracy: number;
  is_active: boolean;
  supported_languages: string[];
  created_at: string;
  last_trained: string;
  model_size: number;
  predictions_count: number;
  framework: 'tensorflow' | 'pytorch' | 'scikit-learn' | 'spacy';
}

interface ModelPrediction {
  id: string;
  model_id: string;
  input_text: string;
  prediction: any;
  confidence: number;
  processing_time: number;
  created_at: string;
}

interface TrainingMetric {
  epoch: number;
  accuracy: number;
  loss: number;
  val_accuracy: number;
  val_loss: number;
}

const MLModels: React.FC = () => {
  const [models, setModels] = useState<MLModel[]>([]);
  const [predictions, setPredictions] = useState<ModelPrediction[]>([]);
  const [trainingMetrics, setTrainingMetrics] = useState<TrainingMetric[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<MLModel | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [testModalVisible, setTestModalVisible] = useState(false);
  const [testText, setTestText] = useState('');
  const [testResult, setTestResult] = useState<any>(null);

  // Mock data
  const mockModels: MLModel[] = [
    {
      id: 'model-001',
      name: 'Sentiment Analyzer',
      model_type: 'sentiment',
      version: '2.1.0',
      accuracy: 0.94,
      is_active: true,
      supported_languages: ['en', 'hi', 'mr'],
      created_at: '2024-01-10T00:00:00Z',
      last_trained: '2024-01-15T10:30:00Z',
      model_size: 125.5,
      predictions_count: 15420,
      framework: 'tensorflow',
    },
    {
      id: 'model-002',
      name: 'Complaint Classifier',
      model_type: 'classification',
      version: '1.8.2',
      accuracy: 0.89,
      is_active: true,
      supported_languages: ['en', 'hi'],
      created_at: '2024-01-08T00:00:00Z',
      last_trained: '2024-01-14T14:20:00Z',
      model_size: 89.2,
      predictions_count: 8765,
      framework: 'scikit-learn',
    },
    {
      id: 'model-003',
      name: 'Named Entity Recognition',
      model_type: 'ner',
      version: '3.2.1',
      accuracy: 0.91,
      is_active: false,
      supported_languages: ['en', 'hi', 'mr', 'gu'],
      created_at: '2024-01-05T00:00:00Z',
      last_trained: '2024-01-12T09:15:00Z',
      model_size: 205.8,
      predictions_count: 5432,
      framework: 'spacy',
    },
  ];

  const mockTrainingMetrics: TrainingMetric[] = [
    { epoch: 1, accuracy: 0.72, loss: 0.85, val_accuracy: 0.69, val_loss: 0.91 },
    { epoch: 2, accuracy: 0.81, loss: 0.62, val_accuracy: 0.78, val_loss: 0.68 },
    { epoch: 3, accuracy: 0.87, loss: 0.45, val_accuracy: 0.84, val_loss: 0.52 },
    { epoch: 4, accuracy: 0.91, loss: 0.34, val_accuracy: 0.88, val_loss: 0.41 },
    { epoch: 5, accuracy: 0.94, loss: 0.28, val_accuracy: 0.91, val_loss: 0.35 },
  ];

  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setModels(mockModels);
      setTrainingMetrics(mockTrainingMetrics);
      setLoading(false);
    }, 1000);
  }, []);

  const modelColumns: ColumnsType<MLModel> = [
    {
      title: 'Model Name',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <Space direction="vertical" size={0}>
          <Text strong>{name}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.model_type.toUpperCase()} • v{record.version}
          </Text>
        </Space>
      ),
    },
    {
      title: 'Framework',
      dataIndex: 'framework',
      key: 'framework',
      render: (framework) => (
        <Tag color="blue">{framework.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Accuracy',
      dataIndex: 'accuracy',
      key: 'accuracy',
      render: (accuracy) => (
        <Space>
          <Progress
            type="circle"
            size={40}
            percent={Math.round(accuracy * 100)}
            strokeColor={accuracy >= 0.9 ? '#52c41a' : accuracy >= 0.8 ? '#faad14' : '#f5222d'}
          />
          <Text>{(accuracy * 100).toFixed(1)}%</Text>
        </Space>
      ),
    },
    {
      title: 'Languages',
      dataIndex: 'supported_languages',
      key: 'supported_languages',
      render: (languages) => (
        <Space wrap>
          {languages.slice(0, 3).map((lang: string) => (
            <Tag key={lang}>{lang.toUpperCase()}</Tag>
          ))}
          {languages.length > 3 && <Tag>+{languages.length - 3}</Tag>}
        </Space>
      ),
    },
    {
      title: 'Predictions',
      dataIndex: 'predictions_count',
      key: 'predictions_count',
      render: (count) => count.toLocaleString(),
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'ACTIVE' : 'INACTIVE'}
        </Tag>
      ),
    },
    {
      title: 'Size',
      dataIndex: 'model_size',
      key: 'model_size',
      render: (size) => `${size} MB`,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title="View Details">
            <Button
              size="small"
              icon={<EyeOutlined />}
              onClick={() => viewModelDetails(record)}
            />
          </Tooltip>
          <Tooltip title="Test Model">
            <Button
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => testModel(record)}
              disabled={!record.is_active}
            />
          </Tooltip>
          <Tooltip title="Configure">
            <Button
              size="small"
              icon={<SettingOutlined />}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const viewModelDetails = (model: MLModel) => {
    setSelectedModel(model);
    setIsModalVisible(true);
  };

  const testModel = (model: MLModel) => {
    setSelectedModel(model);
    setTestModalVisible(true);
    setTestText('');
    setTestResult(null);
  };

  const runModelTest = async () => {
    if (!testText.trim() || !selectedModel) return;

    // Simulate API call
    setLoading(true);
    setTimeout(() => {
      const mockResult = {
        prediction: selectedModel.model_type === 'sentiment' 
          ? { label: 'POSITIVE', score: 0.85 }
          : selectedModel.model_type === 'classification'
          ? { category: 'Infrastructure', confidence: 0.92 }
          : { entities: [{ text: 'street light', label: 'INFRASTRUCTURE' }] },
        confidence: 0.85,
        processing_time: 45,
      };
      setTestResult(mockResult);
      setLoading(false);
    }, 1500);
  };

  const activeModels = models.filter(m => m.is_active).length;
  const avgAccuracy = models.reduce((acc, m) => acc + m.accuracy, 0) / models.length;
  const totalPredictions = models.reduce((acc, m) => acc + m.predictions_count, 0);

  const accuracyChartConfig = {
    data: trainingMetrics,
    xField: 'epoch',
    yField: 'accuracy',
    seriesField: 'type',
    color: ['#1890ff', '#52c41a'],
  };

  const tabItems: TabsProps['items'] = [
    {
      key: 'models',
      label: 'Model Management',
      children: (
        <Table
          columns={modelColumns}
          dataSource={models}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      ),
    },
    {
      key: 'training',
      label: 'Training Metrics',
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Training Progress">
              <Line {...accuracyChartConfig} />
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: 'experiments',
      label: 'Experiments',
      children: (
        <Alert
          message="A/B Testing & Experiments"
          description="Model performance comparison and experiment tracking functionality will be available soon."
          type="info"
          showIcon
        />
      ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={2} className="gov-title">
          Machine Learning Models
        </Title>
        <Text className="gov-subtitle">
          Manage and monitor AI models for intelligent complaint processing
        </Text>
      </div>

      {/* Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Models"
              value={models.length}
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Active Models"
              value={activeModels}
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Avg Accuracy"
              value={avgAccuracy}
              precision={1}
              suffix="%"
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#722ed1' }}
              formatter={(value) => `${((value as number) * 100).toFixed(1)}%`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Predictions"
              value={totalPredictions}
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#13c2c2' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Button type="primary" icon={<CloudUploadOutlined />}>
            Upload New Model
          </Button>
          <Button icon={<PlayCircleOutlined />}>
            Train Model
          </Button>
          <Button icon={<ExperimentOutlined />}>
            Create Experiment
          </Button>
          <Button icon={<DownloadOutlined />}>
            Export Models
          </Button>
        </Space>
      </Card>

      {/* Main Content */}
      <Card>
        <Tabs
          defaultActiveKey="models"
          items={tabItems}
        />
      </Card>

      {/* Model Details Modal */}
      <Modal
        title={selectedModel?.name}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setIsModalVisible(false)}>
            Close
          </Button>,
        ]}
        width={700}
      >
        {selectedModel && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Text strong>Model Type:</Text><br />
                <Text>{selectedModel.model_type.toUpperCase()}</Text>
              </Col>
              <Col span={12}>
                <Text strong>Framework:</Text><br />
                <Text>{selectedModel.framework}</Text>
              </Col>
              <Col span={12}>
                <Text strong>Version:</Text><br />
                <Text>{selectedModel.version}</Text>
              </Col>
              <Col span={12}>
                <Text strong>Accuracy:</Text><br />
                <Text>{(selectedModel.accuracy * 100).toFixed(1)}%</Text>
              </Col>
              <Col span={12}>
                <Text strong>Model Size:</Text><br />
                <Text>{selectedModel.model_size} MB</Text>
              </Col>
              <Col span={12}>
                <Text strong>Predictions:</Text><br />
                <Text>{selectedModel.predictions_count.toLocaleString()}</Text>
              </Col>
            </Row>
            
            <div>
              <Text strong>Supported Languages:</Text><br />
              <Space wrap style={{ marginTop: 4 }}>
                {selectedModel.supported_languages.map(lang => (
                  <Tag key={lang}>{lang.toUpperCase()}</Tag>
                ))}
              </Space>
            </div>

            <div>
              <Text strong>Last Training:</Text><br />
              <Text>{new Date(selectedModel.last_trained).toLocaleString()}</Text>
            </div>
          </Space>
        )}
      </Modal>

      {/* Test Model Modal */}
      <Modal
        title={`Test Model: ${selectedModel?.name}`}
        open={testModalVisible}
        onCancel={() => setTestModalVisible(false)}
        footer={[
          <Button key="cancel" onClick={() => setTestModalVisible(false)}>
            Cancel
          </Button>,
          <Button
            key="test"
            type="primary"
            loading={loading}
            onClick={runModelTest}
            disabled={!testText.trim()}
          >
            Run Test
          </Button>,
        ]}
        width={600}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Alert
            message="Model Testing"
            description="Enter text below to test the model's prediction capabilities."
            type="info"
            showIcon
          />
          
          <div>
            <Text strong>Input Text:</Text>
            <TextArea
              rows={4}
              placeholder="Enter text to analyze..."
              value={testText}
              onChange={(e) => setTestText(e.target.value)}
              style={{ marginTop: 8 }}
            />
          </div>

          {testResult && (
            <Card title="Prediction Result" size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Row>
                  <Col span={12}>
                    <Text strong>Confidence:</Text><br />
                    <Progress percent={Math.round(testResult.confidence * 100)} />
                  </Col>
                  <Col span={12}>
                    <Text strong>Processing Time:</Text><br />
                    <Text>{testResult.processing_time}ms</Text>
                  </Col>
                </Row>
                
                <div>
                  <Text strong>Prediction:</Text><br />
                  <pre style={{ background: '#f5f5f5', padding: 8, borderRadius: 4 }}>
                    {JSON.stringify(testResult.prediction, null, 2)}
                  </pre>
                </div>
              </Space>
            </Card>
          )}
        </Space>
      </Modal>
    </div>
  );
};

export default MLModels;
