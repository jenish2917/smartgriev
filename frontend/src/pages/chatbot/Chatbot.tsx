import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Input,
  Button,
  List,
  Avatar,
  Typography,
  Space,
  Tag,
  Divider,
  Row,
  Col,
  Tooltip,
  message as antMessage,
  Modal,
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  ClearOutlined,
  DownloadOutlined,
  SoundOutlined,
  AudioOutlined,
  FileAddOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import styles from './Chatbot.module.css';

const { Title, Text } = Typography;
const { TextArea } = Input;

// Dynamic API URL for network access
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000/api'
  : `http://${window.location.hostname}:8000/api`;

// Indian Government Theme Colors - Blue and White Only
const THEME_COLORS = {
  primary: '#2196F3',      // Government Blue
  darkBlue: '#1565C0',     // Dark Blue for contrast
  lightBlue: '#E3F2FD',    // Light Blue for backgrounds
  white: '#FFFFFF',        // Pure White
  lightGray: '#F5F5F5',    // Very light gray (almost white)
};

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'text' | 'quick-reply' | 'suggestion';
  suggestions?: string[];
}

const Chatbot: React.FC = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'नमस्ते! Hello! I\'m your AI assistant for SmartGriev. I can help you with:\n\n📝 Filing complaints\n🔍 Checking status\n❓ Answering questions\n🎤 Voice commands\n\nHow can I assist you today?',
      sender: 'bot',
      timestamp: new Date(),
      type: 'text',
      suggestions: [
        'File a new complaint',
        'Check complaint status',
        'What are the complaint categories?',
        'How long does resolution take?',
      ],
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [complaintData, setComplaintData] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize chat session
  useEffect(() => {
    initializeSession();
    initializeVoiceRecognition();
  }, []);

  // Initialize voice recognition
  const initializeVoiceRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US'; // Can be changed to 'hi-IN' for Hindi

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsListening(false);
        antMessage.success('Voice recognized: ' + transcript);
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        antMessage.error('Voice recognition failed. Please try again.');
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  };

  const startVoiceRecognition = () => {
    if (recognitionRef.current) {
      setIsListening(true);
      recognitionRef.current.start();
      antMessage.info('🎤 Listening... Speak now');
    } else {
      antMessage.error('Voice recognition not supported in this browser');
    }
  };

  const stopVoiceRecognition = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const initializeSession = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.log('No token found, using local chat');
        return;
      }

      const response = await axios.post(
        `${API_BASE_URL}/chatbot/session/`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      setSessionId(response.data.session_id);
    } catch (error) {
      console.error('Error initializing session:', error);
      antMessage.info('Using local chat mode');
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      const token = localStorage.getItem('token');
      
      if (token && sessionId) {
        // Use backend API
        const response = await axios.post(
          `${API_BASE_URL}/chatbot/message/`,
          {
            message: text.trim(),
            session_id: sessionId,
            preferred_language: 'en',
          },
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        const botResponse: Message = {
          id: response.data.id || Date.now().toString(),
          text: response.data.reply,
          sender: 'bot',
          timestamp: new Date(response.data.timestamp),
          type: response.data.reply_type || 'text',
          suggestions: response.data.quick_replies || [],
        };

        setMessages(prev => [...prev, botResponse]);
        setIsTyping(false);
      } else {
        // Fallback to local responses
        setTimeout(() => {
          const botResponse = generateBotResponse(text);
          setMessages(prev => [...prev, botResponse]);
          setIsTyping(false);
        }, 1000 + Math.random() * 2000);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Fallback to local response on error
      setTimeout(() => {
        const botResponse = generateBotResponse(text);
        setMessages(prev => [...prev, botResponse]);
        setIsTyping(false);
      }, 1000);
    }
  };

  const generateBotResponse = (userText: string): Message => {
    const text = userText.toLowerCase();
    let response = '';
    let suggestions: string[] = [];
    let shouldNavigate = false;
    let navigationPath = '';

    // Check if user wants to file a complaint
    if (text.includes('file') || text.includes('lodge') || text.includes('submit') || text.includes('new complaint') || text.includes('report')) {
      response = '📝 I\'ll help you file a complaint!\n\nI\'m redirecting you to the complaint submission page where you can:\n\n✅ Describe your issue\n✅ Upload supporting images\n✅ Add audio description\n✅ Specify location\n✅ Select priority\n\nRedirecting in 3 seconds...';
      suggestions = [];
      shouldNavigate = true;
      navigationPath = '/multimodal-submit';
      
      // Navigate after showing message
      setTimeout(() => {
        navigate(navigationPath);
        antMessage.success('Navigating to complaint submission page...');
      }, 3000);
    } 
    // Check complaint status
    else if (text.includes('status') || text.includes('track') || text.includes('check')) {
      response = '🔍 To check your complaint status:\n\n1. Go to "My Complaints" section\n2. Enter your complaint ID\n3. View real-time status updates\n\nComplaint statuses:\n• Pending - Under review\n• In Progress - Being addressed\n• Resolved - Completed\n• Rejected - Not actionable\n\nWould you like me to take you there?';
      suggestions = ['Yes, show my complaints', 'No, I have questions', 'How to track by ID?'];
    }
    // My complaints navigation
    else if (text.includes('my complaint') || text.includes('show my complaint')) {
      response = '📊 Taking you to your complaints dashboard...\n\nYou\'ll be able to see:\n• All your submitted complaints\n• Current status of each\n• Response from authorities\n• Expected resolution time\n\nRedirecting now...';
      shouldNavigate = true;
      navigationPath = '/my-complaints';
      setTimeout(() => {
        navigate(navigationPath);
      }, 2000);
    }
    // Categories
    else if (text.includes('category') || text.includes('categories') || text.includes('type')) {
      response = '📋 Available complaint categories:\n\n🚰 Water Supply - Water availability, quality issues\n🛣️ Road Maintenance - Potholes, traffic signals, road damage\n⚡ Electricity - Power outages, billing issues\n🗑️ Waste Management - Garbage collection, cleanliness\n🏥 Public Health - Sanitation, healthcare facilities\n🏗️ Infrastructure - Public buildings, parks, monuments\n👮 Law & Order - Safety, security concerns\n🌳 Environment - Tree cutting, pollution\n\nWhich category does your complaint fall under?';
      suggestions = ['Water Supply issue', 'Road problem', 'Waste/Garbage', 'File complaint now'];
    }
    // Resolution time
    else if (text.includes('time') || text.includes('long') || text.includes('resolution') || text.includes('how many days')) {
      response = '⏱️ Typical resolution times by category:\n\n⚡ Electricity: 2-3 days\n🚰 Water Supply: 3-5 days\n🗑️ Waste Management: 1-2 days\n🛣️ Road Maintenance: 7-14 days\n🏥 Public Health: 5-10 days\n🏗️ Infrastructure: 10-21 days\n\n⚠️ Note: Urgent complaints are prioritized and resolved faster.\n\nActual times may vary based on complexity. You can track real-time progress through your complaint dashboard.';
      suggestions = ['File urgent complaint', 'Check my complaints', 'What makes it urgent?'];
    }
    // Voice commands
    else if (text.includes('voice') || text.includes('speak') || text.includes('audio')) {
      response = '🎤 Voice Commands Available!\n\nYou can use the microphone button to:\n• Speak your complaint instead of typing\n• Search for information\n• Navigate the system\n\nSupported languages:\n• English\n• Hindi (हिंदी)\n• Regional languages\n\nClick the microphone icon 🎤 in the input box to start!';
      suggestions = ['Try voice now', 'File voice complaint', 'Help with voice'];
    }
    // Help
    else if (text.includes('help') || text.includes('support') || text.includes('assist')) {
      response = '💡 I can help you with:\n\n✅ Filing new complaints (text, voice, or images)\n✅ Tracking complaint status\n✅ Understanding the process\n✅ Choosing the right category\n✅ Document requirements\n✅ Escalation procedures\n✅ Contact information\n✅ Voice-based interaction\n\nWhat would you like to do?';
      suggestions = ['File a complaint', 'Track complaint', 'Use voice', 'Contact support'];
    }
    // Default
    else {
      response = '🤔 I understand you need assistance. Let me help you with common tasks:\n\n• 📝 Filing a new complaint\n• 🔍 Tracking existing complaints\n• 📋 Understanding categories\n• ⏱️ Getting resolution timeframes\n• 🎤 Using voice commands\n\nCould you please clarify what you\'d like help with?';
      suggestions = ['File new complaint', 'Track complaint', 'Get help', 'Use voice'];
    }

    return {
      id: Date.now().toString(),
      text: response,
      sender: 'bot',
      timestamp: new Date(),
      type: 'text',
      suggestions,
    };
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  const clearChat = () => {
    setMessages([messages[0]]); // Keep only the welcome message
  };

  const exportChat = () => {
    const chatHistory = messages.map(msg => 
      `[${msg.timestamp.toLocaleTimeString()}] ${msg.sender.toUpperCase()}: ${msg.text}`
    ).join('\n\n');
    
    const blob = new Blob([chatHistory], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'smartgriev-chat-history.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={styles.chatContainer}>
      <Row className={styles.mainRow}>
        <Col xs={24} sm={24} md={18} lg={18} className={styles.chatColumn}>
          <Card
            title={
              <Space>
                <RobotOutlined className={styles.titleIcon} />
                <span className={styles.titleText}>
                  स्मार्टग्रीव AI सहायक | SmartGriev AI Assistant
                </span>
                <Tag color="blue">Online</Tag>
              </Space>
            }
            extra={
              <Space>
                <Tooltip title="Clear Chat">
                  <Button 
                    icon={<ClearOutlined />} 
                    onClick={clearChat}
                    className={styles.actionButton}
                  />
                </Tooltip>
                <Tooltip title="Export Chat">
                  <Button 
                    icon={<DownloadOutlined />} 
                    onClick={exportChat}
                    className={styles.actionButton}
                  />
                </Tooltip>
              </Space>
            }
            className={styles.chatCard}
            bodyStyle={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column',
              padding: 0,
              overflow: 'hidden',
            }}
            headStyle={{
              background: THEME_COLORS.primary,
              color: THEME_COLORS.white,
              borderRadius: '0',
              borderBottom: `2px solid ${THEME_COLORS.darkBlue}`,
            }}
          >
            <div className={styles.messagesContainer}>
              <List
                dataSource={messages}
                renderItem={(message) => (
                  <List.Item className={styles.messageItem}>
                    <div className={`${styles.messageWrapper} ${message.sender === 'user' ? styles.messageWrapperUser : styles.messageWrapperBot}`}>
                      <div className={`${styles.messageContent} ${message.sender === 'user' ? styles.messageContentUser : styles.messageContentBot}`}>
                        <Avatar
                          icon={message.sender === 'user' ? <UserOutlined /> : <RobotOutlined />}
                          className={`${styles.messageAvatar} ${message.sender === 'user' ? styles.messageAvatarUser : styles.messageAvatarBot}`}
                        />
                        <div>
                          <div className={`${styles.messageBubble} ${message.sender === 'user' ? styles.messageBubbleUser : styles.messageBubbleBot}`}>
                            {message.text}
                          </div>
                          <Text type="secondary" className={`${styles.messageTimestamp} ${message.sender === 'user' ? styles.messageTimestampUser : styles.messageTimestampBot}`}>
                            {message.timestamp.toLocaleTimeString()}
                          </Text>
                          {message.suggestions && (
                            <div className={styles.suggestionsContainer}>
                              <Space wrap>
                                {message.suggestions.map((suggestion, index) => (
                                  <Button
                                    key={index}
                                    size="small"
                                    onClick={() => handleSuggestionClick(suggestion)}
                                    className={styles.suggestionChip}
                                  >
                                    {suggestion}
                                  </Button>
                                ))}
                              </Space>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </List.Item>
                )}
              />
              {isTyping && (
                <div className={styles.typingIndicator}>
                  <Avatar 
                    icon={<RobotOutlined />} 
                    className={`${styles.messageAvatar} ${styles.messageAvatarBot}`}
                  />
                  <div className={styles.messageBubbleBot}>
                    <Text type="secondary">AI is typing...</Text>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            
            <Divider style={{ margin: 0, borderColor: THEME_COLORS.primary }} />
            
            <div className={styles.quickSuggestionsContainer}>
              <Space.Compact style={{ width: '100%' }}>
                <TextArea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="अपना संदेश यहाँ लिखें... | Type your message here..."
                  autoSize={{ minRows: 1, maxRows: 3 }}
                  onPressEnter={(e) => {
                    if (!e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage(inputText);
                    }
                  }}
                  style={{ 
                    resize: 'none',
                    borderColor: THEME_COLORS.primary,
                    flex: 1,
                  }}
                />
                <Button
                  icon={isListening ? <AudioOutlined /> : <SoundOutlined />}
                  onClick={isListening ? stopVoiceRecognition : startVoiceRecognition}
                  style={{
                    borderColor: THEME_COLORS.primary,
                    color: THEME_COLORS.white,
                    background: isListening ? THEME_COLORS.darkBlue : THEME_COLORS.primary,
                  }}
                  title={isListening ? "Stop Recording" : "Voice Input"}
                />
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={() => handleSendMessage(inputText)}
                  disabled={!inputText.trim() || isTyping}
                  style={{ 
                    background: THEME_COLORS.primary,
                    borderColor: THEME_COLORS.primary,
                  }}
                >
                  Send
                </Button>
              </Space.Compact>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={24} md={6} lg={6} style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'auto' }}>
          <Space direction="vertical" style={{ width: '100%', height: '100%', padding: '0' }}>
            <Card 
              title={<span className={styles.sectionTitleSpan}>त्वरित क्रियाएँ | Quick Actions</span>}
              size="small"
              style={{ 
                borderColor: THEME_COLORS.primary,
                borderRadius: '0',
                borderWidth: '2px',
              }}
              headStyle={{
                background: THEME_COLORS.primary,
                color: THEME_COLORS.white,
                borderRadius: '0',
              }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <Button 
                  block 
                  onClick={() => handleSendMessage('How do I file a complaint?')}
                  style={{
                    borderColor: THEME_COLORS.primary,
                    color: THEME_COLORS.primary,
                    fontWeight: 500,
                    background: THEME_COLORS.white,
                  }}
                >
                  📝 File a Complaint
                </Button>
                <Button 
                  block 
                  onClick={() => handleSendMessage('Check complaint status')}
                  style={{
                    borderColor: THEME_COLORS.primary,
                    color: THEME_COLORS.primary,
                    fontWeight: 500,
                    background: THEME_COLORS.white,
                  }}
                >
                  🔍 Track Complaint
                </Button>
                <Button 
                  block 
                  onClick={() => handleSendMessage('What are complaint categories?')}
                  style={{
                    borderColor: THEME_COLORS.primary,
                    color: THEME_COLORS.primary,
                    fontWeight: 500,
                    background: THEME_COLORS.white,
                  }}
                >
                  📋 View Categories
                </Button>
                <Button 
                  block 
                  onClick={() => handleSendMessage('Talk to human agent')}
                  style={{
                    borderColor: THEME_COLORS.primary,
                    color: THEME_COLORS.primary,
                    fontWeight: 500,
                    background: THEME_COLORS.white,
                  }}
                >
                  👤 Human Support
                </Button>
              </Space>
            </Card>
            
            <Card 
              title={<span className={styles.sectionTitleSpan}>सहायता विषय | Help Topics</span>}
              size="small"
              style={{ 
                borderColor: THEME_COLORS.primary,
                borderRadius: '0',
                borderWidth: '2px',
              }}
              headStyle={{
                background: THEME_COLORS.primary,
                color: THEME_COLORS.white,
                borderRadius: '0',
              }}
            >
              <List
                size="small"
                dataSource={[
                  'Filing Process',
                  'Required Documents',
                  'Status Meanings',
                  'Resolution Times',
                  'Escalation Process',
                  'Contact Information',
                ]}
                renderItem={(item) => (
                  <List.Item
                    style={{ 
                      padding: '8px 0', 
                      cursor: 'pointer',
                      borderBottom: '1px solid #f0f0f0',
                    }}
                    onClick={() => handleSendMessage(`Help with ${item}`)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = THEME_COLORS.lightBlue;
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <Text style={{ color: THEME_COLORS.primary }}>📌 {item}</Text>
                  </List.Item>
                )}
              />
            </Card>
          </Space>
        </Col>
      </Row>
    </div>
  );
};

export default Chatbot;
