import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Typography,
  Space,
  Button,
  Badge,
  Tag,
  Row,
  Col,
  Statistic,
  Tabs,
  Switch,
  Select,
  Modal,
  Form,
  Input,
  DatePicker,
  Alert,
  Divider,
} from 'antd';
import {
  BellOutlined,
  MailOutlined,
  MobileOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import type { TabsProps } from 'antd';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  category: 'complaint' | 'system' | 'reminder' | 'announcement';
  is_read: boolean;
  created_at: string;
  scheduled_at?: string;
  metadata?: Record<string, any>;
}

interface NotificationPreference {
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  complaint_updates: boolean;
  system_alerts: boolean;
  reminders: boolean;
  announcements: boolean;
}

const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [preferences, setPreferences] = useState<NotificationPreference>({
    email_enabled: true,
    sms_enabled: false,
    push_enabled: true,
    complaint_updates: true,
    system_alerts: true,
    reminders: true,
    announcements: false,
  });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);

  // Mock notifications
  const mockNotifications: Notification[] = [
    {
      id: 'notif-001',
      title: 'Complaint Status Updated',
      message: 'Your complaint CMP-2024-001 has been marked as "In Progress". The assigned officer will contact you soon.',
      type: 'info',
      category: 'complaint',
      is_read: false,
      created_at: '2024-01-16T10:30:00Z',
      metadata: { complaint_id: 'CMP-2024-001' },
    },
    {
      id: 'notif-002',
      title: 'Complaint Resolved',
      message: 'Great news! Your complaint about street lighting has been successfully resolved.',
      type: 'success',
      category: 'complaint',
      is_read: false,
      created_at: '2024-01-16T09:15:00Z',
      metadata: { complaint_id: 'CMP-2024-002' },
    },
    {
      id: 'notif-003',
      title: 'System Maintenance',
      message: 'Scheduled maintenance will occur tonight from 2:00 AM to 4:00 AM. Services may be temporarily unavailable.',
      type: 'warning',
      category: 'system',
      is_read: true,
      created_at: '2024-01-15T14:00:00Z',
      scheduled_at: '2024-01-16T02:00:00Z',
    },
    {
      id: 'notif-004',
      title: 'New Feature Available',
      message: 'AI-powered complaint categorization is now available. Experience faster processing!',
      type: 'info',
      category: 'announcement',
      is_read: true,
      created_at: '2024-01-15T10:00:00Z',
    },
    {
      id: 'notif-005',
      title: 'Action Required',
      message: 'Please provide additional information for your complaint CMP-2024-003 to expedite processing.',
      type: 'warning',
      category: 'reminder',
      is_read: false,
      created_at: '2024-01-14T16:45:00Z',
      metadata: { complaint_id: 'CMP-2024-003' },
    },
  ];

  useEffect(() => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setNotifications(mockNotifications);
      setLoading(false);
    }, 1000);
  }, []);

  const getNotificationIcon = (type: string, category: string) => {
    const iconProps = { style: { fontSize: 16 } };
    
    if (category === 'complaint') return <BellOutlined {...iconProps} />;
    if (category === 'system') return <SettingOutlined {...iconProps} />;
    if (category === 'reminder') return <ExclamationCircleOutlined {...iconProps} />;
    if (category === 'announcement') return <InfoCircleOutlined {...iconProps} />;
    
    switch (type) {
      case 'success': return <CheckCircleOutlined {...iconProps} />;
      case 'warning': return <WarningOutlined {...iconProps} />;
      case 'error': return <ExclamationCircleOutlined {...iconProps} />;
      default: return <InfoCircleOutlined {...iconProps} />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'success': return 'green';
      case 'warning': return 'orange';
      case 'error': return 'red';
      default: return 'blue';
    }
  };

  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(notif =>
        notif.id === id ? { ...notif, is_read: true } : notif
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notif => ({ ...notif, is_read: true }))
    );
  };

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const viewNotification = (notification: Notification) => {
    setSelectedNotification(notification);
    setIsModalVisible(true);
    if (!notification.is_read) {
      markAsRead(notification.id);
    }
  };

  const filteredNotifications = notifications.filter(notif => {
    if (activeTab === 'all') return true;
    if (activeTab === 'unread') return !notif.is_read;
    return notif.category === activeTab;
  });

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const tabItems: TabsProps['items'] = [
    {
      key: 'all',
      label: `All (${notifications.length})`,
    },
    {
      key: 'unread',
      label: (
        <Badge count={unreadCount} size="small">
          <span>Unread</span>
        </Badge>
      ),
    },
    {
      key: 'complaint',
      label: 'Complaints',
    },
    {
      key: 'system',
      label: 'System',
    },
    {
      key: 'reminder',
      label: 'Reminders',
    },
    {
      key: 'announcement',
      label: 'Announcements',
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={2} className="gov-title">
          Notifications Center
        </Title>
        <Text className="gov-subtitle">
          Stay updated with your complaints and system announcements
        </Text>
      </div>

      {/* Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Total Notifications"
              value={notifications.length}
              prefix={<BellOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Unread"
              value={unreadCount}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="Complaint Updates"
              value={notifications.filter(n => n.category === 'complaint').length}
              prefix={<BellOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="System Alerts"
              value={notifications.filter(n => n.category === 'system').length}
              prefix={<SettingOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Notifications List */}
        <Col xs={24} lg={16}>
          <Card
            title="Notifications"
            extra={
              <Space>
                <Button onClick={markAllAsRead} disabled={unreadCount === 0}>
                  Mark All Read
                </Button>
                <Select defaultValue="newest" style={{ width: 120 }}>
                  <Select.Option value="newest">Newest First</Select.Option>
                  <Select.Option value="oldest">Oldest First</Select.Option>
                  <Select.Option value="unread">Unread First</Select.Option>
                </Select>
              </Space>
            }
          >
            <Tabs
              activeKey={activeTab}
              onChange={setActiveTab}
              items={tabItems}
              style={{ marginBottom: 16 }}
            />

            <List
              loading={loading}
              dataSource={filteredNotifications}
              renderItem={(notification) => (
                <List.Item
                  style={{
                    backgroundColor: notification.is_read ? '#FFFFFF' : '#F6FFED',
                    border: notification.is_read ? '1px solid #F0F0F0' : '1px solid #B7EB8F',
                    borderRadius: 8,
                    marginBottom: 8,
                    padding: 16,
                  }}
                  actions={[
                    <Button
                      type="text"
                      icon={<EyeOutlined />}
                      onClick={() => viewNotification(notification)}
                    >
                      View
                    </Button>,
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => deleteNotification(notification.id)}
                    >
                      Delete
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      <div style={{ position: 'relative' }}>
                        {getNotificationIcon(notification.type, notification.category)}
                        {!notification.is_read && (
                          <Badge
                            dot
                            style={{
                              position: 'absolute',
                              top: -4,
                              right: -4,
                            }}
                          />
                        )}
                      </div>
                    }
                    title={
                      <Space>
                        <Text strong={!notification.is_read}>
                          {notification.title}
                        </Text>
                        <Tag color={getNotificationColor(notification.type)}>
                          {notification.type.toUpperCase()}
                        </Tag>
                        <Tag>{notification.category.toUpperCase()}</Tag>
                      </Space>
                    }
                    description={
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Text>{notification.message}</Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {new Date(notification.created_at).toLocaleString()}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* Notification Preferences */}
        <Col xs={24} lg={8}>
          <Card title="Notification Preferences">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Alert
                message="Customize Your Notifications"
                description="Control how and when you receive notifications"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />

              <div>
                <Text strong>Delivery Methods</Text>
                <Divider style={{ margin: '8px 0' }} />
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Space>
                        <MailOutlined />
                        <Text>Email Notifications</Text>
                      </Space>
                    </Col>
                    <Col>
                      <Switch
                        checked={preferences.email_enabled}
                        onChange={(checked) =>
                          setPreferences(prev => ({ ...prev, email_enabled: checked }))
                        }
                      />
                    </Col>
                  </Row>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Space>
                        <MobileOutlined />
                        <Text>SMS Notifications</Text>
                      </Space>
                    </Col>
                    <Col>
                      <Switch
                        checked={preferences.sms_enabled}
                        onChange={(checked) =>
                          setPreferences(prev => ({ ...prev, sms_enabled: checked }))
                        }
                      />
                    </Col>
                  </Row>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Space>
                        <BellOutlined />
                        <Text>Push Notifications</Text>
                      </Space>
                    </Col>
                    <Col>
                      <Switch
                        checked={preferences.push_enabled}
                        onChange={(checked) =>
                          setPreferences(prev => ({ ...prev, push_enabled: checked }))
                        }
                      />
                    </Col>
                  </Row>
                </Space>
              </div>

              <div>
                <Text strong>Notification Types</Text>
                <Divider style={{ margin: '8px 0' }} />
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Text>Complaint Updates</Text>
                    </Col>
                    <Col>
                      <Switch
                        checked={preferences.complaint_updates}
                        onChange={(checked) =>
                          setPreferences(prev => ({ ...prev, complaint_updates: checked }))
                        }
                      />
                    </Col>
                  </Row>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Text>System Alerts</Text>
                    </Col>
                    <Col>
                      <Switch
                        checked={preferences.system_alerts}
                        onChange={(checked) =>
                          setPreferences(prev => ({ ...prev, system_alerts: checked }))
                        }
                      />
                    </Col>
                  </Row>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Text>Reminders</Text>
                    </Col>
                    <Col>
                      <Switch
                        checked={preferences.reminders}
                        onChange={(checked) =>
                          setPreferences(prev => ({ ...prev, reminders: checked }))
                        }
                      />
                    </Col>
                  </Row>
                  <Row justify="space-between" align="middle">
                    <Col>
                      <Text>Announcements</Text>
                    </Col>
                    <Col>
                      <Switch
                        checked={preferences.announcements}
                        onChange={(checked) =>
                          setPreferences(prev => ({ ...prev, announcements: checked }))
                        }
                      />
                    </Col>
                  </Row>
                </Space>
              </div>

              <Button type="primary" block style={{ marginTop: 16 }}>
                Save Preferences
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Notification Detail Modal */}
      <Modal
        title={selectedNotification?.title}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setIsModalVisible(false)}>
            Close
          </Button>,
        ]}
        width={600}
      >
        {selectedNotification && (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              <Tag color={getNotificationColor(selectedNotification.type)}>
                {selectedNotification.type.toUpperCase()}
              </Tag>
              <Tag>{selectedNotification.category.toUpperCase()}</Tag>
              {selectedNotification.is_read ? (
                <Tag color="green">READ</Tag>
              ) : (
                <Tag color="orange">UNREAD</Tag>
              )}
            </Space>
            
            <Text>{selectedNotification.message}</Text>
            
            <Divider />
            
            <Row>
              <Col span={12}>
                <Text strong>Created:</Text><br />
                <Text>{new Date(selectedNotification.created_at).toLocaleString()}</Text>
              </Col>
              {selectedNotification.scheduled_at && (
                <Col span={12}>
                  <Text strong>Scheduled:</Text><br />
                  <Text>{new Date(selectedNotification.scheduled_at).toLocaleString()}</Text>
                </Col>
              )}
            </Row>
            
            {selectedNotification.metadata && (
              <>
                <Divider />
                <Text strong>Additional Information:</Text>
                <pre style={{ fontSize: 12, background: '#f5f5f5', padding: 8 }}>
                  {JSON.stringify(selectedNotification.metadata, null, 2)}
                </pre>
              </>
            )}
          </Space>
        )}
      </Modal>
    </div>
  );
};

export default Notifications;
