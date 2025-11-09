// SmartGriev Unified Design System - Merged Spec
// Based on Trust Blue (#2563EB) & Success Green (#059669)
export const theme = {
  colors: {
    // Primary - Trust Blue (from PDF spec)
    primary: {
      50: '#EFF6FF',
      100: '#DBEAFE',
      200: '#BFDBFE',
      300: '#93C5FD',
      400: '#60A5FA',
      500: '#2563EB',  // Trust Blue - Main Brand Color
      600: '#1D4ED8',
      700: '#1E40AF',
      800: '#1E3A8A',
      900: '#1E3A70',
      950: '#172554',
    },
    // Secondary - Success Green (from PDF spec)
    secondary: {
      50: '#ECFDF5',
      100: '#D1FAE5',
      200: '#A7F3D0',
      300: '#6EE7B7',
      400: '#34D399',
      500: '#059669',  // Success Green - Secondary Brand Color
      600: '#047857',
      700: '#065F46',
      800: '#064E3B',
      900: '#022C22',
    },
    // White & Neutral Colors
    white: {
      pure: '#FFFFFF',
      off: '#FAFAFA',
    },
    black: {
      pure: '#000000',
      soft: '#1A1A1A',
    },
    // Glassmorphism Colors
    glass: {
      light: 'rgba(255, 255, 255, 0.8)',
      medium: 'rgba(255, 255, 255, 0.6)',
      dark: 'rgba(26, 29, 46, 0.8)',
      blur: 'blur(20px)',
    },
    // Futuristic Accent Colors
    futuristic: {
      purple: '#6C63FF',
      cyan: '#4ECDC4',
      pink: '#FF6584',
      yellow: '#FFD93D',
      lime: '#7BE495',
    },
    // Department Color Coding (from PDF spec)
    departments: {
      water: '#0EA5E9',       // Light blue
      electricity: '#F97316', // Orange
      roads: '#6B7280',       // Gray
      sanitation: '#84CC16',  // Lime green
      waste: '#A855F7',       // Purple
      streetlights: '#FCD34D', // Yellow
      parks: '#10B981',       // Emerald
      building: '#8B5CF6',    // Violet
      fire: '#EF4444',        // Red
      other: '#64748B',       // Slate
    },
    // Indian Government Colors
    government: {
      ashokaChakra: '#000080',
      saffron: '#FF9933',
      white: '#FFFFFF',
      green: '#138808',
      tricolor: {
        saffron: '#FF9933',
        white: '#FFFFFF',
        green: '#138808',
      }
    },
    // Status Colors
    status: {
      success: '#059669',
      warning: '#F59E0B',
      error: '#EF4444',
      info: '#2563EB',
      pending: '#F59E0B',
      resolved: '#059669',
    },
    // Text Colors
    text: {
      primary: '#1E3A8A',
      secondary: '#475569',
      tertiary: '#64748B',
      disabled: '#94A3B8',
      inverse: '#FFFFFF',
      link: '#2563EB',
      dark: {
        primary: '#E8EEF7',
        secondary: '#CBD5E1',
        tertiary: '#94A3B8',
        disabled: '#64748B',
      }
    },
    // Background Colors
    background: {
      primary: '#FFFFFF',
      secondary: '#F8FAFC',
      tertiary: '#F1F5F9',
      accent: '#EFF6FF',
      dark: {
        primary: '#1A1D2E',
        secondary: '#23263E',
        tertiary: '#2D3047',
        accent: '#3A3F5C',
      }
    },
  },
  fonts: {
    primary: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
    heading: "'Poppins', 'Inter', sans-serif",
    mono: "'Fira Code', 'Courier New', monospace",
    // Indian Language Fonts (12 languages)
    multilingual: {
      english: "'Inter', sans-serif",
      hindi: "'Noto Sans Devanagari', sans-serif",
      bengali: "'Noto Sans Bengali', sans-serif",
      telugu: "'Noto Sans Telugu', sans-serif",
      marathi: "'Noto Sans Devanagari', sans-serif",
      tamil: "'Noto Sans Tamil', sans-serif",
      gujarati: "'Noto Sans Gujarati', sans-serif",
      kannada: "'Noto Sans Kannada', sans-serif",
      malayalam: "'Noto Sans Malayalam', sans-serif",
      punjabi: "'Noto Sans Gurmukhi', sans-serif",
      urdu: "'Noto Nastaliq Urdu', sans-serif",  // RTL
      assamese: "'Noto Sans Bengali', sans-serif",
      odia: "'Noto Sans Oriya', sans-serif",
    },
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px',
  },
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  },
  shadows: {
    sm: '0 1px 3px rgba(37, 99, 235, 0.12)',      // Trust blue
    md: '0 4px 6px rgba(37, 99, 235, 0.16)',
    lg: '0 10px 15px rgba(37, 99, 235, 0.2)',
    xl: '0 20px 25px rgba(37, 99, 235, 0.25)',
    glass: '0 8px 32px rgba(108, 99, 255, 0.15)',  // Glassmorphism
    glow: '0 0 20px rgba(37, 99, 235, 0.3)',       // Accent glow
  },
  transitions: {
    fast: '150ms ease',
    normal: '300ms ease',
    slow: '500ms ease',
  },
  // Responsive Breakpoints
  breakpoints: {
    mobile: '480px',
    tablet: '768px',
    desktop: '1024px',
    large: '1280px',
  },
  // Media Queries
  mediaQueries: {
    mobile: '@media (max-width: 480px)',
    tablet: '@media (max-width: 768px)',
    desktop: '@media (max-width: 1024px)',
    large: '@media (min-width: 1280px)',
    tabletUp: '@media (min-width: 481px)',
    desktopUp: '@media (min-width: 769px)',
    largeUp: '@media (min-width: 1025px)',
  },
  // Responsive Spacing
  responsiveSpacing: {
    section: {
      mobile: '20px',
      tablet: '40px',
      desktop: '60px',
    },
    container: {
      mobile: '16px',
      tablet: '24px',
      desktop: '32px',
    },
  },
  // Responsive Typography
  responsiveFontSizes: {
    h1: {
      mobile: '28px',
      tablet: '36px',
      desktop: '48px',
    },
    h2: {
      mobile: '24px',
      tablet: '30px',
      desktop: '36px',
    },
    h3: {
      mobile: '20px',
      tablet: '24px',
      desktop: '28px',
    },
    body: {
      mobile: '14px',
      tablet: '15px',
      desktop: '16px',
    },
  },
};

export type Theme = typeof theme;
