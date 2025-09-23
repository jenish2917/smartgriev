import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, message, Typography, Space, Tag, Alert, Spin, Menu } from 'antd';
import { SendOutlined, EnvironmentOutlined, FileTextOutlined, HomeOutlined, RobotOutlined, LoginOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface LocationData {
  latitude: number;
  longitude: number;
  address?: string;
}

const SimpleComplaint: React.FC = () => {
  const location = useLocation();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [locationData, setLocationData] = useState<LocationData | null>(null);
  const [locationLoading, setLocationLoading] = useState(false);

  const topMenuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Home',
    },
    {
      key: '/complaint',
      icon: <FileTextOutlined />,
      label: 'Submit Complaint',
    },
    {
      key: '/ai-test',
      icon: <RobotOutlined />,
      label: 'AI Test',
    },
    {
      key: '/login',
      icon: <LoginOutlined />,
      label: 'Login',
    },
  ];

  // Get user's current location
  const getCurrentLocation = () => {
    setLocationLoading(true);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const locationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          };
          setLocationData(locationData);
          
          // Reverse geocoding to get address
          reverseGeocode(locationData.latitude, locationData.longitude);
          setLocationLoading(false);
        },
        (error) => {
          console.error('Error getting location:', error);
          message.error('Unable to get your location. Please enable location services.');
          setLocationLoading(false);
        }
      );
    } else {
      message.error('Geolocation is not supported by this browser.');
      setLocationLoading(false);
    }
  };

  // Reverse geocoding to get readable address
  const reverseGeocode = async (lat: number, lng: number) => {
    try {
      // Using a simple reverse geocoding approach
      const response = await fetch(
        `https://api.opencagedata.com/geocode/v1/json?q=${lat}+${lng}&key=YOUR_API_KEY`
      );
      if (response.ok) {
        const data = await response.json();
        if (data.results && data.results.length > 0) {
          setLocationData((prev: LocationData | null) => prev ? {
            ...prev,
            address: data.results[0].formatted
          } : null);
        }
      }
    } catch (error) {
      console.log('Reverse geocoding failed, using coordinates only');
      setLocationData((prev: LocationData | null) => prev ? {
        ...prev,
        address: `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`
      } : null);
    }
  };

  // Submit complaint
  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const complaintData = {
        title: values.title,
        description: values.description,
        location: locationData ? {
          latitude: locationData.latitude,
          longitude: locationData.longitude,
          address: locationData.address || `${locationData.latitude}, ${locationData.longitude}`
        } : null
      };

      // Submit to backend
      const response = await fetch('/api/complaints/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(complaintData),
      });

      if (response.ok) {
        message.success('Complaint submitted successfully!');
        form.resetFields();
        setLocationData(null);
      } else {
        throw new Error('Failed to submit complaint');
      }
    } catch (error) {
      message.error('Failed to submit complaint. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Auto-get location when component mounts
    getCurrentLocation();
  }, []);

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #FF9933 0%, #138808 100%)',
      padding: '0px'
    }}>
      {/* Government Header */}
      <div className="gov-header">
        <div className="gov-logo">🇮🇳</div>
        <Title level={1} style={{ color: 'white', margin: '0 0 8px 0', textAlign: 'center' }}>
          SmartGriev - Quick Complaint
        </Title>
        <Text style={{ color: 'white', fontSize: 18, display: 'block', textAlign: 'center' }}>
          Digital India Initiative - Citizen Grievance Portal
        </Text>
      </div>

      {/* Top Navigation */}
      <div style={{ 
        background: 'white', 
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)', 
        padding: '0 20px',
        marginBottom: 20
      }}>
        <Menu
          mode="horizontal"
          selectedKeys={[location.pathname]}
          style={{ 
            border: 'none', 
            fontSize: 16,
            background: 'linear-gradient(90deg, #FF9933 0%, #138808 100%)',
            borderRadius: '0 0 8px 8px'
          }}
        >
          {topMenuItems.map(item => (
            <Menu.Item key={item.key} icon={item.icon} style={{ color: 'white', fontWeight: '600' }}>
              <Link to={item.key} style={{ color: 'white' }}>{item.label}</Link>
            </Menu.Item>
          ))}
        </Menu>
      </div>

      <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 20px' }}>
        <Card 
          className="feature-card"
          style={{ 
            borderRadius: 16,
            border: '3px solid #000080',
            boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
          }}
          title={
            <div style={{ textAlign: 'center' }}>
              <FileTextOutlined style={{ fontSize: 24, color: '#FF9933', marginRight: 8 }} />
              <span style={{ color: '#000080', fontSize: 20, fontWeight: 'bold' }}>
                Submit Your Complaint
              </span>
            </div>
          }
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={onFinish}
            style={{ marginTop: 20 }}
          >
            <Form.Item
              name="title"
              label={<Text strong style={{ fontSize: 16 }}>Complaint Title</Text>}
              rules={[{ required: true, message: 'Please enter complaint title' }]}
            >
              <Input 
                placeholder="Brief title for your complaint..."
                style={{ height: 45, borderRadius: 8, fontSize: 16 }}
              />
            </Form.Item>

            <Form.Item
              name="description"
              label={<Text strong style={{ fontSize: 16 }}>Complaint Description</Text>}
              rules={[{ required: true, message: 'Please describe your complaint' }]}
            >
              <TextArea
                placeholder="Describe your complaint in detail..."
                rows={6}
                style={{ borderRadius: 8, fontSize: 16 }}
              />
            </Form.Item>

            {/* Location Section */}
            <div style={{ marginBottom: 24 }}>
              <Text strong style={{ fontSize: 16, color: '#333' }}>Location Information</Text>
              <div style={{ marginTop: 12 }}>
                {locationLoading ? (
                  <div style={{ textAlign: 'center', padding: 20 }}>
                    <Spin size="large" />
                    <div style={{ marginTop: 10 }}>
                      <Text>Getting your location...</Text>
                    </div>
                  </div>
                ) : locationData ? (
                  <Alert
                    message="Location Detected"
                    description={
                      <div>
                        <div><strong>Address:</strong> {locationData.address || 'Getting address...'}</div>
                        <div><strong>Coordinates:</strong> {locationData.latitude.toFixed(6)}, {locationData.longitude.toFixed(6)}</div>
                      </div>
                    }
                    type="success"
                    icon={<EnvironmentOutlined />}
                    style={{ marginBottom: 16 }}
                  />
                ) : (
                  <Alert
                    message="Location Required"
                    description="Location helps us route your complaint to the right local authority."
                    type="warning"
                    style={{ marginBottom: 16 }}
                  />
                )}
                
                <Button 
                  onClick={getCurrentLocation}
                  icon={<EnvironmentOutlined />}
                  loading={locationLoading}
                  style={{ 
                    backgroundColor: '#138808',
                    borderColor: '#138808',
                    color: 'white',
                    fontWeight: 'bold'
                  }}
                >
                  {locationData ? 'Update Location' : 'Get Current Location'}
                </Button>
              </div>
            </div>

            <Form.Item style={{ textAlign: 'center', marginTop: 32 }}>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SendOutlined />}
                loading={loading}
                size="large"
                className="primary-button"
                style={{
                  height: 60,
                  fontSize: 18,
                  fontWeight: 'bold',
                  borderRadius: 10,
                  paddingLeft: 40,
                  paddingRight: 40,
                  background: 'linear-gradient(90deg, #FF9933 0%, #138808 100%)',
                  border: '2px solid #000080'
                }}
              >
                Submit Complaint
              </Button>
            </Form.Item>
          </Form>

          {/* Help Section */}
          <Card 
            size="small" 
            style={{ 
              marginTop: 24,
              background: 'linear-gradient(135deg, #FFF8E1 0%, #F3E5F5 100%)',
              border: '1px solid #FFE082'
            }}
          >
            <Title level={5} style={{ color: '#FF9933', marginBottom: 12 }}>
              📋 How it works:
            </Title>
            <Space direction="vertical" size="small">
              <div>• <Text strong>Fill Details:</Text> Provide title and description of your issue</div>
              <div>• <Text strong>Location:</Text> We automatically detect your location for proper routing</div>
              <div>• <Text strong>AI Processing:</Text> Our AI system classifies and routes to the right department</div>
              <div>• <Text strong>Tracking:</Text> You'll receive updates on complaint status</div>
            </Space>
          </Card>
        </Card>
      </div>
    </div>
  );
};

export default SimpleComplaint;