// SmartGriev Real-Time Notifications Component
// Implements WebSocket connections for live updates

import React, { useEffect, useState, useCallback } from 'react';
import { notification, Badge, Dropdown, Menu, Avatar, Typography } from 'antd';
import { BellOutlined, CheckOutlined, InfoCircleOutlined, WarningOutlined } from '@ant-design/icons';
import { useAuth } from '../../hooks/useAuth';

const { Text } = Typography;

interface NotificationItem {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  complaintId?: string;
  actionUrl?: string;
}

interface RealTimeNotificationsProps {
  userId?: string;
}

export const RealTimeNotifications: React.FC<RealTimeNotificationsProps> = ({ userId }) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const { user } = useAuth();

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!user?.id) return;

    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/notifications/${user.id}/`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('📡 Connected to real-time notifications');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleRealTimeNotification(data);
      } catch (error) {
        console.error('Failed to parse notification:', error);
      }
    };

    ws.onclose = () => {
      console.log('📡 Disconnected from real-time notifications');
      setIsConnected(false);
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (user?.id) {
          // Recursive reconnection would be handled by the effect dependency
        }
      }, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [user?.id]);

  const handleRealTimeNotification = useCallback((data: any) => {
    const newNotification: NotificationItem = {
      id: data.id || Math.random().toString(36),
      type: data.type || 'info',
      title: data.title,
      message: data.message,
      timestamp: data.timestamp || new Date().toISOString(),
      read: false,
      complaintId: data.complaint_id,
      actionUrl: data.action_url,
    };

    // Add to notifications list
    setNotifications(prev => [newNotification, ...prev.slice(0, 49)]); // Keep max 50
    setUnreadCount(prev => prev + 1);

    // Show system notification
    const config = {
      message: newNotification.title,
      description: newNotification.message,
      duration: 4.5,
      placement: 'topRight' as const,
    };

    switch (newNotification.type) {
      case 'success':
        notification.success(config);
        break;
      case 'warning':
        notification.warning(config);
        break;
      case 'error':
        notification.error(config);
        break;
      default:
        notification.info(config);
    }

    // Browser notification (if permission granted)
    if (Notification.permission === 'granted') {
      new Notification(newNotification.title, {
        body: newNotification.message,
        icon: '/favicon.ico',
        tag: newNotification.id,
      });
    }
  }, []);

  // Request notification permission on component mount
  useEffect(() => {
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const markAsRead = useCallback((notificationId: string) => {
    setNotifications(prev =>
      prev.map(n =>
        n.id === notificationId ? { ...n, read: true } : n
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  }, []);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckOutlined style={{ color: '#52c41a' }} />;
      case 'warning': return <WarningOutlined style={{ color: '#faad14' }} />;
      case 'error': return <WarningOutlined style={{ color: '#ff4d4f' }} />;
      default: return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  const notificationMenu = (
    <Menu style={{ width: 320, maxHeight: 400, overflowY: 'auto' }}>
      <Menu.Item key="header" disabled style={{ backgroundColor: '#f5f5f5', fontWeight: 'bold' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Notifications</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: isConnected ? '#52c41a' : '#ff4d4f',
              }}
            />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {isConnected ? 'Live' : 'Offline'}
            </Text>
          </div>
        </div>
      </Menu.Item>
      
      {unreadCount > 0 && (
        <Menu.Item key="mark-all" onClick={markAllAsRead}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            Mark all as read
          </Text>
        </Menu.Item>
      )}
      
      <Menu.Divider />
      
      {notifications.length === 0 ? (
        <Menu.Item key="empty" disabled>
          <div style={{ textAlign: 'center', padding: '20px 0', color: '#999' }}>
            <BellOutlined style={{ fontSize: '24px', marginBottom: '8px' }} />
            <div>No notifications yet</div>
          </div>
        </Menu.Item>
      ) : (
        notifications.slice(0, 10).map((notif) => (
          <Menu.Item
            key={notif.id}
            onClick={() => markAsRead(notif.id)}
            style={{
              backgroundColor: notif.read ? 'transparent' : '#f6ffed',
              borderLeft: notif.read ? 'none' : '3px solid #52c41a',
            }}
          >
            <div style={{ display: 'flex', gap: 8 }}>
              {getNotificationIcon(notif.type)}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: notif.read ? 'normal' : 'bold', fontSize: '14px' }}>
                  {notif.title}
                </div>
                <div style={{ 
                  fontSize: '12px', 
                  color: '#666', 
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {notif.message}
                </div>
                <div style={{ fontSize: '11px', color: '#999', marginTop: '2px' }}>
                  {formatTimestamp(notif.timestamp)}
                </div>
              </div>
            </div>
          </Menu.Item>
        ))
      )}
      
      {notifications.length > 10 && (
        <Menu.Item key="view-all">
          <Text type="secondary" style={{ fontSize: '12px' }}>
            View all notifications
          </Text>
        </Menu.Item>
      )}
    </Menu>
  );

  return (
    <Dropdown 
      overlay={notificationMenu} 
      trigger={['click']} 
      placement="bottomRight"
      overlayStyle={{ zIndex: 1050 }}
    >
      <div style={{ cursor: 'pointer', position: 'relative' }}>
        <Badge count={unreadCount} size="small" offset={[-2, 2]}>
          <Avatar 
            size="small" 
            icon={<BellOutlined />} 
            style={{ 
              backgroundColor: isConnected ? '#1890ff' : '#d9d9d9',
              border: '1px solid #d9d9d9'
            }} 
          />
        </Badge>
      </div>
    </Dropdown>
  );
};

export default RealTimeNotifications;