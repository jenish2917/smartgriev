import React, { useState, ChangeEvent, FormEvent, useEffect } from 'react';
import axios from 'axios';
import styles from './MultimodalComplaintSubmit.module.css';
import { API_URLS } from '../config/api.config';

interface FormData {
  title: string;
  description: string;
  priority: string;
  urgency_level: string;
  category: string;
  incident_address: string;
  incident_latitude: number | null;
  incident_longitude: number | null;
}

interface FileState {
  image: File | null;
  audio: File | null;
}

interface PreviewState {
  image: string | null;
  audio: string | null;
}

interface ResultState {
  complaint?: {
    id: number;
    status: string;
  };
  processing_status?: {
    image_processed: boolean;
    audio_processed: boolean;
    ai_classified: boolean;
  };
}

interface ChatMessage {
  type: 'user' | 'bot';
  message: string;
  timestamp: Date;
}

const MultimodalComplaintSubmit = () => {
  // Existing state
  const [formData, setFormData] = useState<FormData>({
    title: '',
    description: '',
    priority: 'medium',
    urgency_level: 'medium',
    category: '',
    incident_address: '',
    incident_latitude: null,
    incident_longitude: null
  });
  
  const [files, setFiles] = useState<FileState>({
    image: null,
    audio: null
  });
  
  const [previews, setPreviews] = useState<PreviewState>({
    image: null,
    audio: null
  });
  
  const [loading, setLoading] = useState<boolean>(false);
  const [success, setSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResultState | null>(null);

  // AI Chatbot state
  const [showChatbot, setShowChatbot] = useState<boolean>(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      type: 'bot',
      message: 'Hello! I\'m your AI assistant. How can I help you file a complaint today?',
      timestamp: new Date()
    }
  ]);
  const [chatInput, setChatInput] = useState<string>('');
  const [chatLoading, setChatLoading] = useState<boolean>(false);

  // Human support state
  const [showHumanSupport, setShowHumanSupport] = useState<boolean>(false);
  const SUPPORT_PHONE = '+91 8141415113';

  const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>, type: keyof FileState) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Update files
    setFiles(prev => ({
      ...prev,
      [type]: file
    }));

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviews(prev => ({
        ...prev,
        [type]: reader.result
      }));
    };
    reader.readAsDataURL(file);
  };

  const removeFile = (type: keyof FileState) => {
    setFiles(prev => ({
      ...prev,
      [type]: null
    }));
    setPreviews(prev => ({
      ...prev,
      [type]: null
    }));
  };

  const getLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            incident_latitude: position.coords.latitude,
            incident_longitude: position.coords.longitude
          }));
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  };

  // AI Chatbot functions
  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage: ChatMessage = {
      type: 'user',
      message: chatInput,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await axios.post(API_URLS.CHATBOT_CHAT(), {
        message: chatInput,
        conversation_history: chatMessages.slice(-10).map(msg => ({
          type: msg.type,
          message: msg.message
        }))
      });

      if (response.data.success) {
        const botMessage: ChatMessage = {
          type: 'bot',
          message: response.data.response,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, botMessage]);
      }
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage: ChatMessage = {
        type: 'bot',
        message: 'Sorry, I encountered an error. Please try again or contact human support.',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleChatKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const token = localStorage.getItem('token');
      
      const submitData = new FormData();
      
      // Add text fields
      Object.keys(formData).forEach(key => {
        const typedKey = key as keyof typeof formData;
        const value = formData[typedKey];
        if (value !== null && value !== '') {
          submitData.append(key, String(value));
        }
      });

      // Add files
      if (files.image) submitData.append('image_file', files.image);
      if (files.audio) submitData.append('audio_file', files.audio);

      // Prepare headers - only add Authorization if token exists
      // DO NOT set Content-Type for FormData - axios will set it automatically with boundary
      const headers: any = {};
      
      // Only send token if user is actually logged in
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await axios.post(
        API_URLS.SUBMIT_COMPLAINT(),
        submitData,
        { 
          headers,
          timeout: 30000  // 30 second timeout to prevent infinite loading
        }
      );

      setSuccess(true);
      setResult(response.data);
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        priority: 'medium',
        urgency_level: 'medium',
        category: '',
        incident_address: '',
        incident_latitude: null,
        incident_longitude: null
      });
      setFiles({ image: null, audio: null });
      setPreviews({ image: null, audio: null });

    } catch (err) {
      const error = err as any;
      console.error('Complaint submission error:', error);
      console.error('Error response:', error.response?.data);
      
      // If 401 error, might be expired token - try without token
      if (error.response?.status === 401) {
        console.log('401 error - attempting anonymous submission...');
        try {
          // Clear potentially bad token
          const submitData = new FormData();
          
          // Add text fields
          Object.keys(formData).forEach(key => {
            const typedKey = key as keyof typeof formData;
            const value = formData[typedKey];
            if (value !== null && value !== '') {
              submitData.append(key, String(value));
            }
          });

          // Add files
          if (files.image) submitData.append('image_file', files.image);
          if (files.audio) submitData.append('audio_file', files.audio);

          // Retry without Authorization header
          const response = await axios.post(
            API_URLS.SUBMIT_COMPLAINT(),
            submitData,
            { 
              headers: {},
              timeout: 30000  // 30 second timeout
            }
          );

          setSuccess(true);
          setResult(response.data);
          
          // Reset form
          setFormData({
            title: '',
            description: '',
            priority: 'medium',
            urgency_level: 'medium',
            category: '',
            incident_address: '',
            incident_latitude: null,
            incident_longitude: null
          });
          setFiles({ image: null, audio: null });
          setPreviews({ image: null, audio: null });
          
          setLoading(false);
          return;
        } catch (retryError) {
          console.error('Retry also failed:', retryError);
        }
      }
      
      // Detailed error message
      let errorMessage = 'Failed to submit complaint';
      
      if (error.response?.data) {
        if (error.response.data.errors) {
          // Validation errors from serializer
          const errors = error.response.data.errors;
          errorMessage = Object.keys(errors).map(key => `${key}: ${errors[key]}`).join(', ');
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Professional Header */}
      <div className={styles.professionalHeader}>
        <h1 className={styles.mainTitle}>SmartGriev Complaint Submission</h1>
        <p className={styles.subtitle}>AI-Powered Grievance Management System</p>
      </div>

      {/* Support Options Bar */}
      <div className={styles.supportBar}>
        <button 
          className={styles.supportButton}
          onClick={() => setShowChatbot(!showChatbot)}
          title="Chat with AI Assistant"
        >
          🤖 AI Assistant
          {showChatbot && <span className={styles.activeDot}></span>}
        </button>
        
        <button 
          className={styles.supportButton}
          onClick={() => setShowHumanSupport(!showHumanSupport)}
          title="Contact Human Support"
        >
          👤 Human Support
          {showHumanSupport && <span className={styles.activeDot}></span>}
        </button>

        <a 
          href={`tel:${SUPPORT_PHONE}`}
          className={styles.phoneButton}
          title="Call Support"
        >
          📞 {SUPPORT_PHONE}
        </a>
      </div>

      {/* AI Chatbot Panel */}
      {showChatbot && (
        <div className={styles.chatbotPanel}>
          <div className={styles.chatHeader}>
            <h3>🤖 AI Assistant</h3>
            <button 
              onClick={() => setShowChatbot(false)}
              className={styles.closeButton}
            >
              ✕
            </button>
          </div>
          
          <div className={styles.chatMessages}>
            {chatMessages.map((msg, index) => (
              <div 
                key={index}
                className={msg.type === 'user' ? styles.userMessage : styles.botMessage}
              >
                <div className={styles.messageContent}>
                  {msg.message}
                </div>
                <div className={styles.messageTime}>
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className={styles.botMessage}>
                <div className={styles.messageContent}>
                  <span className={styles.typing}>AI is typing...</span>
                </div>
              </div>
            )}
          </div>

          <div className={styles.chatInput}>
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={handleChatKeyPress}
              placeholder="Ask anything about filing complaints..."
              className={styles.chatInputField}
              disabled={chatLoading}
            />
            <button
              onClick={sendChatMessage}
              disabled={chatLoading || !chatInput.trim()}
              className={styles.chatSendButton}
            >
              📤
            </button>
          </div>
        </div>
      )}

      {/* Human Support Panel */}
      {showHumanSupport && (
        <div className={styles.humanSupportPanel}>
          <div className={styles.chatHeader}>
            <h3>👤 Human Support</h3>
            <button 
              onClick={() => setShowHumanSupport(false)}
              className={styles.closeButton}
            >
              ✕
            </button>
          </div>
          
          <div className={styles.supportContent}>
            <div className={styles.supportIcon}>📞</div>
            <h4>Need Human Assistance?</h4>
            <p>Our support team is ready to help you!</p>
            
            <div className={styles.contactInfo}>
              <div className={styles.contactMethod}>
                <strong>📞 Phone Support</strong>
                <a href={`tel:${SUPPORT_PHONE}`} className={styles.phoneLink}>
                  {SUPPORT_PHONE}
                </a>
                <button 
                  onClick={() => window.location.href = `tel:${SUPPORT_PHONE}`}
                  className={styles.callButton}
                >
                  📱 Call Now
                </button>
              </div>

              <div className={styles.supportHours}>
                <strong>⏰ Available Hours</strong>
                <p>Monday - Friday: 9:00 AM - 6:00 PM</p>
                <p>Saturday: 10:00 AM - 4:00 PM</p>
                <p>Sunday: Closed</p>
              </div>

              <div className={styles.supportNote}>
                <p><strong>💡 Tip:</strong> Have your complaint details ready when calling for faster assistance.</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <h2 className={styles.header}>
        🎥 Submit Multimodal Complaint
      </h2>
      
      <p className={styles.description}>
        Submit your complaint using text, images, or audio. AI will process your submission automatically.
      </p>

      {success && result && (
        <div className={styles.successAlert}>
          <h3>✅ Complaint Submitted Successfully!</h3>
          <p><strong>Complaint ID:</strong> {result.complaint?.id}</p>
          <p><strong>Status:</strong> {result.complaint?.status}</p>
          <p><strong>Tracking Number:</strong> COMP-{String(result.complaint?.id).padStart(6, '0')}</p>
          
          {result.processing_status && (
            <div className={styles.processingStatus}>
              <p><strong>Processing Status:</strong></p>
              <ul>
                {result.processing_status.image_processed && <li>✅ Image processed with OCR</li>}
                {result.processing_status.audio_processed && <li>✅ Audio transcribed</li>}
                {result.processing_status.ai_classified && <li>✅ Auto-classified by AI</li>}
              </ul>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className={styles.errorAlert}>
          <strong>❌ Error:</strong> {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Title */}
        <div className={styles.formGroup}>
          <label htmlFor="title" className={styles.label}>
            Complaint Title *
          </label>
          <input
            id="title"
            type="text"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            required
            placeholder="Brief title for your complaint"
            className={styles.input}
            title="Enter a brief title for your complaint"
          />
        </div>

        {/* Description */}
        <div className={styles.formGroup}>
          <label htmlFor="description" className={styles.label}>
            Description (optional if uploading media)
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            rows={4}
            placeholder="Describe your complaint in detail..."
            className={styles.textarea}
            title="Describe your complaint in detail"
          />
        </div>

        {/* Media Upload Section */}
        <div className={styles.mediaSection}>
          <h3 className={styles.sectionTitle}>📎 Upload Media (Optional)</h3>
          
          {/* Image Upload */}
          <div className={styles.fileInputWrapper}>
            <label htmlFor="imageUpload" className={styles.fileInputLabel}>
              📷 Image Evidence
            </label>
            {!previews.image ? (
              <input
                id="imageUpload"
                type="file"
                accept="image/*"
                onChange={(e) => handleFileChange(e, 'image')}
                className={styles.fileInput}
                title="Upload an image as evidence"
              />
            ) : (
              <div className={styles.previewContainer}>
                <img src={previews.image} alt="Complaint evidence preview" className={styles.previewImage} />
                <button
                  type="button"
                  onClick={() => removeFile('image')}
                  className={styles.removeButton}
                >
                  Remove
                </button>
              </div>
            )}
          </div>

          {/* Audio Upload */}
          <div className={styles.fileInputWrapper}>
            <label htmlFor="audioUpload" className={styles.fileInputLabel}>
              🎤 Audio Recording
            </label>
            {!previews.audio ? (
              <input
                id="audioUpload"
                type="file"
                accept="audio/*"
                onChange={(e) => handleFileChange(e, 'audio')}
                className={styles.fileInput}
                title="Upload an audio recording"
              />
            ) : (
              <div className={styles.previewContainer}>
                <audio controls src={previews.audio} className={styles.previewAudio} />
                <button
                  type="button"
                  onClick={() => removeFile('audio')}
                  className={styles.removeButton}
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Priority & Urgency */}
        <div className={styles.gridRow}>
          <div className={styles.formGroup}>
            <label htmlFor="priority" className={styles.label}>
              Priority
            </label>
            <select
              id="priority"
              name="priority"
              value={formData.priority}
              onChange={handleInputChange}
              className={styles.select}
              title="Select complaint priority"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="urgency_level" className={styles.label}>
              Urgency Level
            </label>
            <select
              id="urgency_level"
              name="urgency_level"
              value={formData.urgency_level}
              onChange={handleInputChange}
              className={styles.select}
              title="Select urgency level"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        {/* Location */}
        <div className={styles.formGroup}>
          <label htmlFor="incident_address" className={styles.label}>
            📍 Incident Address
          </label>
          <input
            id="incident_address"
            type="text"
            name="incident_address"
            value={formData.incident_address}
            onChange={handleInputChange}
            placeholder="Enter incident address or location"
            className={styles.input}
            title="Enter the location where the incident occurred"
          />
          <button
            type="button"
            onClick={getLocation}
            className={styles.actionButton}
          >
            📍 Get My Current Location
          </button>
          {formData.incident_latitude && formData.incident_longitude && (
            <p className={styles.infoText}>
              📍 Location captured: {formData.incident_latitude.toFixed(6)}, {formData.incident_longitude.toFixed(6)}
            </p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className={styles.submitButton}
        >
          {loading ? '⏳ Processing...' : '📤 Submit Complaint'}
        </button>
      </form>

      <div className={styles.infoBox}>
        <p className={styles.infoBoxText}>
          <strong>💡 Note:</strong> AI will automatically analyze your uploaded media to extract text, detect objects, and classify your complaint to the appropriate department.
        </p>
      </div>
    </div>
  );
};

export default MultimodalComplaintSubmit;
