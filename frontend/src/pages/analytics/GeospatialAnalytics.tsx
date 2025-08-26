import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Button,
  Select,
  Statistic,
  Tag,
  List,
  Alert,
  Tooltip,
  Switch,
} from 'antd';
import {
  EnvironmentOutlined,
  HeatMapOutlined,
  ClusterOutlined,
  EyeOutlined,
  DownloadOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';

const { Title, Text } = Typography;

// Fix for default markers in React Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface GeoComplaint {
  id: string;
  title: string;
  latitude: number;
  longitude: number;
  status: 'pending' | 'in_progress' | 'resolved' | 'rejected';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category: string;
  department: string;
  created_at: string;
  area_type?: string;
}

interface HotspotArea {
  name: string;
  latitude: number;
  longitude: number;
  complaint_count: number;
  avg_resolution_time: number;
  severity_score: number;
}

const GeospatialAnalytics: React.FC = () => {
  const mapRef = useRef<any>(null);
  const [complaints, setComplaints] = useState<GeoComplaint[]>([]);
  const [hotspots, setHotspots] = useState<HotspotArea[]>([]);
  const [loading, setLoading] = useState(false);
  const [mapView, setMapView] = useState<'markers' | 'heatmap' | 'clusters'>('markers');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showHotspots, setShowHotspots] = useState(true);

  // Default center (India)
  const defaultCenter: [number, number] = [20.5937, 78.9629];
  const defaultZoom = 5;

  // Mock data
  const mockComplaints: GeoComplaint[] = [
    {
      id: 'CMP-001',
      title: 'Street Light Not Working',
      latitude: 28.6139,
      longitude: 77.2090,
      status: 'pending',
      priority: 'medium',
      category: 'Infrastructure',
      department: 'Electricity Board',
      created_at: '2024-01-15',
      area_type: 'residential',
    },
    {
      id: 'CMP-002',
      title: 'Water Supply Issue',
      latitude: 19.0760,
      longitude: 72.8777,
      status: 'in_progress',
      priority: 'high',
      category: 'Utilities',
      department: 'Water Board',
      created_at: '2024-01-14',
      area_type: 'commercial',
    },
    {
      id: 'CMP-003',
      title: 'Road Pothole',
      latitude: 13.0827,
      longitude: 80.2707,
      status: 'resolved',
      priority: 'low',
      category: 'Infrastructure',
      department: 'PWD',
      created_at: '2024-01-13',
      area_type: 'public',
    },
  ];

  const mockHotspots: HotspotArea[] = [
    {
      name: 'Connaught Place, Delhi',
      latitude: 28.6315,
      longitude: 77.2167,
      complaint_count: 45,
      avg_resolution_time: 72,
      severity_score: 8.5,
    },
    {
      name: 'Andheri, Mumbai',
      latitude: 19.1136,
      longitude: 72.8697,
      complaint_count: 38,
      avg_resolution_time: 96,
      severity_score: 7.2,
    },
  ];

  useEffect(() => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setComplaints(mockComplaints);
      setHotspots(mockHotspots);
      setLoading(false);
    }, 1000);
  }, []);

  const getMarkerColor = (status: string, priority: string) => {
    if (priority === 'urgent') return 'red';
    if (status === 'resolved') return 'green';
    if (status === 'in_progress') return 'blue';
    return 'orange';
  };

  const filteredComplaints = complaints.filter(complaint => {
    const categoryMatch = filterCategory === 'all' || complaint.category === filterCategory;
    const statusMatch = filterStatus === 'all' || complaint.status === filterStatus;
    return categoryMatch && statusMatch;
  });

  const heatmapPoints = filteredComplaints.map(complaint => [
    complaint.latitude,
    complaint.longitude,
    1 // intensity
  ]);

  const categories = [...new Set(complaints.map(c => c.category))];
  const statuses = ['pending', 'in_progress', 'resolved', 'rejected'];

  const exportData = () => {
    const data = {
      complaints: filteredComplaints,
      hotspots,
      filters: { category: filterCategory, status: filterStatus },
      exported_at: new Date().toISOString(),
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `geospatial-analysis-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="page-header">
        <Title level={2} className="gov-title">
          Geospatial Analytics
        </Title>
        <Text className="gov-subtitle">
          Geographic distribution and analysis of complaints across regions
        </Text>
      </div>

      {/* Controls */}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space wrap>
              <Text strong>View:</Text>
              <Select
                value={mapView}
                onChange={setMapView}
                style={{ width: 120 }}
              >
                <Select.Option value="markers">Markers</Select.Option>
                <Select.Option value="heatmap">Heatmap</Select.Option>
                <Select.Option value="clusters">Clusters</Select.Option>
              </Select>

              <Text strong>Category:</Text>
              <Select
                value={filterCategory}
                onChange={setFilterCategory}
                style={{ width: 150 }}
              >
                <Select.Option value="all">All Categories</Select.Option>
                {categories.map(cat => (
                  <Select.Option key={cat} value={cat}>{cat}</Select.Option>
                ))}
              </Select>

              <Text strong>Status:</Text>
              <Select
                value={filterStatus}
                onChange={setFilterStatus}
                style={{ width: 120 }}
              >
                <Select.Option value="all">All Status</Select.Option>
                {statuses.map(status => (
                  <Select.Option key={status} value={status}>
                    {status.replace('_', ' ').toUpperCase()}
                  </Select.Option>
                ))}
              </Select>

              <Text strong>Hotspots:</Text>
              <Switch
                checked={showHotspots}
                onChange={setShowHotspots}
                checkedChildren="ON"
                unCheckedChildren="OFF"
              />
            </Space>
          </Col>
          <Col>
            <Space>
              <Button icon={<SettingOutlined />}>
                Map Settings
              </Button>
              <Button type="primary" icon={<DownloadOutlined />} onClick={exportData}>
                Export Data
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      <Row gutter={[16, 16]}>
        {/* Map */}
        <Col xs={24} lg={16}>
          <Card title="Geographic Distribution" bordered={false}>
            <div style={{ height: '600px', width: '100%' }}>
              <MapContainer
                center={defaultCenter}
                zoom={defaultZoom}
                style={{ height: '100%', width: '100%' }}
                ref={mapRef}
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                
                {mapView === 'markers' && filteredComplaints.map(complaint => (
                  <CircleMarker
                    key={complaint.id}
                    center={[complaint.latitude, complaint.longitude]}
                    radius={8}
                    fillColor={getMarkerColor(complaint.status, complaint.priority)}
                    color="white"
                    weight={2}
                    opacity={1}
                    fillOpacity={0.8}
                  >
                    <Popup>
                      <div>
                        <Text strong>{complaint.title}</Text><br />
                        <Text>Status: </Text>
                        <Tag color={getMarkerColor(complaint.status, complaint.priority)}>
                          {complaint.status.toUpperCase()}
                        </Tag><br />
                        <Text>Department: {complaint.department}</Text><br />
                        <Text>Category: {complaint.category}</Text><br />
                        <Text>Created: {new Date(complaint.created_at).toLocaleDateString()}</Text>
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}

                {showHotspots && hotspots.map((hotspot, index) => (
                  <CircleMarker
                    key={`hotspot-${index}`}
                    center={[hotspot.latitude, hotspot.longitude]}
                    radius={hotspot.complaint_count / 2}
                    fillColor="red"
                    color="darkred"
                    weight={3}
                    opacity={0.7}
                    fillOpacity={0.3}
                  >
                    <Popup>
                      <div>
                        <Text strong style={{ color: 'red' }}>
                          <HeatMapOutlined /> Hotspot: {hotspot.name}
                        </Text><br />
                        <Text>Complaints: {hotspot.complaint_count}</Text><br />
                        <Text>Avg Resolution: {hotspot.avg_resolution_time}h</Text><br />
                        <Text>Severity Score: {hotspot.severity_score}/10</Text>
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}
              </MapContainer>
            </div>
          </Card>
        </Col>

        {/* Statistics */}
        <Col xs={24} lg={8}>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            {/* Key Metrics */}
            <Card title="Geographic Metrics" size="small">
              <Row gutter={[8, 8]}>
                <Col span={12}>
                  <Statistic
                    title="Total Points"
                    value={filteredComplaints.length}
                    prefix={<EnvironmentOutlined />}
                    valueStyle={{ fontSize: 20 }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Hotspots"
                    value={hotspots.length}
                    prefix={<HeatMapOutlined />}
                    valueStyle={{ fontSize: 20, color: '#f5222d' }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Areas Covered"
                    value={categories.length}
                    prefix={<ClusterOutlined />}
                    valueStyle={{ fontSize: 20 }}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="Avg Response"
                    value={48}
                    suffix="hrs"
                    valueStyle={{ fontSize: 20 }}
                  />
                </Col>
              </Row>
            </Card>

            {/* Hotspots List */}
            <Card title="Problem Hotspots" size="small">
              <Alert
                message="High Activity Areas"
                description="Areas with unusually high complaint volumes require immediate attention"
                type="warning"
                style={{ marginBottom: 12 }}
                showIcon
              />
              <List
                size="small"
                dataSource={hotspots}
                renderItem={(hotspot) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={<HeatMapOutlined style={{ color: '#f5222d' }} />}
                      title={
                        <Space>
                          <Text strong>{hotspot.name}</Text>
                          <Tag color="red">{hotspot.complaint_count} complaints</Tag>
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size={0}>
                          <Text type="secondary">
                            Avg Resolution: {hotspot.avg_resolution_time}h
                          </Text>
                          <Text type="secondary">
                            Severity: {hotspot.severity_score}/10
                          </Text>
                        </Space>
                      }
                    />
                    <Tooltip title="View Details">
                      <Button size="small" icon={<EyeOutlined />} />
                    </Tooltip>
                  </List.Item>
                )}
              />
            </Card>

            {/* Legend */}
            <Card title="Map Legend" size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong>Status Colors:</Text>
                </div>
                <Space wrap>
                  <Tag color="orange">PENDING</Tag>
                  <Tag color="blue">IN PROGRESS</Tag>
                  <Tag color="green">RESOLVED</Tag>
                  <Tag color="red">URGENT</Tag>
                </Space>
                <div style={{ marginTop: 8 }}>
                  <Text strong>Hotspot Areas:</Text>
                </div>
                <Text type="secondary">
                  Red circles indicate areas with high complaint density
                </Text>
              </Space>
            </Card>
          </Space>
        </Col>
      </Row>
    </div>
  );
};

export default GeospatialAnalytics;
