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
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [isLiveCall, setIsLiveCall] = useState<boolean>(false);
  const [callLanguage, setCallLanguage] = useState<string>('en-IN');

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
    const currentInput = chatInput;
    setChatInput('');
    setChatLoading(true);

    try {
      // Send message with conversation history for context
      const response = await axios.post(API_URLS.CHATBOT_CHAT(), {
        message: currentInput,
        conversation_history: chatMessages.slice(-10).map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.message
        }))
      });

      // Check if we have a response
      if (response.data && response.data.response) {
        const botMessage: ChatMessage = {
          type: 'bot',
          message: response.data.response,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, botMessage]);
        
        // Automatically speak the AI's response (like a phone call)
        speakResponse(response.data.response);
      } else {
        throw new Error('No response from chatbot');
      }
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage: ChatMessage = {
        type: 'bot',
        message: 'Sorry, I encountered an error. Please try again.',
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

  // Voice Recognition - Listen to user's voice
  const startVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Voice recognition not supported in your browser. Please use Chrome or Edge.');
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    // Auto-detect language (supports multiple Indian languages)
    recognition.lang = 'hi-IN'; // Hindi as default, but will detect others

    setIsListening(true);

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setChatInput(transcript);
      setIsListening(false);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      alert('Voice input failed. Please try again.');
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  // Text-to-Speech - AI speaks the response
  const speakResponse = (text: string) => {
    if (!('speechSynthesis' in window)) {
      console.warn('Text-to-speech not supported');
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Auto-detect language from text
    if (/[\u0A80-\u0AFF]/.test(text)) {
      utterance.lang = 'gu-IN'; // Gujarati
    } else if (/[\u0900-\u097F]/.test(text)) {
      utterance.lang = 'hi-IN'; // Hindi
    } else if (/[\u0980-\u09FF]/.test(text)) {
      utterance.lang = 'mr-IN'; // Marathi
    } else if (/[\u0A00-\u0A7F]/.test(text)) {
      utterance.lang = 'pa-IN'; // Punjabi
    } else {
      utterance.lang = 'en-IN'; // English
    }

    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    setIsSpeaking(true);

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
  };

  // Stop speaking
  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  // Start Live Voice Call - AI speaks first and has continuous conversation
  const startLiveCall = async () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Voice recognition not supported in your browser. Please use Chrome or Edge.');
      return;
    }

    if (!('speechSynthesis' in window)) {
      alert('Text-to-speech not supported in your browser.');
      return;
    }

    setIsLiveCall(true);

    // AI greets user first (like answering a phone call)
    const greetings = {
      'en-IN': 'Hello! I am your AI assistant from SmartGriev. How can I help you today?',
      'hi-IN': 'नमस्ते! मैं SmartGriev से आपका AI सहायक हूं। आज मैं आपकी कैसे मदद कर सकता हूं?',
      'gu-IN': 'નમસ્તે! હું SmartGriev તરફથી તમારો AI સહાયક છું. આજે હું તમને કેવી રીતે મદદ કરી શકું?',
      'mr-IN': 'नमस्कार! मी SmartGriev कडून तुमचा AI सहाय्यक आहे. आज मी तुम्हाला कशी मदत करू शकतो?',
      'pa-IN': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ SmartGriev ਤੋਂ ਤੁਹਾਡਾ AI ਸਹਾਇਕ ਹਾਂ। ਅੱਜ ਮੈਂ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?'
    };

    const greeting = greetings[callLanguage as keyof typeof greetings] || greetings['en-IN'];

    // Add AI greeting to chat
    const greetingMessage: ChatMessage = {
      type: 'bot',
      message: greeting,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, greetingMessage]);

    // AI speaks the greeting
    const utterance = new SpeechSynthesisUtterance(greeting);
    utterance.lang = callLanguage;
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    setIsSpeaking(true);

    utterance.onend = () => {
      setIsSpeaking(false);
      // After AI finishes speaking, start listening to user
      setTimeout(() => {
        if (isLiveCall) {
          continueLiveConversation();
        }
      }, 500);
    };

    window.speechSynthesis.speak(utterance);
  };

  // Continue live conversation - listen and respond automatically
  const continueLiveConversation = () => {
    if (!isLiveCall) return;

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = callLanguage;

    setIsListening(true);

    recognition.onresult = async (event: any) => {
      const transcript = event.results[0][0].transcript;
      setIsListening(false);

      // Add user's speech to chat
      const userMessage: ChatMessage = {
        type: 'user',
        message: transcript,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, userMessage]);

      // Get AI response
      setChatLoading(true);
      try {
        const response = await axios.post(API_URLS.CHATBOT_CHAT(), {
          message: transcript,
          conversation_history: chatMessages.slice(-10).map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.message
          }))
        });

        if (response.data && response.data.response) {
          const botMessage: ChatMessage = {
            type: 'bot',
            message: response.data.response,
            timestamp: new Date()
          };
          setChatMessages(prev => [...prev, botMessage]);

          // AI speaks the response
          const utterance = new SpeechSynthesisUtterance(response.data.response);
          utterance.lang = callLanguage;
          utterance.rate = 0.9;
          utterance.pitch = 1.0;

          setIsSpeaking(true);
          setChatLoading(false);

          utterance.onend = () => {
            setIsSpeaking(false);
            // Continue listening for next input
            setTimeout(() => {
              if (isLiveCall) {
                continueLiveConversation();
              }
            }, 1000);
          };

          window.speechSynthesis.speak(utterance);
        }
      } catch (err) {
        console.error('Live call error:', err);
        setChatLoading(false);
        endLiveCall();
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      if (isLiveCall && event.error !== 'no-speech') {
        // Retry after error (except no-speech)
        setTimeout(() => {
          if (isLiveCall) {
            continueLiveConversation();
          }
        }, 1000);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  // End live call
  const endLiveCall = () => {
    setIsLiveCall(false);
    setIsListening(false);
    setIsSpeaking(false);
    window.speechSynthesis.cancel();
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

      {/* Support Options Bar - AI Only */}
      <div className={styles.supportBar}>
        <button 
          className={styles.supportButton}
          onClick={() => setShowChatbot(!showChatbot)}
          title="Chat with AI Assistant"
        >
          🤖 AI Assistant
          {showChatbot && <span className={styles.activeDot}></span>}
        </button>
      </div>

      {/* AI Chatbot Panel */}
      {showChatbot && (
        <div className={styles.chatbotPanel}>
          <div className={styles.chatHeader}>
            <h3>🤖 AI Assistant</h3>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              {!isLiveCall ? (
                <>
                  <select 
                    value={callLanguage}
                    onChange={(e) => setCallLanguage(e.target.value)}
                    style={{
                      padding: '5px 10px',
                      borderRadius: '5px',
                      border: '1px solid #ddd',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                    title="Select language for live call"
                  >
                    <option value="en-IN">🇬🇧 English</option>
                    <option value="hi-IN">🇮🇳 हिंदी</option>
                    <option value="gu-IN">🇮🇳 ગુજરાતી</option>
                    <option value="mr-IN">🇮🇳 मराठी</option>
                    <option value="pa-IN">🇮🇳 ਪੰਜਾਬੀ</option>
                  </select>
                  <button
                    onClick={startLiveCall}
                    disabled={isSpeaking || isListening}
                    style={{
                      background: '#00C853',
                      color: 'white',
                      border: 'none',
                      borderRadius: '20px',
                      padding: '8px 15px',
                      fontSize: '14px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px'
                    }}
                    title="Start live voice call with AI"
                  >
                    📞 Live Call
                  </button>
                </>
              ) : (
                <button
                  onClick={endLiveCall}
                  style={{
                    background: '#ff4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '20px',
                    padding: '8px 15px',
                    fontSize: '14px',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    animation: 'pulse 1.5s infinite'
                  }}
                  title="End live call"
                >
                  📞 End Call
                </button>
              )}
              <button 
                onClick={() => setShowChatbot(false)}
                className={styles.closeButton}
              >
                ✕
              </button>
            </div>
          </div>
          
          {isLiveCall && (
            <div style={{
              background: 'linear-gradient(90deg, #00C853, #00E676)',
              color: 'white',
              padding: '10px',
              textAlign: 'center',
              fontSize: '14px',
              fontWeight: 'bold',
              borderBottom: '2px solid #00C853'
            }}>
              📞 Live Call Active - {isListening ? '🎤 Listening...' : isSpeaking ? '🔊 AI Speaking...' : '⏸️ Ready'}
            </div>
          )}
          
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
            <button
              onClick={startVoiceInput}
              disabled={chatLoading || isListening}
              className={styles.voiceButton}
              title="Click to speak (Voice Input)"
              style={{
                background: isListening ? '#ff4444' : '#4CAF50',
                color: 'white',
                border: 'none',
                borderRadius: '50%',
                width: '45px',
                height: '45px',
                fontSize: '20px',
                cursor: chatLoading || isListening ? 'not-allowed' : 'pointer',
                marginRight: '8px',
                animation: isListening ? 'pulse 1s infinite' : 'none'
              }}
            >
              {isListening ? '🔴' : '🎤'}
            </button>
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={handleChatKeyPress}
              placeholder={isListening ? "Listening..." : "Type or speak your question..."}
              className={styles.chatInputField}
              disabled={chatLoading}
            />
            {isSpeaking && (
              <button
                onClick={stopSpeaking}
                className={styles.stopSpeakButton}
                title="Stop speaking"
                style={{
                  background: '#ff6b6b',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50%',
                  width: '45px',
                  height: '45px',
                  fontSize: '20px',
                  cursor: 'pointer',
                  marginLeft: '8px'
                }}
              >
                🔇
              </button>
            )}
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

      {/* Human Support Panel - REMOVED */}

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
