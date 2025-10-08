import React, { useState, ChangeEvent, FormEvent } from 'react';
import axios from 'axios';

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
  video: File | null;
  image: File | null;
  audio: File | null;
}

interface PreviewState {
  video: string | null;
  image: string | null;
  audio: string | null;
}

interface ResultState {
  complaint?: {
    id: number;
    status: string;
  };
  processing_status?: {
    video_processed: boolean;
    image_processed: boolean;
    audio_processed: boolean;
    ai_classified: boolean;
  };
}

const MultimodalComplaintSubmit = () => {
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
    video: null,
    image: null,
    audio: null
  });
  
  const [previews, setPreviews] = useState<PreviewState>({
    video: null,
    image: null,
    audio: null
  });
  
  const [loading, setLoading] = useState<boolean>(false);
  const [success, setSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ResultState | null>(null);

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

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Please login to submit a complaint');
      }

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
      if (files.video) submitData.append('video_file', files.video);
      if (files.image) submitData.append('image_file', files.image);
      if (files.audio) submitData.append('audio_file', files.audio);

      const response = await axios.post(
        'http://127.0.0.1:8000/api/complaints/submit/',
        submitData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
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
      setFiles({ video: null, image: null, audio: null });
      setPreviews({ video: null, image: null, audio: null });

    } catch (err) {
      const error = err as any;
      setError(error.response?.data?.error || error.message || 'Failed to submit complaint');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="multimodal-complaint-container" style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h2 style={{
        color: '#FF671F',
        borderBottom: '3px solid #046A38',
        paddingBottom: '10px'
      }}>
        🎥 Submit Multimodal Complaint
      </h2>
      
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Submit your complaint using text, images, videos, or audio. AI will process your submission automatically.
      </p>

      {success && result && (
        <div style={{
          backgroundColor: '#d4edda',
          color: '#155724',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #c3e6cb'
        }}>
          <h3>✅ Complaint Submitted Successfully!</h3>
          <p><strong>Complaint ID:</strong> {result.complaint?.id}</p>
          <p><strong>Status:</strong> {result.complaint?.status}</p>
          <p><strong>Tracking Number:</strong> COMP-{String(result.complaint?.id).padStart(6, '0')}</p>
          
          {result.processing_status && (
            <div style={{ marginTop: '10px', fontSize: '14px' }}>
              <p><strong>Processing Status:</strong></p>
              <ul>
                {result.processing_status.video_processed && <li>✅ Video analyzed</li>}
                {result.processing_status.image_processed && <li>✅ Image processed with OCR</li>}
                {result.processing_status.audio_processed && <li>✅ Audio transcribed</li>}
                {result.processing_status.ai_classified && <li>✅ Auto-classified by AI</li>}
              </ul>
            </div>
          )}
        </div>
      )}

      {error && (
        <div style={{
          backgroundColor: '#f8d7da',
          color: '#721c24',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #f5c6cb'
        }}>
          <strong>❌ Error:</strong> {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Title */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Complaint Title *
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            required
            placeholder="Brief title for your complaint"
            style={{
              width: '100%',
              padding: '10px',
              fontSize: '16px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              boxSizing: 'border-box'
            }}
          />
        </div>

        {/* Description */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Description (optional if uploading media)
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            rows={4}
            placeholder="Describe your complaint in detail..."
            style={{
              width: '100%',
              padding: '10px',
              fontSize: '16px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              boxSizing: 'border-box',
              resize: 'vertical'
            }}
          />
        </div>

        {/* Media Upload Section */}
        <div style={{
          backgroundColor: '#f8f9fa',
          padding: '20px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '2px dashed #ddd'
        }}>
          <h3 style={{ marginTop: 0, color: '#046A38' }}>📎 Upload Media (Optional)</h3>
          
          {/* Video Upload */}
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              🎥 Video Evidence
            </label>
            {!previews.video ? (
              <input
                type="file"
                accept="video/*"
                onChange={(e) => handleFileChange(e, 'video')}
                style={{
                  display: 'block',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  width: '100%',
                  boxSizing: 'border-box'
                }}
              />
            ) : (
              <div style={{ position: 'relative' }}>
                <video controls src={previews.video} style={{ width: '100%', borderRadius: '8px' }} />
                <button
                  type="button"
                  onClick={() => removeFile('video')}
                  style={{
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '5px 10px',
                    cursor: 'pointer'
                  }}
                >
                  Remove
                </button>
              </div>
            )}
          </div>

          {/* Image Upload */}
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              📷 Image Evidence
            </label>
            {!previews.image ? (
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFileChange(e, 'image')}
                style={{
                  display: 'block',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  width: '100%',
                  boxSizing: 'border-box'
                }}
              />
            ) : (
              <div style={{ position: 'relative' }}>
                <img src={previews.image} alt="Preview" style={{ width: '100%', borderRadius: '8px' }} />
                <button
                  type="button"
                  onClick={() => removeFile('image')}
                  style={{
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '5px 10px',
                    cursor: 'pointer'
                  }}
                >
                  Remove
                </button>
              </div>
            )}
          </div>

          {/* Audio Upload */}
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              🎤 Audio Recording
            </label>
            {!previews.audio ? (
              <input
                type="file"
                accept="audio/*"
                onChange={(e) => handleFileChange(e, 'audio')}
                style={{
                  display: 'block',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  width: '100%',
                  boxSizing: 'border-box'
                }}
              />
            ) : (
              <div style={{ position: 'relative' }}>
                <audio controls src={previews.audio} style={{ width: '100%' }} />
                <button
                  type="button"
                  onClick={() => removeFile('audio')}
                  style={{
                    marginTop: '10px',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '5px 10px',
                    cursor: 'pointer'
                  }}
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Priority & Urgency */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Priority
            </label>
            <select
              name="priority"
              value={formData.priority}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '10px',
                fontSize: '16px',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Urgency Level
            </label>
            <select
              name="urgency_level"
              value={formData.urgency_level}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '10px',
                fontSize: '16px',
                border: '1px solid #ddd',
                borderRadius: '4px'
              }}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        {/* Location */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            📍 Incident Address
          </label>
          <input
            type="text"
            name="incident_address"
            value={formData.incident_address}
            onChange={handleInputChange}
            placeholder="Enter incident address or location"
            style={{
              width: '100%',
              padding: '10px',
              fontSize: '16px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              boxSizing: 'border-box',
              marginBottom: '10px'
            }}
          />
          <button
            type="button"
            onClick={getLocation}
            style={{
              backgroundColor: '#046A38',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
            📍 Get My Current Location
          </button>
          {formData.incident_latitude && formData.incident_longitude && (
            <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
              📍 Location captured: {formData.incident_latitude.toFixed(6)}, {formData.incident_longitude.toFixed(6)}
            </p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '15px',
            backgroundColor: loading ? '#ccc' : '#FF671F',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '18px',
            fontWeight: 'bold',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'background-color 0.3s'
          }}
        >
          {loading ? '⏳ Processing...' : '📤 Submit Complaint'}
        </button>
      </form>

      <div style={{
        marginTop: '30px',
        padding: '15px',
        backgroundColor: '#fff3cd',
        borderRadius: '8px',
        border: '1px solid #ffc107'
      }}>
        <p style={{ margin: 0, fontSize: '14px' }}>
          <strong>💡 Note:</strong> AI will automatically analyze your uploaded media to extract text, detect objects, and classify your complaint to the appropriate department.
        </p>
      </div>
    </div>
  );
};

export default MultimodalComplaintSubmit;
