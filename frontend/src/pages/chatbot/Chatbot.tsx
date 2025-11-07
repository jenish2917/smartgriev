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
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  ClearOutlined,
  DownloadOutlined,
  SoundOutlined,
} from '@ant-design/icons';

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
      text: "Hi — I'm your SmartGriev AI assistant. I can help you file complaints, check status, or answer questions. Ready to start?",
      sender: 'bot',
      timestamp: new Date(),
      type: 'text',
      suggestions: [
        'File a complaint',
        'Track complaint',
        'What documents do I need?',
      ],
    },
  ]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
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

    // Simulate bot response
    setTimeout(() => {
      const botResponse = generateBotResponse(text);
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 800 + Math.random() * 1200);
  };

  const generateBotResponse = (userText: string): Message => {
    const text = userText.toLowerCase();
    let response = '';
    let suggestions: string[] = [];

    if (text.includes('file') || text.includes('complaint') || text.includes('lodge')) {
      response = 'To file a complaint:\n\n1. Click on "Lodge Complaint" in the main menu\n2. Fill in the complaint details\n3. Select the appropriate category\n4. Upload any supporting documents\n5. Submit your complaint\n\nYou\'ll receive a complaint ID for tracking. Would you like me to guide you through any specific step?';
      suggestions = ['Guide me through filing', 'What documents do I need?', 'How to choose category?'];
    } else if (text.includes('status') || text.includes('track') || text.includes('check')) {
      response = 'To check your complaint status:\n\n1. Go to "Track Complaint" in the menu\n2. Enter your complaint ID\n3. View real-time status updates\n\nComplaint statuses:\n• Pending - Under review\n• In Progress - Being addressed\n• Resolved - Completed\n• Rejected - Not actionable\n\nDo you have a complaint ID you\'d like me to help you track?';
      suggestions = ['I have a complaint ID', 'Why was my complaint rejected?', 'How to contact officer?'];
    } else if (text.includes('category') || text.includes('categories') || text.includes('type')) {
      response = 'Available complaint categories:\n\n🚰 Water Supply - Issues with water availability, quality\n🛣️ Road Maintenance - Potholes, traffic signals\n⚡ Electricity - Power outages, billing issues\n🗑️ Waste Management - Garbage collection, cleanliness\n🏥 Public Health - Sanitation, healthcare facilities\n🏗️ Infrastructure - Public buildings, parks\n👮 Law & Order - Safety, security concerns\n\nWhich category best describes your issue?';
      suggestions = ['Water Supply issue', 'Road problem', 'Electricity complaint', 'Other category'];
    } else if (text.includes('time') || text.includes('long') || text.includes('resolution')) {
      response = 'Typical resolution times by category:\n\n⚡ Electricity: 2-3 days\n🚰 Water Supply: 3-5 days\n🗑️ Waste Management: 1-2 days\n🛣️ Road Maintenance: 7-14 days\n🏥 Public Health: 5-10 days\n\nActual times may vary based on complexity and resource availability. You can track progress in real-time through your complaint dashboard.';
      suggestions = ['Why is my complaint delayed?', 'How to escalate?', 'Check complaint progress'];
    } else if (text.includes('help') || text.includes('support')) {
      response = 'I can help you with:\n\n✅ Filing new complaints\n✅ Tracking complaint status\n✅ Understanding the process\n✅ Choosing right category\n✅ Document requirements\n✅ Escalation procedures\n✅ Contact information\n\nWhat specific assistance do you need?';
      suggestions = ['File a complaint', 'Track existing complaint', 'Contact support', 'Learn about process'];
    } else {
      response = 'I understand you need assistance. Let me help you with common tasks:\n\n• Filing a new complaint\n• Tracking existing complaints\n• Understanding categories\n• Getting resolution timeframes\n\nCould you please clarify what you\'d like help with?';
      suggestions = ['File new complaint', 'Track complaint', 'Get help', 'Talk to human agent'];
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
