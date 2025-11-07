# DINOv2 Integration Guide for SmartGriev

## 🎉 What's New

We've integrated **Facebook's DINOv2** (Distilled No-Labels version 2) model into SmartGriev to provide advanced visual understanding of complaint images!

## 🔍 What is DINOv2?

DINOv2 is a state-of-the-art self-supervised vision transformer model developed by Meta AI (Facebook). It can:

- **Extract Rich Visual Features**: Understand image content without specific training
- **Scene Classification**: Identify whether images show outdoor/indoor, infrastructure, public spaces
- **Element Detection**: Detect visual elements like lighting conditions, complexity, environment type
- **Similarity Comparison**: Find similar complaints based on visual similarity
- **Automatic Categorization**: Suggest complaint categories based on visual content

## 📦 Installation

### Backend Dependencies

Install the required Python packages:

```bash
cd backend
pip install torch torchvision
pip install transformers
pip install pillow opencv-python numpy
```

### GPU Support (Optional but Recommended)

For faster processing, install CUDA-enabled PyTorch:

```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

## 🚀 How It Works

### 1. Image Upload Flow

```
Citizen uploads complaint image
    ↓
OCR extracts text from image
    ↓
DINOv2 analyzes visual content
    ↓
Visual Analyzer detects objects
    ↓
Combined results stored in database
    ↓
Automatic department assignment
```

### 2. DINOv2 Analysis Output

When an image is processed, DINOv2 provides:

```json
{
  "analysis_method": "dinov2",
  "scene_classification": {
    "scene_type": "outdoor",
    "confidence": 0.87
  },
  "detected_elements": [
    "outdoor_environment",
    "complex_scene",
    "multiple_objects",
    "bright_condition"
  ],
  "complaint_analysis": {
    "suggested_category": "infrastructure",
    "urgency_indicators": [
      "public_exposure",
      "multiple_issues_detected"
    ],
    "requires_attention": true
  },
  "quality_metrics": {
    "brightness": 178.5,
    "contrast": 45.2,
    "quality_score": 0.72
  },
  "image_properties": {
    "width": 1920,
    "height": 1080,
    "aspect_ratio": 1.77
  }
}
```

### 3. Complaint Categories Detected

DINOv2 can suggest these categories:

- **Infrastructure**: Roads, buildings, bridges, construction
- **Sanitation**: Garbage, waste, drainage issues
- **Utilities**: Streetlights, electricity, water pipes
- **Public Spaces**: Parks, playgrounds, gardens
- **Traffic**: Vehicles, signals, congestion
- **Safety**: Hazards, dangers, potholes
- **Environmental**: Trees, plants, weather-related

## 🔧 Configuration

### Model Selection

You can choose different DINOv2 model sizes:

```python
# In dinov2_processor.py
processor = DINOv2Processor(
    model_name="facebook/dinov2-small"   # Fastest, less accurate
    # or
    model_name="facebook/dinov2-base"    # Balanced (default)
    # or
    model_name="facebook/dinov2-large"   # More accurate, slower
    # or
    model_name="facebook/dinov2-giant"   # Best accuracy, slowest
)
```

### Fallback Mode

If DINOv2 libraries are not installed, the system automatically falls back to basic image analysis:

- Image properties (size, format, aspect ratio)
- Brightness and contrast analysis
- Blur detection
- Basic quality assessment

## 📝 API Usage

### Analyze Image Directly

```python
from machine_learning.dinov2_processor import analyze_complaint_image

# From file path
result = analyze_complaint_image('/path/to/image.jpg')

# From bytes
result = analyze_complaint_image_bytes(image_bytes)
```

### Compare Images

```python
from machine_learning.dinov2_processor import get_dinov2_processor

processor = get_dinov2_processor()
similarity = processor.compare_images(image1, image2)

if similarity['similarity_score'] > 0.8:
    print("These complaints are visually similar!")
```

### Check System Status

```python
from machine_learning.dinov2_processor import get_dinov2_info

info = get_dinov2_info()
print(f"DINOv2 Available: {info['available']}")
print(f"Device: {info['device']}")
print(f"Model: {info['model_name']}")
```

## 🎨 Frontend Integration

The chatbot has been updated with Indian Government colors:

### Color Palette

- **Primary Blue**: `#2196F3` - Main government blue
- **Saffron/Orange**: `#FF9933` - Accent color
- **Green**: `#138808` - Success/positive actions
- **Navy Blue**: `#000080` - Headers and important elements
- **Light Blue**: `#E3F2FD` - Backgrounds

### Bilingual Support

The chatbot now displays text in both Hindi and English:
- नमस्ते! Hello!
- त्वरित क्रियाएँ | Quick Actions
- सहायता विषय | Help Topics

## 🧪 Testing

### Test DINOv2 Module

```bash
cd backend/machine_learning
python dinov2_processor.py
```

### Test Complete Pipeline

```python
from complaints.serializers import MultimodalComplaintSerializer
from django.core.files.uploadedfile import SimpleUploadedFile

# Create test complaint with image
with open('test_image.jpg', 'rb') as f:
    image_file = SimpleUploadedFile('test.jpg', f.read(), content_type='image/jpeg')

data = {
    'title': 'Test Complaint',
    'description': 'Testing DINOv2 integration',
    'priority': 'medium',
    'urgency_level': 'medium',
}

files = {'image_file': image_file}
serializer = MultimodalComplaintSerializer(data=data)
if serializer.is_valid():
    complaint = serializer.save()
    print(f"Detected elements: {complaint.detected_objects}")
    print(f"Category: {complaint.department_classification}")
```

## 📊 Performance Optimization

### Model Caching

DINOv2 models are cached automatically:

```python
# First load: 5-10 seconds
# Subsequent loads: < 1 second (cached)
```

### GPU Acceleration

With GPU:
- Small model: ~0.1-0.2 seconds per image
- Base model: ~0.2-0.4 seconds per image
- Large model: ~0.5-1.0 seconds per image

Without GPU (CPU):
- Small model: ~1-2 seconds per image
- Base model: ~3-5 seconds per image
- Large model: ~8-12 seconds per image

### Clear Cache

To free up memory:

```python
from machine_learning.dinov2_processor import clear_dinov2_cache
clear_dinov2_cache()
```

## 🔒 Security & Privacy

- All image processing happens on your server
- No data sent to external APIs
- Models run locally
- Images are processed in memory
- Original images are saved securely

## 🐛 Troubleshooting

### DINOv2 Not Loading

**Error**: "DINOv2 not available"

**Solution**:
```bash
pip install torch transformers pillow
```

### Out of Memory

**Error**: "CUDA out of memory"

**Solution**:
- Use a smaller model (`dinov2-small`)
- Process images in smaller batches
- Reduce image resolution before processing
- Clear cache: `clear_dinov2_cache()`

### Slow Processing

**Solution**:
- Use GPU if available
- Use `dinov2-small` for faster processing
- Enable model caching (enabled by default)
- Reduce image size before upload

## 📚 Training Custom Models

DINOv2 is pre-trained and ready to use, but you can fine-tune it:

### Collect Training Data

1. Gather complaint images from your system
2. Label them with categories
3. Create a dataset structure

### Fine-tuning Script

```python
# training/finetune_dinov2.py (to be created)
from transformers import AutoImageProcessor, AutoModel, TrainingArguments, Trainer
import torch
from torch.utils.data import Dataset

class ComplaintDataset(Dataset):
    def __init__(self, images, labels, processor):
        self.images = images
        self.labels = labels
        self.processor = processor
    
    def __getitem__(self, idx):
        image = self.images[idx]
        inputs = self.processor(images=image, return_tensors="pt")
        return {
            'pixel_values': inputs['pixel_values'].squeeze(),
            'labels': self.labels[idx]
        }
    
    def __len__(self):
        return len(self.images)

# Load base model
model = AutoModel.from_pretrained("facebook/dinov2-base")
processor = AutoImageProcessor.from_pretrained("facebook/dinov2-base")

# Add classification head
num_labels = 7  # Number of complaint categories
classifier = torch.nn.Linear(model.config.hidden_size, num_labels)

# Training configuration
training_args = TrainingArguments(
    output_dir="./dinov2-smartgriev",
    num_train_epochs=10,
    per_device_train_batch_size=8,
    learning_rate=2e-5,
    save_steps=100,
)

# Train model
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
```

## 🌟 Benefits

### For Citizens
- **Better categorization**: Complaints automatically assigned to correct department
- **Faster processing**: Visual analysis helps prioritize urgent issues
- **Similar complaints**: System can find and link related issues

### For Officials
- **Rich insights**: Understand complaint context from images
- **Automatic routing**: Visual features help route to right department
- **Duplicate detection**: Find similar complaints automatically
- **Quality assessment**: Filter low-quality or unclear images

### For System
- **Improved accuracy**: Combines OCR + DINOv2 + Visual Analyzer
- **Graceful degradation**: Falls back to simpler methods if DINOv2 unavailable
- **Scalable**: Efficient caching and GPU support
- **Extensible**: Easy to add new features and categories

## 📈 Roadmap

Future improvements planned:

- [ ] Real-time object detection with bounding boxes
- [ ] Multi-image comparison for duplicate detection
- [ ] Automatic urgency detection from visual cues
- [ ] Integration with Google Maps for location verification
- [ ] Video frame analysis using DINOv2
- [ ] Custom fine-tuned models for Indian infrastructure
- [ ] Regional language support in image text
- [ ] AR overlay for field verification

## 🤝 Contributing

To improve DINOv2 integration:

1. Collect more complaint images
2. Label them accurately
3. Fine-tune model on local data
4. Share results with team

## 📞 Support

For issues or questions:
- Check logs: `logs/smartgriev.log`
- Test with: `python dinov2_processor.py`
- Fallback mode: System continues working without DINOv2

---

**Last Updated**: October 29, 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready with Graceful Fallback
