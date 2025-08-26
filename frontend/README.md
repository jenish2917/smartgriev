# SmartGriev Frontend

A modern React.js frontend application for the SmartGriev Enterprise Grievance Management Platform.

## 🚀 Features

### Core Functionality
- **User Authentication** - Login, registration, profile management
- **Complaint Management** - Create, view, update, and track complaints
- **Real-time Dashboard** - Live analytics and metrics
- **AI Chatbot Integration** - Conversational AI assistant
- **Analytics & Reports** - Data visualization and insights
- **Geospatial Features** - Maps, location tracking, and clustering
- **Real-time Updates** - WebSocket integration for live data

### Technical Features
- **Modern Stack** - React 18, TypeScript, Vite
- **State Management** - Redux Toolkit with React Query
- **UI Framework** - Ant Design with custom styling
- **Real-time Communication** - Socket.io WebSocket integration
- **Charts & Visualizations** - Recharts for data visualization
- **Maps Integration** - Leaflet for geospatial features
- **Responsive Design** - Mobile-first responsive UI
- **Type Safety** - Full TypeScript implementation

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── layout/       # Layout components
│   │   ├── common/       # Common UI components
│   │   └── forms/        # Form components
│   ├── pages/            # Page components
│   │   ├── auth/         # Authentication pages
│   │   ├── complaints/   # Complaint management pages
│   │   └── ...          # Other pages
│   ├── services/         # API service layer
│   │   ├── api.ts        # Base API configuration
│   │   ├── authService.ts
│   │   ├── complaintService.ts
│   │   ├── analyticsService.ts
│   │   ├── chatbotService.ts
│   │   ├── geospatialService.ts
│   │   └── websocketService.ts
│   ├── store/            # Redux store configuration
│   │   ├── index.ts      # Store setup
│   │   └── slices/       # Redux slices
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Utility functions
│   ├── types/            # TypeScript type definitions
│   └── assets/           # Images, icons, etc.
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on localhost:8000

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Environment Configuration**
   Create a `.env` file in the frontend root:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api
   VITE_WS_URL=ws://localhost:8000
   VITE_APP_NAME=SmartGriev
   VITE_APP_VERSION=1.0.0
   ```

4. **Start development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Access the application**
   Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

### Code Structure

#### Services Layer
All API interactions are handled through service functions:

```typescript
// Example: Using the complaint service
import { complaintService } from '@/services/complaintService';

const complaints = await complaintService.getComplaints({
  status: 'pending',
  page: 1,
  page_size: 10
});
```

#### State Management
Redux Toolkit is used for global state management:

```typescript
// Using Redux state
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store';

const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);
```

#### Real-time Updates
WebSocket integration for live data:

```typescript
// Using WebSocket service
import { useWebSocket } from '@/services/websocketService';

const ws = useWebSocket();
ws.on('dashboard_update', (data) => {
  // Handle real-time dashboard updates
});
```

### Key Components

#### Layout Components
- `AppLayout` - Main application layout with sidebar and header
- `AuthLayout` - Authentication pages layout

#### Page Components
- `Dashboard` - Main dashboard with analytics
- `Complaints` - Complaint management interface
- `Chatbot` - AI assistant interface
- `Analytics` - Advanced analytics and reports

### API Integration

The frontend integrates with the Django REST API backend:

#### Authentication
- JWT token-based authentication
- Automatic token refresh
- Protected route handling

#### Real-time Features
- WebSocket connections for live updates
- Dashboard metrics streaming
- Notification system
- Chat interface

#### Data Visualization
- Interactive charts using Recharts
- Geospatial maps with Leaflet
- Real-time metric displays

## 🎨 UI/UX Features

### Design System
- Ant Design component library
- Custom CSS styles and themes
- Responsive grid system
- Consistent color palette and typography

### User Experience
- Intuitive navigation with sidebar menu
- Breadcrumb navigation
- Loading states and error handling
- Form validation and feedback
- Mobile-responsive design

### Accessibility
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- High contrast support

## 🔄 State Management

### Redux Slices
- `authSlice` - User authentication state
- `complaintSlice` - Complaint data management
- `dashboardSlice` - Dashboard metrics and data
- `chatbotSlice` - Chatbot conversation state
- `notificationSlice` - Notification management
- `uiSlice` - UI state (sidebar, theme, modals)

### React Query
Used for server state management:
- Automatic caching and synchronization
- Background refetching
- Optimistic updates
- Error handling

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

Key responsive features:
- Collapsible sidebar on mobile
- Responsive grid layouts
- Touch-friendly interface
- Optimized for mobile browsers

## 🔧 Configuration

### Environment Variables
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
VITE_APP_NAME=SmartGriev
VITE_APP_VERSION=1.0.0
VITE_ENABLE_DEVTOOLS=true
```

### Build Configuration
Vite configuration includes:
- TypeScript support
- Path aliases (@components, @services, etc.)
- Hot module replacement
- Optimized production builds
- Code splitting

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Docker Deployment
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment-specific Builds
- Development: Hot reloading, source maps
- Staging: Optimized build with debug info
- Production: Minified, optimized, no debug info

## 🧪 Testing

### Unit Testing
```bash
npm run test
```

### E2E Testing
```bash
npm run test:e2e
```

### Test Coverage
```bash
npm run test:coverage
```

## 📚 API Integration

### Endpoints
- Authentication: `/api/auth/`
- Complaints: `/api/complaints/`
- Analytics: `/api/analytics/`
- Chatbot: `/api/chatbot/`
- Geospatial: `/api/geospatial/`
- Notifications: `/api/notifications/`

### WebSocket Events
- `dashboard_update` - Real-time dashboard data
- `complaint_update` - Complaint status changes
- `notification` - New notifications
- `metric_update` - Live metric updates
- `alert` - System alerts

## 🔍 Monitoring

### Development Tools
- Redux DevTools integration
- React DevTools support
- Console logging for API calls
- Error boundary implementation

### Production Monitoring
- Error tracking integration ready
- Performance monitoring hooks
- User analytics integration points
- Custom event tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript best practices
- Use React functional components with hooks
- Implement proper error handling
- Write meaningful commit messages
- Add appropriate TypeScript types
- Follow the established code style

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**SmartGriev Frontend** - Transforming grievance management with modern web technology.
