# 🚀 Complete Guide: Running SmartGriev with Multi-Model Image Processing

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Running the System](#running-the-system)
4. [Using the Multi-Model Features](#using-the-multi-model-features)
5. [Testing and Verification](#testing-and-verification)
6. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Minimum Requirements (CPU Mode)
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.8 or higher
- **RAM**: 8 GB minimum, 16 GB recommended
- **Storage**: 5 GB free space for models
- **CPU**: Intel i5 or equivalent

### Recommended Requirements (GPU Mode)
- **GPU**: NVIDIA GPU with 4GB+ VRAM
- **CUDA**: 11.8 or higher
- **cuDNN**: Compatible version
- **RAM**: 16 GB+

---

## 📦 Installation

### Step 1: Clone the Repository (if not already done)

```bash
git clone https://github.com/jenish2917/smartgriev.git
cd smartgriev
```

### Step 2: Install System Dependencies

#### Windows
```powershell
# Install Tesseract OCR
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR
# Add to PATH during installation

# Verify installation
tesseract --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev
sudo apt-get install -y python3-pip python3-venv
sudo apt-get install -y libgl1-mesa-glx  # For OpenCV
```

#### macOS
```bash
brew install tesseract
brew install python@3.9
```

### Step 3: Quick Setup with Script

#### Windows PowerShell
```powershell
# Run the quick start script
.\QUICK_START_MULTIMODEL.ps1

# Select option 5 for complete setup
```

#### Manual Setup (All Platforms)

```bash
# Navigate to backend
cd smartgriev/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install requirements
pip install -r requirements_multimodel.txt

# Setup and download models
python setup_multimodel.py

# Test the system
python test_multimodel.py
```

---

## 🏃 Running the System

### Option 1: Run Everything Together

```bash
# Terminal 1: Backend
cd smartgriev/backend
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/macOS
python manage.py runserver

# Terminal 2: Frontend
cd smartgriev/frontend
npm install
npm start
```

### Option 2: Use Quick Start Script

```powershell
# Windows
.\QUICK_START_MULTIMODEL.ps1

# Select option 4 to run Django server
# Then in another terminal, run frontend
```

### Access the Application

1. **Backend API**: http://127.0.0.1:8000
2. **Frontend**: http://localhost:3000
3. **Admin Panel**: http://127.0.0.1:8000/admin

---

## 🎯 Using the Multi-Model Features

### From the Frontend (User Interface)

#### 1. Navigate to Complaint Submission
- Go to http://localhost:3000
- Click on "File Complaint" or "Multimodal Submit"

#### 2. Upload Image
- Click "Upload Image" button
- Select an image containing:
  - Damaged infrastructure (potholes, broken roads)
  - Garbage/waste issues
  - Text/signs
  - Any civic problem

#### 3. Automatic Processing
The system will automatically:
- ✅ Detect objects using YOLO
- ✅ Extract text using OCR
- ✅ Classify scene using CLIP
- ✅ Analyze with ResNet
- ✅ Categorize complaint
- ✅ Assign priority
- ✅ Suggest department

#### 4. Review Results
You'll see:
- **Detected Objects**: What the system found
- **Extracted Text**: Any text from the image
- **Category**: Auto-assigned category
- **Priority**: Suggested urgency level
- **Department**: Recommended department

### From the API (Programmatic Access)

```python
import requests

# Prepare files
files = {
    'image_file': open('complaint_image.jpg', 'rb')
}

# Prepare data
data = {
    'title': 'Road Damage',
    'description': 'Pothole on main street',
    'priority': 'high',
    'process_multimodal': True  # Enable AI processing
}

# Submit complaint
response = requests.post(
    'http://127.0.0.1:8000/api/complaints/multimodal/',
    files=files,
    data=data,
    headers={'Authorization': f'Bearer {your_token}'}
)

# Get results
result = response.json()
print(f"Detected Objects: {result['complaint']['detected_objects']}")
print(f"Extracted Text: {result['complaint']['image_ocr_text']}")
print(f"Category: {result['complaint']['department_classification']}")
```

---

## 🧪 Testing and Verification

### Test 1: System Setup Verification

```bash
cd smartgriev/backend
python setup_multimodel.py
```

**Expected Output:**
```
✓ SUCCESS: Checking Python version
✓ SUCCESS: Installing requirements
✓ SUCCESS: Downloading YOLO model
✓ SUCCESS: Downloading CLIP model
✓ SUCCESS: Downloading ResNet model
✓ SUCCESS: Setting up EasyOCR
✓ SUCCESS: Checking Tesseract OCR
✓ SUCCESS: Testing advanced processor

8/8 steps completed successfully
🎉 Setup completed successfully!
```

### Test 2: Multi-Model Processing

```bash
python test_multimodel.py
```

**Expected Output:**
```
📊 Models Used: YOLOv8, OCR, CLIP, ResNet50
🎯 YOLO Object Detection: 3 objects detected
📝 OCR Text Extraction: Text found
🏞️ Scene Classification: damaged road with potholes (87%)
⚠️ Complaint Analysis: infrastructure, severity=high
✓ Test Completed Successfully!
```

### Test 3: End-to-End Test

1. **Open Frontend**: http://localhost:3000
2. **Login/Register**: Create an account
3. **Go to Chatbot**: Test voice and text features
4. **Submit Complaint**:
   - Take/upload a photo of a civic issue
   - Add description
   - Submit
5. **Check Results**:
   - View detected objects
   - See extracted text
   - Verify auto-categorization

---

## 🔧 Troubleshooting

### Issue 1: Tesseract Not Found

**Error:**
```
TesseractNotFoundError: tesseract is not installed
```

**Solution (Windows):**
```powershell
# Download and install from:
# https://github.com/UB-Mannheim/tesseract/wiki

# Add to PATH or set in code:
$env:PATH += ";C:\Program Files\Tesseract-OCR"

# Or in Python:
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Issue 2: CUDA/GPU Not Available

**Warning:**
```
CUDA not available, using CPU
```

**Solution:**
```bash
# For CPU-only systems, this is normal and expected
# Models will run on CPU (slower but functional)

# To enable GPU (if you have NVIDIA GPU):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Issue 3: Out of Memory

**Error:**
```
RuntimeError: CUDA out of memory
```

**Solution:**
```python
# Use CPU mode
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Or use smaller models
# In advanced_image_processor.py:
# yolov8n.pt instead of yolov8x.pt
```

### Issue 4: Models Not Downloading

**Error:**
```
Failed to download model
```

**Solution:**
```bash
# Manual download
cd smartgriev/backend

# Download YOLO manually
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# Download CLIP manually
python -c "from transformers import CLIPModel; CLIPModel.from_pretrained('openai/clip-vit-base-patch32')"
```

### Issue 5: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'ultralytics'
```

**Solution:**
```bash
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/macOS

# Reinstall requirements
pip install -r requirements_multimodel.txt
```

### Issue 6: Port Already in Use

**Error:**
```
Error: That port is already in use.
```

**Solution:**
```bash
# Use a different port
python manage.py runserver 8001

# Or kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux:
lsof -i :8000
kill -9 <PID>
```

### Issue 7: Frontend Not Connecting to Backend

**Issue:** Frontend shows connection errors

**Solution:**
```javascript
// Check API URL in frontend
// src/pages/chatbot/Chatbot.tsx
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Ensure CORS is configured in Django
// backend/config/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
```

---

## 📊 Performance Benchmarks

### Processing Times (Average)

| Operation | CPU | GPU | Quality |
|-----------|-----|-----|---------|
| YOLO Detection | 2-3s | 0.5s | High |
| OCR Extraction | 1-2s | 1-2s | High |
| CLIP Classification | 3-4s | 1s | High |
| ResNet Classification | 4-5s | 1s | High |
| **Total Processing** | **10-15s** | **3-5s** | **High** |

### Memory Usage

| Component | RAM | VRAM (GPU) |
|-----------|-----|------------|
| YOLO | 2 GB | 1 GB |
| CLIP | 1 GB | 500 MB |
| ResNet | 1 GB | 500 MB |
| OCR | 500 MB | - |
| **Total** | **4-5 GB** | **2 GB** |

---

## 🎓 Next Steps

1. **Customize Categories**:
   - Edit `COMPLAINT_OBJECTS` in `advanced_image_processor.py`
   - Add your specific complaint types

2. **Improve Accuracy**:
   - Add more training data
   - Fine-tune models for your region
   - Adjust confidence thresholds

3. **Optimize Performance**:
   - Use GPU for faster processing
   - Implement caching for common objects
   - Batch process multiple images

4. **Extend Functionality**:
   - Add video processing
   - Integrate more models
   - Create custom detectors

---

## 📞 Support

For help:
- **Check Logs**: `backend/logs/django.log`
- **Run Diagnostics**: `python test_multimodel.py`
- **Review Documentation**: `MULTIMODEL_README.md`

---

## ✅ Quick Checklist

Before reporting issues, verify:

- [ ] Python 3.8+ installed
- [ ] Tesseract OCR installed and in PATH
- [ ] Virtual environment activated
- [ ] All packages installed (`pip list`)
- [ ] Models downloaded (check `~/.cache/huggingface/`)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] CORS configured correctly
- [ ] Sufficient disk space (5+ GB)
- [ ] Sufficient RAM (8+ GB)

---

**Happy Coding! 🎉**

*Built for SmartGriev - Making civic complaints smarter with AI*
