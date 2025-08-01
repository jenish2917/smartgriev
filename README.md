# SmartGriev - Intelligent Grievance Management System

SmartGriev is an AI-powered grievance management system designed to streamline the process of handling public complaints and grievances in multiple Indian languages. The system uses advanced machine learning models for sentiment analysis, complaint classification, and named entity recognition to automate and enhance the grievance redressal process.

## Features

### 1. Multi-Language Support
- Process complaints in multiple Indian languages
- Automatic language detection
- Standardized processing regardless of input language

### 2. AI-Powered Analysis
- **Sentiment Analysis**: Automatically detect the urgency and sentiment of complaints
- **Smart Classification**: Categorize complaints into appropriate departments
- **Named Entity Recognition**: Extract important information like locations, dates, and concerned authorities

### 3. User Interface
- **Frontend**: Modern React-based dashboard
- **Mobile Responsive**: Accessible on all devices
- **Real-time Updates**: Track complaint status live

### 4. Backend Systems
- **Django REST API**: Robust and scalable backend
- **ML Pipeline**: Automated model training and updating
- **Secure Authentication**: JWT-based authentication system

## Tech Stack

### Frontend
- React.js with TypeScript
- TailwindCSS for styling
- Redux for state management
- Vite for build tooling

### Backend
- Django REST Framework
- PostgreSQL Database
- Celery for async tasks
- Redis for caching

### ML Components
- TensorFlow/Keras for deep learning models
- Hugging Face Transformers for NLP
- spaCy for text processing
- Scikit-learn for ML pipelines

### DevOps
- Docker containerization
- GitHub Actions for CI/CD
- AWS/Azure cloud deployment
- Nginx for reverse proxy

## Project Structure
```
SmartGriev/
├── backend/                 # Django backend
│   ├── mlmodels/           # Machine learning models
│   ├── api/                # REST API endpoints
│   └── core/               # Core Django settings
├── frontend/               # React frontend
│   ├── src/               
│   │   ├── components/    # React components
│   │   ├── pages/        # Page layouts
│   │   └── services/     # API services
│   └── public/            # Static files
└── docs/                  # Documentation
```

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL
- Redis

### Backend Setup
1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\\Scripts\\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Setup database:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

### Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

### Training ML Models
1. Navigate to ML models directory:
   ```bash
   cd backend/mlmodels
   ```

2. Run training notebook:
   ```bash
   jupyter notebook train_models.ipynb
   ```

## API Documentation

### Authentication
- JWT-based authentication
- Endpoints protected with token verification
- Role-based access control

### Main Endpoints
- `POST /api/complaints/` - Submit new complaint
- `GET /api/complaints/` - List all complaints
- `GET /api/complaints/{id}/` - Get complaint details
- `PUT /api/complaints/{id}/` - Update complaint status
- `POST /api/analyze/` - Analyze complaint text

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ML Model Details

### 1. Sentiment Analysis Model
- Based on multilingual DeBERTa
- Fine-tuned on grievance data
- Supports multiple Indian languages
- Accuracy metrics available in `model_metrics.md`

### 2. Classification Model
- Hierarchical classification system
- Department and sub-department categorization
- Regular retraining with new data

### 3. NER Model
- Custom BiLSTM-CRF architecture
- Extracts locations, dates, names, and organizations
- Optimized for Indian context

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Municipal Corporations for providing training data
- Open source NLP community
- Government portals for API access# smartgriev
