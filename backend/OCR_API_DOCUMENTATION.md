# SmartGriev OCR API Documentation

## Overview
The SmartGriev OCR (Optical Character Recognition) system provides powerful text extraction capabilities from complaint images using Microsoft's TrOCR model. This enables automatic processing of text-based complaints submitted as images.

## Features
- **Image-to-Text Conversion**: Extract text from images using state-of-the-art TrOCR model
- **Multiple Image Formats**: Supports JPEG, PNG, BMP, TIFF, GIF
- **File Size Limits**: Up to 10MB for basic OCR, 15MB for complaint processing
- **NLP Integration**: Optional named entity recognition and complaint classification
- **Authentication**: JWT-based secure access

## API Endpoints

### 1. Health Check
**GET** `/api/ml/ocr/health/`

Check if OCR services are operational.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "status": "healthy",
    "message": "OCR services are operational",
    "available": true,
    "model": "microsoft/trocr-base-printed"
}
```

### 2. Basic OCR Processing
**POST** `/api/ml/ocr/`

Extract text from any image file.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body:**
- `image`: Image file (required)

**Response:**
```json
{
    "extracted_text": "Text found in the image",
    "text_length": 25,
    "status": "success",
    "processing_time": 2.45
}
```

### 3. Complaint OCR with NLP
**POST** `/api/ml/ocr/complaint/`

Extract text from complaint images with optional NLP processing.

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body:**
- `image`: Complaint image file (required)
- `extract_entities`: Boolean (optional, default: true)
- `classify_complaint`: Boolean (optional, default: true)

**Response:**
```json
{
    "extracted_text": "Complaint text from image",
    "text_length": 50,
    "entities": {
        "persons": ["John Doe"],
        "locations": ["Mumbai"],
        "organizations": ["City Council"],
        "dates": ["2025-09-27"]
    },
    "classification": {
        "category": "UTILITIES",
        "confidence": 0.85,
        "department": "Water, Electricity and Utilities"
    },
    "sentiment": {
        "polarity": "negative",
        "confidence": 0.72
    },
    "status": "success",
    "processing_time": 3.21
}
```

## Usage Examples

### Python Example
```python
import requests

# Get JWT token (implementation depends on your auth system)
token = "your_jwt_token"
headers = {"Authorization": f"Bearer {token}"}

# Basic OCR
with open("complaint_image.jpg", "rb") as f:
    files = {"image": f}
    response = requests.post(
        "http://127.0.0.1:8000/api/ml/ocr/",
        headers=headers,
        files=files
    )
    result = response.json()
    print(f"Extracted: {result['extracted_text']}")

# Complaint OCR with NLP
with open("complaint_image.jpg", "rb") as f:
    files = {"image": f}
    data = {
        "extract_entities": True,
        "classify_complaint": True
    }
    response = requests.post(
        "http://127.0.0.1:8000/api/ml/ocr/complaint/",
        headers=headers,
        files=files,
        data=data
    )
    result = response.json()
    print(f"Text: {result['extracted_text']}")
    print(f"Classification: {result['classification']}")
```

### cURL Example
```bash
# Health Check
curl -X GET "http://127.0.0.1:8000/api/ml/ocr/health/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Basic OCR
curl -X POST "http://127.0.0.1:8000/api/ml/ocr/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "image=@complaint_image.jpg"

# Complaint OCR
curl -X POST "http://127.0.0.1:8000/api/ml/ocr/complaint/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "image=@complaint_image.jpg" \
     -F "extract_entities=true" \
     -F "classify_complaint=true"
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid request data",
    "details": {
        "image": ["This field is required."]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 413 Payload Too Large
```json
{
    "error": "Invalid request data",
    "details": {
        "image": ["Image file too large. Maximum size is 10MB."]
    }
}
```

### 500 Internal Server Error
```json
{
    "extracted_text": "",
    "text_length": 0,
    "status": "error",
    "error_message": "Error during OCR processing: Model not available",
    "processing_time": 0.1
}
```

## Performance Notes

- **First Request**: The first OCR request may take longer (10-20 seconds) as the TrOCR model needs to be loaded
- **Subsequent Requests**: Faster processing (2-5 seconds) as the model stays in memory
- **Model Size**: The TrOCR model is approximately 1.33GB and is cached locally
- **CPU Processing**: Currently uses CPU processing; GPU acceleration can be enabled for better performance

## Integration with SmartGriev

The OCR system integrates seamlessly with the SmartGriev complaint management system:

1. **Automatic Text Extraction**: Images uploaded as complaints are automatically processed
2. **NLP Pipeline**: Extracted text feeds into the existing NLP pipeline for classification
3. **Database Storage**: OCR results can be stored alongside complaint data
4. **Multi-language Support**: Supports text extraction in multiple languages

## Technical Details

- **Model**: Microsoft TrOCR (Transformer-based OCR)
- **Framework**: Hugging Face Transformers
- **Supported Formats**: JPEG, PNG, BMP, TIFF, GIF
- **Authentication**: JWT tokens required for all endpoints
- **Rate Limiting**: Consider implementing rate limiting for production use

## Next Steps

To further enhance the OCR system:

1. **GPU Acceleration**: Enable CUDA support for faster processing
2. **Batch Processing**: Add support for processing multiple images
3. **Language Detection**: Auto-detect text language for better processing
4. **Custom Models**: Fine-tune models for specific complaint types
5. **Caching**: Implement result caching for frequently processed images

## Testing

Run the included test script to verify functionality:
```bash
python test_ocr.py
```

This will test all endpoints and provide a comprehensive status report.