/**
 * SmartGriev OCR Integration - Frontend Example
 * 
 * This file demonstrates how to integrate the OCR API with the React frontend
 * to allow users to upload images and extract text for complaint processing.
 */

import React, { useState } from 'react';
import axios from 'axios';

// API configuration
const API_BASE_URL = 'http://127.0.0.1:8000';
const OCR_ENDPOINTS = {
  health: `${API_BASE_URL}/api/ml/ocr/health/`,
  basic: `${API_BASE_URL}/api/ml/ocr/`,
  complaint: `${API_BASE_URL}/api/ml/ocr/complaint/`
};

/**
 * OCR Service for API interactions
 */
class OCRService {
  constructor(authToken) {
    this.authToken = authToken;
    this.headers = {
      'Authorization': `Bearer ${authToken}`
    };
  }

  /**
   * Check OCR service health
   */
  async checkHealth() {
    try {
      const response = await axios.get(OCR_ENDPOINTS.health, {
        headers: this.headers
      });
      return response.data;
    } catch (error) {
      console.error('OCR health check failed:', error);
      throw error;
    }
  }

  /**
   * Process image with basic OCR
   */
  async processImage(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      const response = await axios.post(OCR_ENDPOINTS.basic, formData, {
        headers: {
          ...this.headers,
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('OCR processing failed:', error);
      throw error;
    }
  }

  /**
   * Process complaint image with NLP analysis
   */
  async processComplaintImage(imageFile, options = {}) {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('extract_entities', options.extractEntities || true);
    formData.append('classify_complaint', options.classifyComplaint || true);

    try {
      const response = await axios.post(OCR_ENDPOINTS.complaint, formData, {
        headers: {
          ...this.headers,
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Complaint OCR processing failed:', error);
      throw error;
    }
  }
}

/**
 * React Component for OCR Image Upload
 */
const OCRImageUpload = ({ authToken, onTextExtracted }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [ocrService] = useState(() => new OCRService(authToken));

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setError('File too large. Maximum size is 10MB.');
        return;
      }

      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        setError('Unsupported file type. Please select JPEG, PNG, BMP, TIFF, or GIF.');
        return;
      }

      setSelectedFile(file);
      setError(null);
      setResult(null);
    }
  };

  const processImage = async (useComplaintOCR = false) => {
    if (!selectedFile) return;

    setProcessing(true);
    setError(null);

    try {
      let result;
      if (useComplaintOCR) {
        result = await ocrService.processComplaintImage(selectedFile, {
          extractEntities: true,
          classifyComplaint: true
        });
      } else {
        result = await ocrService.processImage(selectedFile);
      }

      setResult(result);
      
      // Callback to parent component
      if (onTextExtracted) {
        onTextExtracted(result.extracted_text, result);
      }
    } catch (err) {
      setError(err.response?.data?.error_message || 'OCR processing failed');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="ocr-upload-container">
      <h3>Upload Image for Text Extraction</h3>
      
      {/* File Input */}
      <div className="file-input-section">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          disabled={processing}
          className="file-input"
        />
        
        {selectedFile && (
          <div className="file-info">
            <p>Selected: {selectedFile.name}</p>
            <p>Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        )}
      </div>

      {/* Processing Buttons */}
      {selectedFile && (
        <div className="action-buttons">
          <button
            onClick={() => processImage(false)}
            disabled={processing}
            className="btn btn-primary"
          >
            {processing ? 'Processing...' : 'Extract Text (Basic)'}
          </button>
          
          <button
            onClick={() => processImage(true)}
            disabled={processing}
            className="btn btn-secondary"
          >
            {processing ? 'Processing...' : 'Process Complaint (Advanced)'}
          </button>
        </div>
      )}

      {/* Loading Indicator */}
      {processing && (
        <div className="processing-indicator">
          <div className="spinner"></div>
          <p>Processing image... This may take a few seconds.</p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="ocr-results">
          <h4>OCR Results</h4>
          
          <div className="result-section">
            <h5>Extracted Text:</h5>
            <div className="extracted-text">
              {result.extracted_text || 'No text found in image'}
            </div>
          </div>

          <div className="result-stats">
            <p><strong>Characters:</strong> {result.text_length}</p>
            <p><strong>Processing Time:</strong> {result.processing_time?.toFixed(2)}s</p>
            <p><strong>Status:</strong> {result.status}</p>
          </div>

          {/* Advanced Results (if using complaint OCR) */}
          {result.entities && (
            <div className="nlp-results">
              <h5>Named Entities:</h5>
              <pre>{JSON.stringify(result.entities, null, 2)}</pre>
            </div>
          )}

          {result.classification && (
            <div className="classification-results">
              <h5>Classification:</h5>
              <p><strong>Category:</strong> {result.classification.category}</p>
              <p><strong>Department:</strong> {result.classification.department}</p>
              <p><strong>Confidence:</strong> {result.classification.confidence}</p>
            </div>
          )}

          {result.sentiment && (
            <div className="sentiment-results">
              <h5>Sentiment Analysis:</h5>
              <p><strong>Polarity:</strong> {result.sentiment.polarity}</p>
              <p><strong>Confidence:</strong> {result.sentiment.confidence}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/**
 * Example usage in a complaint form component
 */
const ComplaintFormWithOCR = ({ authToken }) => {
  const [complaintText, setComplaintText] = useState('');
  const [extractedData, setExtractedData] = useState(null);

  const handleTextExtracted = (text, fullResult) => {
    setComplaintText(prev => prev + '\n' + text);
    setExtractedData(fullResult);
  };

  const handleSubmitComplaint = async () => {
    const complaintData = {
      description: complaintText,
      category: extractedData?.classification?.category || 'GENERAL',
      extracted_entities: extractedData?.entities,
      sentiment: extractedData?.sentiment,
      // ... other complaint fields
    };

    try {
      // Submit complaint using your existing API
      const response = await axios.post('/api/complaints/', complaintData, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      console.log('Complaint submitted:', response.data);
    } catch (error) {
      console.error('Failed to submit complaint:', error);
    }
  };

  return (
    <div className="complaint-form-container">
      <h2>Submit New Complaint</h2>
      
      {/* OCR Upload Section */}
      <OCRImageUpload
        authToken={authToken}
        onTextExtracted={handleTextExtracted}
      />
      
      {/* Complaint Text Area */}
      <div className="complaint-text-section">
        <label htmlFor="complaint-description">Complaint Description:</label>
        <textarea
          id="complaint-description"
          value={complaintText}
          onChange={(e) => setComplaintText(e.target.value)}
          placeholder="Describe your complaint here... or upload an image above to extract text automatically"
          rows={6}
          className="complaint-textarea"
        />
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmitComplaint}
        disabled={!complaintText.trim()}
        className="btn btn-success"
      >
        Submit Complaint
      </button>
    </div>
  );
};

// CSS Styles (add to your stylesheet)
const ocrStyles = `
.ocr-upload-container {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  background-color: #f9f9f9;
}

.file-input-section {
  margin-bottom: 15px;
}

.file-input {
  width: 100%;
  padding: 10px;
  border: 2px dashed #ccc;
  border-radius: 4px;
  background-color: white;
}

.file-info {
  margin-top: 10px;
  padding: 10px;
  background-color: #e9ecef;
  border-radius: 4px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin: 15px 0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.processing-indicator {
  text-align: center;
  padding: 20px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}

.ocr-results {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin-top: 15px;
}

.extracted-text {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 10px;
  font-family: monospace;
  white-space: pre-wrap;
  min-height: 60px;
}

.result-stats {
  display: flex;
  gap: 20px;
  margin: 10px 0;
}

.nlp-results, .classification-results, .sentiment-results {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.complaint-textarea {
  width: 100%;
  min-height: 120px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
}
`;

export {
  OCRService,
  OCRImageUpload,
  ComplaintFormWithOCR,
  ocrStyles
};