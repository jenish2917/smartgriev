# SmartGriev Frontend Rebuild - Comprehensive Plan

**Date Created**: November 11, 2025  
**Status**: Planning Phase  
**Branch**: `frontend-rebuild` (to be created)  
**Approval Required**: Yes - deployment to staging for user approval before merging

---

## 📋 Table of Contents
1. [Executive Summary](#executive-summary)
2. [Project Analysis](#project-analysis)
3. [Technology Stack Decision](#technology-stack-decision)
4. [Design System](#design-system)
5. [Architecture](#architecture)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Quality Standards](#quality-standards)
8. [Approval Process](#approval-process)

---

## 1. Executive Summary

### Current State
- **Existing Frontend**: React 18.2 + TypeScript + Vite + Ant Design
- **Issues**: Complex codebase, mixed patterns, E2E test failures, performance concerns
- **Tech Debt**: High coupling, inconsistent state management, large bundle size

### Proposed Solution
- **Complete Rebuild**: Modern, scalable architecture from scratch
- **Focus Areas**: Performance, Accessibility, Maintainability, User Experience
- **Timeline**: 24 structured phases (estimated 4-6 weeks for complete implementation)
- **Risk Mitigation**: Separate branch, staged approval, comprehensive testing

---

## 2. Project Analysis

### 2.1 Core Requirements (from README & MERGED_IMPLEMENTATION_STRATEGY)

#### **Functional Requirements**
1. **Multi-Language Support (12 Languages)**
   - English, Hindi, Bengali, Telugu, Marathi, Tamil, Gujarati, Kannada, Malayalam, Punjabi, Urdu (RTL), Odia
   - Native script rendering (Devanagari, Bengali, Telugu, Tamil, etc.)
   - Real-time translation via backend API
   - Persist user language preference

2. **Authentication System**
   - User registration with email + mobile
   - Email verification (auto-link + manual 6-digit code)
   - Mobile OTP verification (SMS-based with 60s cooldown)
   - Password reset flow (email-based token)
   - JWT authentication with refresh tokens
   - Profile management (update name, address, language, mobile)

3. **Complaint Management**
   - **22-Field Complaint Form**:
     - Basic: Title, Description, Category, Department
     - Location: GPS coordinates, address, landmark, Plus Code, area type
     - Details: Urgency level, submitted language, location method
     - Multimodal: Audio file, image file
   - Dynamic categories/departments (fetch from API)
   - GPS location capture ("Get Current Location" button)
   - Multimodal input (voice recording, image upload)
   - Status tracking (pending, in-progress, resolved, closed)
   - Complaint list with filters, pagination, search
   - Detailed complaint view with timeline

4. **AI Chatbot**
   - Natural language conversation
   - Multi-language support
   - Intent detection (greeting, complaint, status check, help)
   - Smart entity extraction (locations, dates)
   - Quick reply suggestions
   - Conversation history

5. **Dashboard & Analytics**
   - User dashboard (my complaints, statistics)
   - Complaint trends (charts/graphs)
   - Status distribution
   - Category breakdown
   - Date range filters

#### **Non-Functional Requirements**
1. **Performance**
   - Lighthouse score: 90+ (Performance, Accessibility, Best Practices, SEO)
   - First Contentful Paint (FCP): < 1.5s
   - Time to Interactive (TTI): < 3.5s
   - Bundle size: < 300KB (gzipped)
   - Code splitting for routes

2. **Accessibility**
   - WCAG 2.1 Level AA compliance
   - Keyboard navigation (Tab, Enter, Escape, Arrow keys)
   - Screen reader support (ARIA labels, roles, live regions)
   - Focus management (visible focus indicators)
   - Color contrast ratios: 4.5:1 (normal text), 3:1 (large text)
   - Skip navigation links

3. **Browser Support**
   - Chrome/Edge (latest 2 versions)
   - Firefox (latest 2 versions)
   - Safari (latest 2 versions)
   - Mobile browsers (iOS Safari, Chrome Android)
   - Progressive enhancement for older browsers

4. **Security**
   - XSS prevention (sanitize user inputs)
   - CSRF protection (tokens in API requests)
   - Secure storage (JWT in httpOnly cookies or secure localStorage)
   - Content Security Policy (CSP) headers
   - Input validation (client + server-side)

### 2.2 Backend API Analysis

#### **Available Endpoints** (from api.config.ts)
```typescript
// Authentication
POST   /api/auth/register/                    // User registration
POST   /api/auth/login/                       // JWT login
POST   /api/auth/logout/                      // Logout
GET    /api/auth/user/                        // Get user profile
PUT    /api/auth/user/                        // Update profile
PUT    /api/auth/language/                    // Update language preference
POST   /api/auth/verify-email/                // Email verification
POST   /api/auth/verify-mobile/               // Mobile OTP verification
POST   /api/auth/resend-email-verification/   // Resend email code
POST   /api/auth/resend-mobile-otp/           // Resend mobile OTP
POST   /api/auth/password-reset/              // Request password reset
POST   /api/auth/password-reset/confirm/      // Confirm password reset
POST   /api/auth/2fa/                         // Two-factor authentication

// Complaints
GET    /api/complaints/                       // List complaints (paginated)
POST   /api/complaints/                       // Create complaint
GET    /api/complaints/{id}/                  // Get complaint details
PUT    /api/complaints/{id}/                  // Update complaint
DELETE /api/complaints/{id}/                  // Delete complaint
GET    /api/complaints/stats/                 // Complaint statistics
GET    /api/complaints/categories/            // List categories
GET    /api/complaints/departments-list/      // List departments

// Chatbot
POST   /api/chatbot/message/                  // Send message
GET    /api/chatbot/history/                  // Conversation history
POST   /api/chatbot/translate/                // Translate text

// Machine Learning
POST   /api/ml/classify/                      // Classify complaint
POST   /api/ml/ocr/                           // Extract text from image
GET    /api/ml/models/                        // List ML models
POST   /api/ml/predict/                       // Make prediction
```

#### **Data Models** (inferred from API)
```typescript
interface User {
  id: number;
  email: string;
  mobile: string;
  firstName: string;
  lastName: string;
  address?: string;
  language: string; // 'en', 'hi', 'bn', 'te', 'mr', 'ta', 'gu', 'kn', 'ml', 'pa', 'ur', 'or'
  isEmailVerified: boolean;
  isMobileVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

interface Complaint {
  id: number;
  userId: number;
  title: string;
  description: string;
  category: string;
  department: string;
  urgencyLevel: 'Low' | 'Medium' | 'High' | 'Critical';
  submittedLanguage: string;
  status: 'pending' | 'in-progress' | 'resolved' | 'closed';
  incidentLatitude?: number;
  incidentLongitude?: number;
  incidentAddress?: string;
  incidentLandmark?: string;
  plusCode?: string;
  areaType?: 'road' | 'park' | 'building' | 'water-body' | 'public-space' | 'residential' | 'commercial';
  gpsAccuracy?: number;
  locationMethod?: 'gps' | 'manual' | 'map';
  audioFile?: string; // URL
  imageFile?: string; // URL
  createdAt: string;
  updatedAt: string;
  resolvedAt?: string;
}

interface Category {
  id: number;
  name: string;
  description: string;
}

interface Department {
  id: number;
  name: string;
  zone: string;
  contactEmail: string;
}

interface ChatMessage {
  id: number;
  userId: number;
  message: string;
  response: string;
  intent: string;
  timestamp: string;
}
```

---

## 3. Technology Stack Decision

### 3.1 Framework & Build Tool
**Selected: React 18.2 + Vite 5.x**

**Rationale:**
- React: Industry standard, large ecosystem, excellent TypeScript support
- Vite: Lightning-fast HMR, optimized builds, native ESM
- Alternatives considered: Next.js (overkill for this SPA), Vue/Svelte (team familiarity)

### 3.2 Type System
**Selected: TypeScript 5.3+ (Strict Mode)**

**Configuration:**
```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### 3.3 UI Component Library
**Selected: shadcn/ui + Radix UI**

**Rationale:**
- **Pros**: Copy-paste components (no npm bloat), full customization, accessible (Radix primitives), Tailwind CSS integration
- **Cons**: Need to manually add components (mitigated by CLI)
- **Alternatives considered**:
  - Ant Design: Too opinionated, large bundle, hard to customize
  - Chakra UI: Good but heavier than shadcn
  - Material UI: Too Google-specific design language

### 3.4 Styling Solution
**Selected: Tailwind CSS 3.4+ + CSS Variables**

**Rationale:**
- Utility-first approach (fast development)
- Purge unused CSS (small bundle)
- Design tokens via CSS variables (theme switching)
- JIT mode (on-demand class generation)

### 3.5 State Management
**Selected: Zustand 4.x + React Query (TanStack Query) 5.x**

**Rationale:**
- **Zustand**: Lightweight (1KB), simple API, no boilerplate, TypeScript-first
- **React Query**: Server state management, caching, auto-refetch, optimistic updates
- **Avoid Redux**: Too much boilerplate for this project size

### 3.6 Form Management
**Selected: React Hook Form 7.x + Zod 3.x**

**Rationale:**
- React Hook Form: Uncontrolled inputs (performance), small bundle, easy validation
- Zod: TypeScript-first schema validation, type inference, composable schemas
- **Alternatives**: Formik (larger, slower), Yup (not TypeScript-first)

### 3.7 Internationalization (i18n)
**Selected: react-i18next 14.x + i18next 23.x**

**Rationale:**
- De facto standard for React i18n
- Lazy loading translations (per-route)
- Pluralization, interpolation, formatting
- RTL support (for Urdu)
- Backend integration (load translations from API)

### 3.8 Routing
**Selected: React Router 6.x**

**Rationale:**
- Nested routes, loaders, actions
- Type-safe routes (with TypeScript)
- Lazy loading support
- SSR-ready (future-proof)

### 3.9 HTTP Client
**Selected: Axios 1.x (wrapped in custom API client)**

**Rationale:**
- Interceptors (auth token, error handling)
- Request/response transformation
- Timeout handling
- Cancel requests (AbortController)
- Better TypeScript support than fetch

### 3.10 Testing
**Selected: Vitest 1.x + Testing Library + Playwright 1.40**

**Rationale:**
- **Vitest**: Vite-native, fast, ESM support, compatible with Jest API
- **Testing Library**: Best practices (test user behavior, not implementation)
- **Playwright**: Already in use, cross-browser E2E testing

### 3.11 Code Quality
**Selected: ESLint 9.x + Prettier 3.x + Husky 9.x + lint-staged**

**Rules:**
- ESLint: `eslint-config-airbnb-typescript`, `@typescript-eslint/recommended-type-checked`
- Prettier: Single quotes, 2 spaces, trailing commas
- Husky: Pre-commit hooks (lint, type-check, format)
- lint-staged: Only lint changed files

---

## 4. Design System

### 4.1 Color Palette

#### **Rationale for Civic Tech Colors**
- **Trust & Authority**: Blues/Teals (government, reliability)
- **Urgency & Action**: Oranges/Reds (alerts, critical issues)
- **Success & Resolution**: Greens (resolved complaints, positive feedback)
- **Neutrals**: Grays (text, backgrounds, borders)

#### **Primary Colors**
```css
:root {
  /* Primary (Trust/Government) - Blue-Teal */
  --color-primary-50: #e6f7f7;
  --color-primary-100: #b3e7e6;
  --color-primary-200: #80d6d5;
  --color-primary-300: #4dc5c3;
  --color-primary-400: #1ab4b2;
  --color-primary-500: #0095a0; /* Main brand color */
  --color-primary-600: #007882;
  --color-primary-700: #005a63;
  --color-primary-800: #003d45;
  --color-primary-900: #002026;

  /* Secondary (Action/Urgency) - Orange */
  --color-secondary-50: #fff4e6;
  --color-secondary-100: #ffe0b3;
  --color-secondary-200: #ffcc80;
  --color-secondary-300: #ffb84d;
  --color-secondary-400: #ffa41a;
  --color-secondary-500: #ff9000; /* Call-to-action */
  --color-secondary-600: #cc7300;
  --color-secondary-700: #995600;
  --color-secondary-800: #663a00;
  --color-secondary-900: #331d00;

  /* Success - Green */
  --color-success-50: #e8f5e9;
  --color-success-100: #c8e6c9;
  --color-success-200: #a5d6a7;
  --color-success-300: #81c784;
  --color-success-400: #66bb6a;
  --color-success-500: #4caf50; /* Resolved state */
  --color-success-600: #43a047;
  --color-success-700: #388e3c;
  --color-success-800: #2e7d32;
  --color-success-900: #1b5e20;

  /* Warning - Yellow */
  --color-warning-50: #fffde7;
  --color-warning-100: #fff9c4;
  --color-warning-200: #fff59d;
  --color-warning-300: #fff176;
  --color-warning-400: #ffee58;
  --color-warning-500: #ffeb3b; /* Medium urgency */
  --color-warning-600: #fdd835;
  --color-warning-700: #fbc02d;
  --color-warning-800: #f9a825;
  --color-warning-900: #f57f17;

  /* Error/Danger - Red */
  --color-error-50: #ffebee;
  --color-error-100: #ffcdd2;
  --color-error-200: #ef9a9a;
  --color-error-300: #e57373;
  --color-error-400: #ef5350;
  --color-error-500: #f44336; /* Critical urgency */
  --color-error-600: #e53935;
  --color-error-700: #d32f2f;
  --color-error-800: #c62828;
  --color-error-900: #b71c1c;

  /* Neutrals - Gray */
  --color-gray-50: #fafafa;
  --color-gray-100: #f5f5f5;
  --color-gray-200: #eeeeee;
  --color-gray-300: #e0e0e0;
  --color-gray-400: #bdbdbd;
  --color-gray-500: #9e9e9e;
  --color-gray-600: #757575;
  --color-gray-700: #616161;
  --color-gray-800: #424242;
  --color-gray-900: #212121;
}
```

#### **Dark Mode Colors**
```css
[data-theme="dark"] {
  --color-bg-primary: #0a0f1e;
  --color-bg-secondary: #151b2e;
  --color-text-primary: #e6e8f0;
  --color-text-secondary: #a0a6b8;
  --color-border: #2a3244;
  
  /* Adjust primary/secondary for dark backgrounds */
  --color-primary-500: #26c6da;
  --color-secondary-500: #ffb74d;
}
```

### 4.2 Typography Scale

```css
:root {
  /* Font Families */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* Font Sizes (Fluid Typography) */
  --text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);      /* 12-14px */
  --text-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);        /* 14-16px */
  --text-base: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);      /* 16-18px */
  --text-lg: clamp(1.125rem, 1.05rem + 0.375vw, 1.25rem);    /* 18-20px */
  --text-xl: clamp(1.25rem, 1.15rem + 0.5vw, 1.5rem);        /* 20-24px */
  --text-2xl: clamp(1.5rem, 1.35rem + 0.75vw, 1.875rem);     /* 24-30px */
  --text-3xl: clamp(1.875rem, 1.65rem + 1.125vw, 2.25rem);   /* 30-36px */
  --text-4xl: clamp(2.25rem, 1.95rem + 1.5vw, 3rem);         /* 36-48px */
  
  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* Line Heights */
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;
  
  /* Letter Spacing */
  --tracking-tighter: -0.05em;
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
}
```

### 4.3 Spacing Scale (8pt Grid)

```css
:root {
  --space-0: 0;
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
}
```

### 4.4 Border Radius

```css
:root {
  --radius-none: 0;
  --radius-sm: 0.125rem;    /* 2px */
  --radius-base: 0.25rem;   /* 4px */
  --radius-md: 0.375rem;    /* 6px */
  --radius-lg: 0.5rem;      /* 8px */
  --radius-xl: 0.75rem;     /* 12px */
  --radius-2xl: 1rem;       /* 16px */
  --radius-full: 9999px;    /* Fully rounded */
}
```

### 4.5 Shadows

```css
:root {
  --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
  --shadow-base: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  --shadow-2xl: 0 30px 60px -15px rgba(0, 0, 0, 0.3);
  --shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05);
}
```

### 4.6 Breakpoints (Mobile-First)

```css
/* Mobile-first approach */
@media (min-width: 640px)  { /* sm - Small tablets */ }
@media (min-width: 768px)  { /* md - Tablets */ }
@media (min-width: 1024px) { /* lg - Laptops */ }
@media (min-width: 1280px) { /* xl - Desktops */ }
@media (min-width: 1536px) { /* 2xl - Large desktops */ }
```

---

## 5. Architecture

### 5.1 Folder Structure

```
frontend-new/
├── public/
│   ├── locales/                    # i18n translation files
│   │   ├── en/
│   │   │   ├── common.json
│   │   │   ├── auth.json
│   │   │   ├── complaints.json
│   │   │   └── dashboard.json
│   │   ├── hi/
│   │   ├── bn/
│   │   └── ... (10 more languages)
│   ├── fonts/                      # Inter, Noto Sans (multi-script support)
│   └── favicon.ico
│
├── src/
│   ├── api/                        # API client & endpoints
│   │   ├── client.ts               # Axios instance with interceptors
│   │   ├── endpoints/
│   │   │   ├── auth.ts
│   │   │   ├── complaints.ts
│   │   │   ├── chatbot.ts
│   │   │   └── ml.ts
│   │   └── types/                  # API response/request types
│   │       ├── auth.types.ts
│   │       ├── complaint.types.ts
│   │       └── common.types.ts
│   │
│   ├── assets/                     # Static assets
│   │   ├── icons/
│   │   ├── images/
│   │   └── animations/             # Lottie JSON files
│   │
│   ├── components/                 # React components (Atomic Design)
│   │   ├── atoms/                  # Basic building blocks
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.test.tsx
│   │   │   │   └── Button.stories.tsx (optional Storybook)
│   │   │   ├── Input/
│   │   │   ├── Select/
│   │   │   ├── Checkbox/
│   │   │   ├── Badge/
│   │   │   ├── Avatar/
│   │   │   └── Spinner/
│   │   │
│   │   ├── molecules/              # Composite components
│   │   │   ├── FormField/          # Label + Input + Error
│   │   │   ├── Card/
│   │   │   ├── SearchBar/
│   │   │   ├── LanguageSelector/
│   │   │   ├── LocationPicker/
│   │   │   └── FileUploader/
│   │   │
│   │   ├── organisms/              # Complex components
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   ├── ComplaintForm/
│   │   │   ├── ChatWindow/
│   │   │   ├── ComplaintCard/
│   │   │   └── StatisticsChart/
│   │   │
│   │   ├── templates/              # Page layouts
│   │   │   ├── AuthLayout/
│   │   │   ├── DashboardLayout/
│   │   │   └── PublicLayout/
│   │   │
│   │   └── providers/              # Context providers
│   │       ├── ThemeProvider.tsx
│   │       ├── AuthProvider.tsx
│   │       ├── I18nProvider.tsx
│   │       └── QueryProvider.tsx
│   │
│   ├── hooks/                      # Custom React hooks
│   │   ├── useAuth.ts              # Authentication hook
│   │   ├── useLocalStorage.ts
│   │   ├── useDebounce.ts
│   │   ├── useMediaQuery.ts
│   │   ├── useGeolocation.ts
│   │   ├── useVoiceRecognition.ts
│   │   └── useTranslation.ts       # Wrapper for react-i18next
│   │
│   ├── lib/                        # Utility libraries
│   │   ├── axios.ts                # Axios configuration
│   │   ├── i18n.ts                 # i18next configuration
│   │   ├── queryClient.ts          # React Query client
│   │   └── utils.ts                # Helper functions (cn, formatDate, etc.)
│   │
│   ├── pages/                      # Route pages
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── ForgotPasswordPage.tsx
│   │   │   ├── EmailVerificationPage.tsx
│   │   │   ├── MobileVerificationPage.tsx
│   │   │   └── PasswordResetConfirmPage.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ComplaintsListPage.tsx
│   │   │   ├── ComplaintDetailPage.tsx
│   │   │   ├── CreateComplaintPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   ├── SettingsPage.tsx
│   │   │   └── AnalyticsPage.tsx
│   │   │
│   │   ├── chatbot/
│   │   │   └── ChatbotPage.tsx
│   │   │
│   │   ├── public/
│   │   │   ├── HomePage.tsx
│   │   │   ├── AboutPage.tsx
│   │   │   └── ContactPage.tsx
│   │   │
│   │   └── error/
│   │       ├── NotFoundPage.tsx
│   │       └── ErrorPage.tsx
│   │
│   ├── routes/                     # Routing configuration
│   │   ├── index.tsx               # Main router
│   │   ├── ProtectedRoute.tsx      # Auth guard
│   │   └── PublicRoute.tsx
│   │
│   ├── store/                      # Zustand stores
│   │   ├── authStore.ts            # Auth state (user, tokens)
│   │   ├── themeStore.ts           # Theme (light/dark)
│   │   ├── languageStore.ts        # Language preference
│   │   └── chatStore.ts            # Chat history
│   │
│   ├── styles/                     # Global styles
│   │   ├── index.css               # Tailwind imports + global styles
│   │   ├── variables.css           # CSS custom properties
│   │   └── fonts.css               # Font-face declarations
│   │
│   ├── types/                      # TypeScript types
│   │   ├── index.ts                # Barrel export
│   │   ├── api.types.ts
│   │   ├── form.types.ts
│   │   └── common.types.ts
│   │
│   ├── utils/                      # Utility functions
│   │   ├── cn.ts                   # Classname merger (clsx + tailwind-merge)
│   │   ├── date.ts                 # Date formatting
│   │   ├── validation.ts           # Zod schemas
│   │   ├── storage.ts              # localStorage wrapper
│   │   └── constants.ts            # App constants
│   │
│   ├── App.tsx                     # Root component
│   ├── main.tsx                    # Entry point
│   └── vite-env.d.ts               # Vite types
│
├── tests/                          # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/                        # Playwright tests (adapt existing)
│
├── .env.example                    # Environment variables template
├── .eslintrc.cjs                   # ESLint config
├── .prettierrc                     # Prettier config
├── components.json                 # shadcn/ui config
├── index.html
├── package.json
├── postcss.config.js               # PostCSS for Tailwind
├── tailwind.config.ts              # Tailwind configuration
├── tsconfig.json                   # TypeScript config
├── tsconfig.node.json
├── vite.config.ts                  # Vite config
└── vitest.config.ts                # Vitest config
```

### 5.2 State Management Strategy

#### **Client State (Zustand)**
- User authentication (user object, tokens, isAuthenticated)
- UI state (theme, sidebar open/closed, modals)
- Language preference
- Local chat history (temporary)

#### **Server State (React Query)**
- Complaints list (with pagination, filters)
- Complaint details
- Categories/departments (cached)
- User profile
- Chatbot conversation history
- Statistics/analytics data

#### **Form State (React Hook Form)**
- All form inputs (uncontrolled for performance)
- Validation errors
- Submission status

### 5.3 Data Flow

```
User Action → Component → Hook → API Client → Backend
                ↓
            React Query (cache)
                ↓
            Component Re-render
```

**Example: Login Flow**
1. User submits login form
2. `LoginPage` calls `useLogin` hook (React Query mutation)
3. Hook calls `authApi.login()` (Axios)
4. Success: Store JWT in `authStore` (Zustand), redirect to dashboard
5. Fail: Display error message via toast

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Week 1)
✅ **Days 1-2: Project Setup**
- [ ] Create `frontend-rebuild` branch
- [ ] Delete existing frontend
- [ ] Initialize Vite + React + TypeScript
- [ ] Configure ESLint, Prettier, Husky
- [ ] Setup folder structure
- [ ] Configure path aliases
- [ ] Install core dependencies

✅ **Days 3-4: Design System**
- [ ] Create CSS variables (colors, typography, spacing)
- [ ] Setup Tailwind CSS with custom theme
- [ ] Configure shadcn/ui
- [ ] Create `cn()` utility (class name merger)
- [ ] Test theme switching (light/dark)

✅ **Days 5-7: Core Infrastructure**
- [ ] Setup Axios client with interceptors
- [ ] Create API endpoint modules
- [ ] Setup React Query with devtools
- [ ] Setup Zustand stores (auth, theme, language)
- [ ] Create error boundary component
- [ ] Setup toast notification system

### Phase 2: Atoms & Molecules (Week 2)
✅ **Days 1-3: Atomic Components**
- [ ] Button (variants: primary, secondary, ghost, danger, loading states)
- [ ] Input (text, email, password, number, show/hide password)
- [ ] Select (single, multi-select with search)
- [ ] Checkbox, Radio, Switch
- [ ] TextArea (with character counter)
- [ ] Label, Badge, Avatar, Spinner
- [ ] Write unit tests for each component

✅ **Days 4-5: Molecular Components**
- [ ] FormField (Label + Input + Error message)
- [ ] Card (header, body, footer slots)
- [ ] SearchBar (with debounce)
- [ ] Dropdown, Tooltip, Modal
- [ ] Alert (success, error, warning, info)
- [ ] Write integration tests

✅ **Days 6-7: Complex Molecules**
- [ ] LanguageSelector (12 languages, flags, native names)
- [ ] LocationPicker (GPS button, manual input, map integration)
- [ ] FileUploader (drag-drop, image preview, audio player)
- [ ] DatePicker, TimePicker
- [ ] Pagination component

### Phase 3: Authentication (Week 2-3)
✅ **Days 1-2: Auth Pages - Part 1**
- [ ] LoginPage (email/password, remember me, forgot password link)
- [ ] RegisterPage (12-language selector, address, terms checkbox)
- [ ] Form validation with Zod schemas
- [ ] Password strength indicator

✅ **Days 3-4: Auth Pages - Part 2**
- [ ] ForgotPasswordPage (email input, send reset link)
- [ ] PasswordResetConfirmPage (token validation, new password, strength)
- [ ] EmailVerificationPage (auto-verify from link, manual code input)
- [ ] MobileVerificationPage (OTP input, resend with cooldown)

✅ **Days 5-7: Auth Logic**
- [ ] Setup authStore (Zustand)
- [ ] Create useAuth hook (login, logout, register, verify)
- [ ] JWT token refresh logic
- [ ] ProtectedRoute component
- [ ] PublicRoute component (redirect if authenticated)
- [ ] Persist auth state (localStorage/sessionStorage)
- [ ] Write E2E tests for auth flows

### Phase 4: Internationalization (Week 3)
✅ **Days 1-2: i18n Setup**
- [ ] Configure i18next + react-i18next
- [ ] Create translation JSON files (12 languages)
- [ ] Translate: common, auth, complaints, dashboard, chatbot
- [ ] Setup lazy loading (load translations per route)

✅ **Days 3-4: RTL Support & Scripts**
- [ ] Configure Urdu RTL support
- [ ] Test native script rendering (Devanagari, Bengali, Telugu, Tamil, etc.)
- [ ] Add font-face for multi-script (Noto Sans, Inter)
- [ ] Language selector component (flags, native names)

✅ **Day 5: Translation Integration**
- [ ] Wrap app in I18nProvider
- [ ] Create useTranslation wrapper hook
- [ ] Test language switching (persist in localStorage)
- [ ] Update language preference API call

### Phase 5: Dashboard & Navigation (Week 3-4)
✅ **Days 1-2: Layouts**
- [ ] AuthLayout (for login/register - centered form)
- [ ] DashboardLayout (sidebar + header + main content)
- [ ] Responsive sidebar (collapse on mobile, hamburger menu)
- [ ] Header with user profile dropdown, notifications bell, language selector

✅ **Days 3-4: Dashboard Page**
- [ ] Stats cards (total complaints, pending, resolved, avg response time)
- [ ] Recent complaints list (table/cards)
- [ ] Quick actions (create complaint, chatbot, view all)
- [ ] Skeleton loading states

✅ **Day 5: Navigation**
- [ ] Setup React Router with nested routes
- [ ] Implement route guards (ProtectedRoute)
- [ ] Breadcrumb component
- [ ] Active link highlighting

### Phase 6: Complaint Form (Week 4)
✅ **Days 1-2: Multi-Step Form - Step 1 (Basic Info)**
- [ ] Title input (max length, validation)
- [ ] Description textarea (rich text editor optional, character counter)
- [ ] Language selector (submitted_language field)
- [ ] Category dropdown (dynamic fetch from API)
- [ ] Department dropdown (filtered by category)
- [ ] Progress indicator (step 1/3)

✅ **Days 3-4: Multi-Step Form - Step 2 (Location)**
- [ ] "Get Current Location" button (Geolocation API)
- [ ] Display GPS coordinates (latitude, longitude, accuracy)
- [ ] Address input (auto-fill from reverse geocoding)
- [ ] Landmark input
- [ ] Plus Code input (optional)
- [ ] Area type selector (7 options: road, park, building, etc.)
- [ ] Location method (auto-detect: gps/manual)
- [ ] Google Maps embed (optional, show pin)

✅ **Days 5-7: Multi-Step Form - Step 3 (Details & Submit)**
- [ ] Urgency level selector (Low, Medium, High, Critical with colors)
- [ ] Image upload (preview, crop, max 5MB)
- [ ] Audio recording button (start/stop, waveform visualization)
- [ ] Terms & conditions checkbox
- [ ] Submit button (loading state)
- [ ] Success modal (with complaint ID, status tracker)
- [ ] Form persistence (save draft to localStorage)

### Phase 7: Complaints Management (Week 5)
✅ **Days 1-3: Complaints List Page**
- [ ] Table/Cards view toggle
- [ ] Filters: Status, Category, Date range, Urgency
- [ ] Search by title/description
- [ ] Sort by date, urgency, status
- [ ] Pagination (React Query infinite scroll optional)
- [ ] Bulk actions (delete, export)
- [ ] Empty state (no complaints yet)

✅ **Days 4-5: Complaint Detail Page**
- [ ] Display all complaint fields
- [ ] Status timeline (created → in-progress → resolved)
- [ ] Image gallery (lightbox)
- [ ] Audio player
- [ ] Location map (if GPS provided)
- [ ] Edit button (only if pending)
- [ ] Delete button (with confirmation)
- [ ] Share button (copy link, social media)

✅ **Days 6-7: Edit Complaint**
- [ ] Pre-fill form with existing data
- [ ] Disable editing if status is resolved/closed
- [ ] Optimistic update (React Query)
- [ ] Validation (same as create form)

### Phase 8: AI Chatbot (Week 5-6)
✅ **Days 1-2: Chat UI**
- [ ] Message bubbles (user vs bot, timestamps)
- [ ] Typing indicator (animated dots)
- [ ] Scroll to bottom on new message
- [ ] Message input (multi-line, shift+enter for newline)
- [ ] Send button (or enter to send)

✅ **Days 3-4: Chat Logic**
- [ ] Send message API call
- [ ] Display bot response (with intent, entities)
- [ ] Quick reply buttons (e.g., "Check status", "File complaint")
- [ ] Language detection (auto-translate)
- [ ] Conversation history (load from API)

✅ **Days 5-7: Voice Input**
- [ ] Microphone button (request permission)
- [ ] Real-time transcription (Web Speech API)
- [ ] Language selection for voice recognition
- [ ] Display transcript in message input
- [ ] Handle unsupported browsers (fallback to text)
- [ ] Visual feedback (recording animation)

### Phase 9: User Profile & Settings (Week 6)
✅ **Days 1-2: Profile Page**
- [ ] Display user info (name, email, mobile, address, language)
- [ ] Edit mode (inline editing)
- [ ] Avatar upload (crop, resize)
- [ ] Verification badges (email, mobile)
- [ ] Save changes (optimistic update)

✅ **Days 3-4: Settings Page**
- [ ] Language preference (dropdown)
- [ ] Theme selector (light, dark, system)
- [ ] Notification preferences (email, SMS, push)
- [ ] Privacy settings (profile visibility)
- [ ] Two-factor authentication toggle

✅ **Day 5: Change Password**
- [ ] Current password input
- [ ] New password input (with strength indicator)
- [ ] Confirm password input
- [ ] Validation (match, strength requirements)
- [ ] Success message

### Phase 10: Analytics & Charts (Week 6-7)
✅ **Days 1-3: Dashboard Charts**
- [ ] Complaint trends (line chart, last 30 days)
- [ ] Status distribution (pie/donut chart)
- [ ] Category breakdown (bar chart)
- [ ] Urgency levels (stacked bar chart)
- [ ] Use recharts or victory library
- [ ] Responsive charts (adjust on mobile)

✅ **Days 4-5: Filters & Export**
- [ ] Date range picker (last 7 days, 30 days, custom)
- [ ] Category filter
- [ ] Export data (CSV, PDF)
- [ ] Print view (printer-friendly)

### Phase 11: Performance & Accessibility (Week 7)
✅ **Days 1-2: Code Splitting**
- [ ] Lazy load routes with React.lazy
- [ ] Suspense with fallback (Spinner)
- [ ] Split vendor bundles (React, ReactDOM, Axios separate)
- [ ] Analyze bundle size (vite-bundle-visualizer)
- [ ] Optimize images (WebP, lazy load with intersection observer)

✅ **Days 3-4: Performance**
- [ ] Lighthouse audit (target 90+)
- [ ] Optimize FCP, LCP, CLS, TTI
- [ ] Service worker for caching (optional PWA)
- [ ] Preload critical resources
- [ ] Minify CSS/JS
- [ ] Compress assets (Brotli/Gzip)

✅ **Days 5-7: Accessibility**
- [ ] Keyboard navigation (Tab, Enter, Escape, Arrow keys)
- [ ] Focus management (visible focus indicators, focus trap in modals)
- [ ] ARIA labels (buttons, inputs, links)
- [ ] ARIA roles (navigation, main, complementary)
- [ ] ARIA live regions (announcements, errors)
- [ ] Screen reader testing (NVDA, JAWS, VoiceOver)
- [ ] Color contrast check (4.5:1 for text)
- [ ] Skip navigation link
- [ ] Semantic HTML (h1-h6 hierarchy, nav, main, aside, footer)

### Phase 12: Testing & QA (Week 7-8)
✅ **Days 1-3: Unit Tests (Vitest)**
- [ ] Test utility functions (date, validation, storage)
- [ ] Test custom hooks (useAuth, useGeolocation, useDebounce)
- [ ] Test Zustand stores (actions, selectors)
- [ ] Target 80%+ coverage

✅ **Days 4-5: Component Tests (Testing Library)**
- [ ] Test atoms (Button, Input, Select)
- [ ] Test molecules (FormField, Card, LanguageSelector)
- [ ] Test organisms (ComplaintForm, ChatWindow)
- [ ] Mock API calls (MSW - Mock Service Worker)
- [ ] Test user interactions (click, type, submit)

✅ **Days 6-7: Integration Tests**
- [ ] Test auth flow (login, register, verify, password reset)
- [ ] Test complaint submission flow
- [ ] Test complaint list filters and pagination
- [ ] Test chatbot conversation

### Phase 13: E2E Tests (Week 8)
✅ **Days 1-3: Adapt Existing Playwright Tests**
- [ ] Update selectors to match new components
- [ ] Test authentication (all 10 tests)
- [ ] Test complaint submission (all tests)
- [ ] Test dashboard navigation

✅ **Days 4-5: Additional E2E Tests**
- [ ] Test chatbot interaction
- [ ] Test voice input (if supported in browser)
- [ ] Test location picker
- [ ] Test analytics page
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)

✅ **Days 6-7: Mobile Testing**
- [ ] Test on mobile viewport (375x667, 414x896)
- [ ] Test touch interactions
- [ ] Test responsive layouts
- [ ] Test mobile-specific features (geolocation prompt)

### Phase 14: Documentation & Deployment (Week 8)
✅ **Days 1-2: Documentation**
- [ ] README.md (setup, run, test, build)
- [ ] ARCHITECTURE.md (folder structure, data flow, design decisions)
- [ ] CONTRIBUTING.md (code style, PR process, testing requirements)
- [ ] API_INTEGRATION.md (how to add new endpoints, error handling)
- [ ] Inline code comments (JSDoc for complex functions)
- [ ] Component documentation (props, examples)

✅ **Days 3-4: Build & Deploy**
- [ ] Production build (`npm run build`)
- [ ] Optimize bundle size (target < 300KB gzipped)
- [ ] Setup environment variables (.env.example)
- [ ] Create Dockerfile (multi-stage build)
- [ ] Setup Nginx config (SPA fallback)
- [ ] Deploy to staging server (Vercel/Netlify/custom)

✅ **Days 5-7: Final QA & Approval**
- [ ] End-to-end manual testing (all features)
- [ ] Cross-browser testing
- [ ] Mobile device testing (Android, iOS)
- [ ] Performance audit (Lighthouse)
- [ ] Accessibility audit (axe DevTools, WAVE)
- [ ] Security audit (OWASP Top 10)
- [ ] Create demo video/screenshots
- [ ] Prepare approval presentation
- [ ] **Request user approval** ⚠️

---

## 7. Quality Standards

### 7.1 Code Quality Metrics

| Metric | Target | Tool |
|--------|--------|------|
| TypeScript Coverage | 100% | `tsc --noEmit` |
| Test Coverage | 80%+ | Vitest |
| Bundle Size (gzipped) | < 300KB | vite-bundle-visualizer |
| Lighthouse Performance | 90+ | Chrome DevTools |
| Lighthouse Accessibility | 95+ | Chrome DevTools |
| Lighthouse Best Practices | 95+ | Chrome DevTools |
| Lighthouse SEO | 90+ | Chrome DevTools |
| ESLint Errors | 0 | ESLint |
| Code Duplication | < 5% | jscpd |

### 7.2 Coding Standards

#### **Naming Conventions**
- **Components**: PascalCase (`LoginPage`, `ComplaintForm`)
- **Hooks**: camelCase with `use` prefix (`useAuth`, `useGeolocation`)
- **Utils/Functions**: camelCase (`formatDate`, `validateEmail`)
- **Constants**: SCREAMING_SNAKE_CASE (`API_BASE_URL`, `MAX_FILE_SIZE`)
- **Types/Interfaces**: PascalCase (`User`, `Complaint`, `ApiResponse`)
- **CSS Classes**: kebab-case or Tailwind utilities

#### **File Naming**
- **Components**: PascalCase matching component name (`Button.tsx`, `LoginPage.tsx`)
- **Hooks**: camelCase (`useAuth.ts`, `useDebounce.ts`)
- **Utils**: camelCase (`date.ts`, `validation.ts`)
- **Types**: PascalCase or descriptive (`api.types.ts`, `complaint.types.ts`)

#### **Code Organization**
- **Single Responsibility**: Each function/component does one thing
- **DRY (Don't Repeat Yourself)**: Extract reusable logic into hooks/utils
- **KISS (Keep It Simple, Stupid)**: Avoid over-engineering
- **Composition over Inheritance**: Use hooks and composition for reusability

#### **TypeScript**
- **No `any` types**: Use `unknown` and type guards
- **Strict null checks**: Explicitly handle `null`/`undefined`
- **Type inference**: Let TypeScript infer when obvious
- **Discriminated unions**: For state machines (e.g., API status: idle | loading | success | error)

#### **React Best Practices**
- **Functional components**: No class components
- **Hooks**: Use custom hooks for reusable logic
- **Props destructuring**: Extract props in function signature
- **Avoid inline functions**: Define event handlers outside JSX (except for simple arrow functions)
- **Memoization**: Use `useMemo`/`useCallback` sparingly (profile first)
- **Error boundaries**: Wrap risky components

### 7.3 Accessibility Checklist

- [ ] Semantic HTML (h1-h6, nav, main, aside, footer, article, section)
- [ ] ARIA labels for icon buttons (`aria-label="Close"`)
- [ ] ARIA roles for custom components (`role="dialog"` for modals)
- [ ] ARIA live regions for dynamic content (`aria-live="polite"`)
- [ ] Keyboard navigation (Tab, Shift+Tab, Enter, Escape, Arrow keys)
- [ ] Focus management (auto-focus on modal open, focus trap)
- [ ] Visible focus indicators (`:focus-visible` for keyboard, not mouse)
- [ ] Color contrast (4.5:1 for normal text, 3:1 for large text)
- [ ] Alt text for images
- [ ] Skip navigation link (`<a href="#main-content">Skip to main content</a>`)
- [ ] Form labels (explicit `<label for="...">`)</label>
- [ ] Error messages (associated with inputs via `aria-describedby`)
- [ ] Disabled state (visually distinct, `aria-disabled="true"`)
- [ ] Loading state announcements (`aria-busy="true"`, `aria-live="polite"`)

### 7.4 Performance Checklist

- [ ] Code splitting (lazy load routes)
- [ ] Tree shaking (remove unused code)
- [ ] Image optimization (WebP format, lazy loading)
- [ ] Font optimization (preload, font-display: swap)
- [ ] Minify CSS/JS
- [ ] Compress assets (Brotli/Gzip)
- [ ] Cache static assets (long cache headers)
- [ ] Debounce/throttle event handlers (scroll, resize, input)
- [ ] Virtualize long lists (react-window for 100+ items)
- [ ] Optimize re-renders (React.memo, useMemo, useCallback - use sparingly)
- [ ] Avoid layout thrashing (batch DOM reads/writes)
- [ ] Use Web Workers for heavy computations (optional)

---

## 8. Approval Process

### 8.1 Pre-Approval Checklist

Before requesting user approval, ensure:

- [ ] **All 24 phases completed** (100% feature parity with old frontend)
- [ ] **No console errors** in browser DevTools
- [ ] **No TypeScript errors** (`npm run type-check`)
- [ ] **No ESLint errors** (`npm run lint`)
- [ ] **All tests passing** (unit, integration, E2E)
- [ ] **Test coverage > 80%**
- [ ] **Lighthouse score > 90** (Performance, Accessibility, Best Practices, SEO)
- [ ] **Bundle size < 300KB** (gzipped)
- [ ] **Cross-browser tested** (Chrome, Firefox, Safari, Edge)
- [ ] **Mobile tested** (responsive on 375x667 and 414x896)
- [ ] **Accessibility tested** (keyboard navigation, screen reader)
- [ ] **Documentation complete** (README, ARCHITECTURE, CONTRIBUTING)
- [ ] **Staging deployment successful** (URL accessible)

### 8.2 Approval Deliverables

#### **1. Demo Video (5-10 minutes)**
- Full walkthrough of all features
- Highlight performance improvements
- Show mobile responsiveness
- Demonstrate accessibility features (keyboard nav, screen reader)

#### **2. Feature Comparison Table**
| Feature | Old Frontend | New Frontend | Status |
|---------|--------------|--------------|--------|
| Authentication | ✅ | ✅ | Improved (better UX) |
| Multi-language | ✅ (12 langs) | ✅ (12 langs) | Same |
| Complaint Form | ✅ (22 fields) | ✅ (22 fields) | Enhanced (better validation) |
| GPS Location | ✅ | ✅ | Improved (better UI) |
| Voice Input | ✅ | ✅ | Same |
| Chatbot | ✅ | ✅ | Improved (better UX) |
| Dashboard | ✅ | ✅ | Enhanced (more charts) |
| Analytics | ⚠️ (basic) | ✅ (advanced) | New feature |
| Dark Mode | ❌ | ✅ | New feature |
| Accessibility | ⚠️ (partial) | ✅ (WCAG 2.1 AA) | Improved |
| Performance | ⚠️ (slow) | ✅ (90+ Lighthouse) | Improved |
| Bundle Size | ❌ (1.2MB) | ✅ (< 300KB) | Improved |
| Test Coverage | ❌ (< 20%) | ✅ (> 80%) | Improved |

#### **3. Performance Report**
- Lighthouse scores (before vs after)
- Bundle size comparison
- Load time comparison
- Core Web Vitals (FCP, LCP, CLS, TTI)

#### **4. Accessibility Report**
- WCAG 2.1 compliance level (target: AA)
- axe DevTools scan results
- WAVE scan results
- Screen reader testing results

#### **5. Staging URL**
- Public URL for testing (e.g., `https://smartgriev-new.vercel.app`)
- Credentials for test account
- Instructions for testing all features

### 8.3 Approval Decision Tree

```
User Reviews Staging → All Good? → Approve → Merge to Main → Deploy Production
                           ↓ No
                      Feedback → Revisions → Re-submit for Approval
```

**If Approved:**
1. Merge `frontend-rebuild` branch into `main`
2. Delete old frontend directory
3. Move new frontend to `frontend/` directory
4. Update root README.md
5. Deploy to production
6. Archive old frontend (optional backup branch)

**If Revisions Needed:**
1. Create list of required changes
2. Implement revisions on `frontend-rebuild` branch
3. Re-test and re-deploy to staging
4. Request re-approval

---

## 9. Risk Mitigation

### 9.1 Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Backend API changes | Low | High | Lock API contracts, version endpoints |
| Browser compatibility issues | Medium | Medium | Test in all browsers early, use polyfills |
| Performance degradation | Low | High | Continuous Lighthouse audits, bundle size monitoring |
| Translation errors | Medium | Medium | Native speaker review, fallback to English |
| Accessibility failures | Medium | High | Automated testing (axe, WAVE), manual testing |
| Scope creep | High | High | Strict adherence to 24-phase plan, no new features |
| Timeline delays | Medium | Medium | Weekly progress tracking, buffer time in Phase 14 |
| User rejection | Low | High | Incremental approval checkpoints, demo videos |

### 9.2 Rollback Plan

If production deployment fails:
1. **Immediate**: Revert to previous frontend (keep backup branch)
2. **Root Cause**: Analyze failure (logs, error reports)
3. **Fix**: Apply hotfix to `frontend-rebuild` branch
4. **Re-deploy**: After testing fix in staging

---

## 10. Success Metrics

### 10.1 Technical Metrics
- [ ] Bundle size reduced by 75% (1.2MB → < 300KB)
- [ ] Lighthouse Performance score > 90 (previously < 70)
- [ ] Lighthouse Accessibility score > 95 (previously < 60)
- [ ] Test coverage > 80% (previously < 20%)
- [ ] 0 TypeScript errors (previously ~50)
- [ ] 0 ESLint errors (previously ~100)
- [ ] Load time < 2s (previously 5-8s)

### 10.2 User Experience Metrics
- [ ] All 12 languages working correctly
- [ ] Complaint submission success rate > 95%
- [ ] Chatbot response time < 1s
- [ ] GPS location capture success rate > 90%
- [ ] Mobile responsiveness on all screen sizes
- [ ] No reported accessibility issues

### 10.3 Business Metrics
- [ ] User complaints submitted: No decrease from old frontend
- [ ] User satisfaction: Positive feedback from approval testing
- [ ] Developer productivity: Faster feature development (cleaner codebase)
- [ ] Maintenance cost: Reduced (better code quality, tests)

---

## 11. Timeline Summary

| Phase | Duration | Tasks | Deliverables |
|-------|----------|-------|--------------|
| 1. Foundation | Week 1 | Setup, Design System, Core Infrastructure | Boilerplate, CSS variables, API client |
| 2. Atoms & Molecules | Week 2 | Basic components | Button, Input, Select, Card, etc. |
| 3. Authentication | Week 2-3 | Auth pages, logic | Login, Register, Verify, Reset |
| 4. i18n | Week 3 | 12 languages, RTL | Translation files, LanguageSelector |
| 5. Dashboard & Nav | Week 3-4 | Layouts, Dashboard | DashboardLayout, DashboardPage |
| 6. Complaint Form | Week 4 | Multi-step form | CreateComplaintPage (3 steps) |
| 7. Complaints Mgmt | Week 5 | List, Detail, Edit | ComplaintsListPage, ComplaintDetailPage |
| 8. Chatbot | Week 5-6 | Chat UI, Voice | ChatbotPage, Voice input |
| 9. Profile & Settings | Week 6 | Profile, Settings | ProfilePage, SettingsPage |
| 10. Analytics | Week 6-7 | Charts, Filters | AnalyticsPage with charts |
| 11. Performance & A11y | Week 7 | Optimization, WCAG | Lighthouse 90+, WCAG AA |
| 12. Testing & QA | Week 7-8 | Unit, Integration | 80%+ coverage |
| 13. E2E Tests | Week 8 | Playwright tests | All tests passing |
| 14. Docs & Deploy | Week 8 | Documentation, Staging | README, Staging URL, Approval |

**Total Estimated Time**: **6-8 weeks** (for one developer, working full-time)

---

## 12. Next Steps

### Immediate Actions
1. **User Approval to Proceed**: Confirm plan and timeline
2. **Create Branch**: `git checkout -b frontend-rebuild`
3. **Delete Old Frontend**: `rm -rf frontend`
4. **Commit**: `git commit -m "chore: remove old frontend for rebuild"`
5. **Initialize New Project**: `npm create vite@latest frontend-new -- --template react-ts`
6. **Start Phase 1**: Foundation setup

### Communication
- **Weekly Updates**: Progress report every Monday
- **Blocker Reporting**: Immediate notification of critical issues
- **Mid-Point Demo**: Show progress after Phase 7 (Week 5)
- **Final Demo**: Full feature walkthrough before approval request

---

## 13. Conclusion

This comprehensive rebuild plan ensures:
- ✅ **Modern Tech Stack**: Latest React, TypeScript, Vite, Tailwind CSS
- ✅ **Best Practices**: Atomic Design, Accessibility, Performance
- ✅ **100% Feature Parity**: All existing features maintained
- ✅ **Enhanced UX**: Improved user experience, faster, more accessible
- ✅ **Maintainability**: Clean code, well-tested, documented
- ✅ **Scalability**: Easy to add new features, modular architecture

**Approval Required**: This plan requires user sign-off before starting implementation. Once approved, development will begin on a separate `frontend-rebuild` branch, with no impact on the current production frontend until final approval and merge.

---

**Document Version**: 1.0  
**Created**: November 11, 2025  
**Author**: AI Assistant (via GitHub Copilot)  
**Status**: Awaiting User Approval ⏳
