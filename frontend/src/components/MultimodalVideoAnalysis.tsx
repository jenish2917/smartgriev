import React, { useState } from 'react';
import { Upload, Button, Card, Spin, Alert, Progress, Divider, Tag, Space } from 'antd';
import { InboxOutlined, PlayCircleOutlined, AudioOutlined, EyeOutlined, RobotOutlined } from '@ant-design/icons';
import axios from 'axios';
import './MultimodalVideoAnalysis.css';

const { Dragger } = Upload;

interface AnalysisResult {
  success: boolean;
  analysis_summary: string;
  emotion_detected: string;
  urgency_level: string;
  identified_objects: string[];
  scene_context: string;
  extracted_text: string;
  transcribed_audio: string;
  ai_reply: string;
  suggested_department: string;
  suggested_priority: string;
  processing_time: number;
  video_metadata?: {
    duration: number;
    fps: number;
    frame_count: number;
    width: number;
    height: number;
  };
}

const MultimodalVideoAnalysis: React.FC = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (info: any) => {
    const { file } = info;
    
    if (file.status === 'removed') {
      setVideoFile(null);
      setAnalysisResult(null);
      setError(null);
      return;
    }

    // Validate file type
    const isVideo = file.type.startsWith('video/');
    if (!isVideo) {
      setError('Please upload a valid video file');
      return;
    }

    // Validate file size (max 100MB)
    const isLt100M = file.size / 1024 / 1024 < 100;
    if (!isLt100M) {
      setError('Video file must be smaller than 100MB');
      return;
    }

    setVideoFile(file.originFileObj || file);
    setError(null);
  };

  const analyzeVideo = async () => {
    if (!videoFile) {
      setError('Please select a video file first');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('video', videoFile);

    // Get Groq API key from environment or user input
    const groqApiKey = process.env.REACT_APP_GROQ_API_KEY;
    if (groqApiKey) {
      formData.append('groq_api_key', groqApiKey);
    }

    try {
      const token = localStorage.getItem('access_token');
      
      const response = await axios.post(
        'http://localhost:8000/api/ml/multimodal/video/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = progressEvent.total
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0;
            setUploadProgress(percentCompleted);
          }
        }
      );

      if (response.data.success) {
        setAnalysisResult(response.data);
        setError(null);
      } else {
        setError(response.data.error || 'Analysis failed');
      }
    } catch (err: any) {
      console.error('Video analysis error:', err);
      setError(err.response?.data?.error || err.message || 'Failed to analyze video');
    } finally {
      setAnalyzing(false);
      setUploadProgress(0);
    }
  };

  const getEmotionColor = (emotion: string) => {
    const colors: Record<string, string> = {
      anger: 'red',
      anxiety: 'orange',
      frustration: 'volcano',
      neutral: 'default',
      unknown: 'default'
    };
    return colors[emotion.toLowerCase()] || 'default';
  };

  const getUrgencyColor = (urgency: string) => {
    const colors: Record<string, string> = {
      high: 'red',
      medium: 'orange',
      low: 'green'
    };
    return colors[urgency.toLowerCase()] || 'default';
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      High: 'error',
      Medium: 'warning',
      Low: 'success'
    };
    return colors[priority] || 'default';
  };

  return (
    <div className="multimodal-video-analysis">
      <Card
        title={
          <Space>
            <PlayCircleOutlined style={{ fontSize: '24px', color: '#FF671F' }} />
            <span>Multimodal Video Complaint Analysis</span>
          </Space>
        }
        className="analysis-card"
      >
        <Alert
          message="Advanced AI-Powered Analysis"
          description="Upload a video complaint to analyze audio (speech, emotion), visual content (objects, scenes), and generate an intelligent response with department routing and priority assessment."
          type="info"
          showIcon
          style={{ marginBottom: '24px' }}
        />

        <Dragger
          name="video"
          multiple={false}
          accept="video/*"
          beforeUpload={() => false}
          onChange={handleFileChange}
          disabled={analyzing}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ color: '#FF671F' }} />
          </p>
          <p className="ant-upload-text">Click or drag video file to this area to upload</p>
          <p className="ant-upload-hint">
            Supports: MP4, AVI, MOV, MKV, WebM (Max: 100MB, 5 minutes duration)
          </p>
        </Dragger>

        {error && (
          <Alert
            message="Error"
            description={error}
            type="error"
            showIcon
            closable
            onClose={() => setError(null)}
            style={{ marginTop: '16px' }}
          />
        )}

        {videoFile && !analyzing && (
          <div style={{ marginTop: '16px', textAlign: 'center' }}>
            <Button
              type="primary"
              size="large"
              icon={<RobotOutlined />}
              onClick={analyzeVideo}
              style={{ background: '#FF671F', borderColor: '#FF671F' }}
            >
              Analyze Video with AI
            </Button>
          </div>
        )}

        {analyzing && (
          <div style={{ marginTop: '24px', textAlign: 'center' }}>
            <Spin size="large" />
            <div style={{ marginTop: '16px' }}>
              <Progress percent={uploadProgress} status="active" />
              <p style={{ marginTop: '8px', color: '#666' }}>
                {uploadProgress === 100 ? 'Processing video... This may take a moment.' : 'Uploading video...'}
              </p>
            </div>
          </div>
        )}

        {analysisResult && (
          <div className="analysis-results" style={{ marginTop: '32px' }}>
            <Divider orientation="left">
              <RobotOutlined /> AI Analysis Results
            </Divider>

            {/* Summary Card */}
            <Card title="📋 Analysis Summary" size="small" style={{ marginBottom: '16px' }}>
              <p>{analysisResult.analysis_summary}</p>
              <Space style={{ marginTop: '12px' }}>
                <Tag color={getEmotionColor(analysisResult.emotion_detected)}>
                  Emotion: {analysisResult.emotion_detected}
                </Tag>
                <Tag color={getUrgencyColor(analysisResult.urgency_level)}>
                  Urgency: {analysisResult.urgency_level}
                </Tag>
                <Tag color={getPriorityColor(analysisResult.suggested_priority)}>
                  Priority: {analysisResult.suggested_priority}
                </Tag>
              </Space>
            </Card>

            {/* Audio Analysis */}
            {analysisResult.transcribed_audio && (
              <Card
                title={<Space><AudioOutlined /> Audio Transcription</Space>}
                size="small"
                style={{ marginBottom: '16px' }}
              >
                <p><strong>Transcribed Speech:</strong></p>
                <p style={{ fontStyle: 'italic', color: '#555' }}>
                  "{analysisResult.transcribed_audio}"
                </p>
              </Card>
            )}

            {/* Visual Analysis */}
            {analysisResult.identified_objects.length > 0 && (
              <Card
                title={<Space><EyeOutlined /> Visual Analysis</Space>}
                size="small"
                style={{ marginBottom: '16px' }}
              >
                <p><strong>Detected Objects:</strong></p>
                <Space wrap style={{ marginTop: '8px' }}>
                  {analysisResult.identified_objects.map((obj, idx) => (
                    <Tag key={idx} color="blue">{obj}</Tag>
                  ))}
                </Space>
                {analysisResult.scene_context && (
                  <div style={{ marginTop: '12px' }}>
                    <p><strong>Scene Context:</strong> {analysisResult.scene_context}</p>
                  </div>
                )}
                {analysisResult.extracted_text && (
                  <div style={{ marginTop: '12px' }}>
                    <p><strong>Extracted Text:</strong> {analysisResult.extracted_text}</p>
                  </div>
                )}
              </Card>
            )}

            {/* AI Response */}
            <Card
              title="🤖 AI-Generated Response"
              size="small"
              style={{ marginBottom: '16px', background: '#f0f9ff', borderColor: '#1890ff' }}
            >
              <p style={{ fontSize: '15px', lineHeight: '1.6' }}>
                {analysisResult.ai_reply}
              </p>
            </Card>

            {/* Department & Priority */}
            <Card title="📍 Routing Information" size="small" style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <p><strong>Suggested Department:</strong></p>
                  <Tag color="green" style={{ fontSize: '14px', padding: '4px 12px' }}>
                    {analysisResult.suggested_department}
                  </Tag>
                </div>
                <div>
                  <p><strong>Priority Level:</strong></p>
                  <Tag color={getPriorityColor(analysisResult.suggested_priority)} style={{ fontSize: '14px', padding: '4px 12px' }}>
                    {analysisResult.suggested_priority}
                  </Tag>
                </div>
              </div>
            </Card>

            {/* Metadata */}
            {analysisResult.video_metadata && (
              <Card title="ℹ️ Video Metadata" size="small">
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '8px' }}>
                  <div><strong>Duration:</strong> {analysisResult.video_metadata.duration.toFixed(2)}s</div>
                  <div><strong>FPS:</strong> {analysisResult.video_metadata.fps.toFixed(2)}</div>
                  <div><strong>Frames:</strong> {analysisResult.video_metadata.frame_count}</div>
                  <div><strong>Resolution:</strong> {analysisResult.video_metadata.width}x{analysisResult.video_metadata.height}</div>
                  <div><strong>Processing Time:</strong> {analysisResult.processing_time.toFixed(2)}s</div>
                </div>
              </Card>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};

export default MultimodalVideoAnalysis;
