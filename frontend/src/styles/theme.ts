// SmartGriev Blue & White Theme
export const theme = {
  colors: {
    // Primary Blue Shades
    primary: {
      50: '#E3F2FD',
      100: '#BBDEFB',
      200: '#90CAF9',
      300: '#64B5F6',
      400: '#42A5F5',
      500: '#2196F3',  // Main Blue
      600: '#1E88E5',
      700: '#1976D2',
      800: '#1565C0',
      900: '#0D47A1',
    },
    // Secondary Blue Shades
    secondary: {
      50: '#E1F5FE',
      100: '#B3E5FC',
      200: '#81D4FA',
      300: '#4FC3F7',
      400: '#29B6F6',
      500: '#03A9F4',
      600: '#039BE5',
      700: '#0288D1',
      800: '#0277BD',
      900: '#01579B',
    },
    // White Shades
    white: {
      pure: '#FFFFFF',
      50: '#FAFAFA',
      100: '#F5F5F5',
      200: '#EEEEEE',
      300: '#E0E0E0',
      400: '#BDBDBD',
    },
    // Accent Colors
    accent: {
      blue: '#2196F3',
      lightBlue: '#64B5F6',
      darkBlue: '#1565C0',
      cyan: '#00BCD4',
    },
    // Status Colors
    status: {
      success: '#4CAF50',
      warning: '#FF9800',
      error: '#F44336',
      info: '#2196F3',
    },
    // Text Colors
    text: {
      primary: '#1565C0',
      secondary: '#1976D2',
      tertiary: '#64B5F6',
      dark: '#0D47A1',
      light: '#90CAF9',
      white: '#FFFFFF',
    },
    // Background Colors
    background: {
      primary: '#FFFFFF',
      secondary: '#F5F5F5',
      tertiary: '#E3F2FD',
      blue: '#2196F3',
      lightBlue: '#BBDEFB',
    },
  },
  fonts: {
    primary: "'Inter', 'Segoe UI', 'Roboto', sans-serif",
    heading: "'Poppins', 'Inter', sans-serif",
    mono: "'Fira Code', 'Courier New', monospace",
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
    sm: '0 1px 3px rgba(33, 150, 243, 0.12)',
    md: '0 4px 6px rgba(33, 150, 243, 0.16)',
    lg: '0 10px 15px rgba(33, 150, 243, 0.2)',
    xl: '0 20px 25px rgba(33, 150, 243, 0.25)',
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
