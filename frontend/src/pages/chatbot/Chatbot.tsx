import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
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
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  ClearOutlined,
  DownloadOutlined,
  SoundOutlined,
} from '@ant-design/icons';
import { API_URLS } from '@/config/api.config';

const { Title, Text } = Typography;
const { TextArea } = Input;
import './chatbot.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'text' | 'quick-reply' | 'suggestion';
  suggestions?: string[];
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      text: "Hi! I'm your SmartGriev AI assistant powered by Google Gemini. I can help you file complaints in your language. How can I help you today?",
      sender: 'bot',
      timestamp: new Date(),
      type: 'text',
      suggestions: [
        'File a complaint',
        'Track complaint',
        'मुझे मदद चाहिए',
        'મને મદદ જોઈએ છે',
      ],
    },
  ]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [language, setLanguage] = useState<string>('en');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
      // Call real Gemini API
      const response = await axios.post(API_URLS.CHATBOT_CHAT(), {
        message: text.trim(),
        session_id: sessionId || undefined,
        language: language,
      });

      if (response.data) {
        // Save session ID for context
        if (response.data.session_id && !sessionId) {
          setSessionId(response.data.session_id);
        }

        const botResponse: Message = {
          id: (Date.now() + 1).toString(),
          text: response.data.response || 'Sorry, I could not understand that.',
          sender: 'bot',
          timestamp: new Date(),
          type: 'text',
          suggestions: response.data.complaint_data?.category ? [
            'Yes, submit this complaint',
            'No, let me change details',
            'Start over',
          ] : [
            'Tell me more',
            'Change language',
            'Talk to human agent',
          ],
        };

        setMessages(prev => [...prev, botResponse]);
      }
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I am having trouble connecting. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        type: 'text',
      };
      setMessages(prev => [...prev, errorMessage]);
      antMessage.error('Failed to get response from AI assistant');
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  const clearChat = () => {
    setMessages([messages[0]]); // Keep only the welcome message
    setSessionId(''); // Reset session
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
    <div className="chat-page">
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card
            title={
              <Space>
                <RobotOutlined style={{ color: '#FF6600' }} />
                <span>AI Assistant</span>
                <Tag color="green">Online</Tag>
              </Space>
            }
            extra={
              <span className="export-clear-space">
                <Tooltip title="Clear Chat">
                  <Button icon={<ClearOutlined />} onClick={clearChat} />
                </Tooltip>
                <Tooltip title="Export Chat">
                  <Button icon={<DownloadOutlined />} onClick={exportChat} />
                </Tooltip>
              </span>
            }
            className="chat-card"
            bodyStyle={{ padding: 0 }}
          >
            <div className="chat-messages">
              <List
                dataSource={messages}
                renderItem={(message) => (
                  <List.Item className="chat-list-item">
                    <div className={`message-row ${message.sender}`}>
                      <div className={`message-content ${message.sender}`}>
                        <Avatar
                          icon={message.sender === 'user' ? <UserOutlined /> : <RobotOutlined />}
                          className={`avatar ${message.sender}`}
                        />
                        <div>
                          <div className={`bubble ${message.sender}`}>{message.text}</div>
                          <Text className="timestamp">{message.timestamp.toLocaleTimeString()}</Text>
                          {message.suggestions && (
                            <div className="suggestions">
                              <Space wrap>
                                {message.id === 'welcome' && !showSuggestions ? (
                                  <Button size="small" onClick={() => setShowSuggestions(true)}>
                                    Start here
                                  </Button>
                                ) : (
                                  message.suggestions.map((suggestion, index) => (
                                    <Button key={index} size="small" onClick={() => handleSuggestionClick(suggestion)}>
                                      {suggestion}
                                    </Button>
                                  ))
                                )}
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
                <div className="typing-indicator">
                  <Avatar icon={<RobotOutlined />} className="avatar bot" />
                  <div className="bubble bot"> <Text style={{ color: 'inherit' }}>AI is typing...</Text> </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="chat-input-area">
              <Input.Group compact>
                <TextArea
                  className="chat-textarea"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Type your message here..."
                  autoSize={{ minRows: 1, maxRows: 4 }}
                  onPressEnter={(e) => {
                    if (!e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage(inputText);
                    }
                  }}
                />
                <Button type="primary" icon={<SendOutlined />} onClick={() => handleSendMessage(inputText)} disabled={!inputText.trim() || isTyping} />
              </Input.Group>
              <Text type="secondary" style={{ fontSize: '12px', marginTop: '8px', display: 'block' }}>
                Press Enter to send, Shift+Enter for new line
              </Text>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Chatbot;
