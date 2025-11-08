import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpBackend from 'i18next-http-backend';

// Supported languages for India
export const SUPPORTED_LANGUAGES = {
  en: { name: 'English', nativeName: 'English', flag: '🇬🇧' },
  hi: { name: 'Hindi', nativeName: 'हिन्दी', flag: '🇮🇳' },
  bn: { name: 'Bengali', nativeName: 'বাংলা', flag: '🇮🇳' },
  te: { name: 'Telugu', nativeName: 'తెలుగు', flag: '🇮🇳' },
  mr: { name: 'Marathi', nativeName: 'मराठी', flag: '🇮🇳' },
  ta: { name: 'Tamil', nativeName: 'தமிழ்', flag: '🇮🇳' },
  gu: { name: 'Gujarati', nativeName: 'ગુજરાતી', flag: '🇮🇳' },
  kn: { name: 'Kannada', nativeName: 'ಕನ್ನಡ', flag: '🇮🇳' },
};

// Language codes array
export const LANGUAGE_CODES = Object.keys(SUPPORTED_LANGUAGES);

i18n
  // Load translations from backend/public folder
  .use(HttpBackend)
  // Detect user language
  .use(LanguageDetector)
  // Pass the i18n instance to react-i18next
  .use(initReactI18next)
  // Initialize i18next
  .init({
    // Default language
    fallbackLng: 'en',
    
    // Supported languages
    supportedLngs: LANGUAGE_CODES,
    
    // Debug mode (disable in production)
    debug: process.env.NODE_ENV === 'development',
    
    // Language detection options
    detection: {
      // Order of detection methods
      order: ['localStorage', 'navigator', 'htmlTag'],
      
      // Keys to lookup language from
      lookupLocalStorage: 'smartgriev_language',
      
      // Cache user language
      caches: ['localStorage'],
      
      // Don't convert language to lowercase
      convertDetectedLanguage: (lng: string) => lng,
    },
    
    // Backend options
    backend: {
      // Path to load translation files
      loadPath: '/locales/{{lng}}/{{ns}}.json',
      
      // Allow cross-origin requests
      crossDomain: false,
    },
    
    // Namespaces
    ns: ['common', 'auth', 'complaints', 'dashboard', 'notifications'],
    defaultNS: 'common',
    
    // Interpolation options
    interpolation: {
      // React already escapes values
      escapeValue: false,
      
      // Format values
      format: (value, format, lng) => {
        if (format === 'uppercase') return value.toUpperCase();
        if (format === 'lowercase') return value.toLowerCase();
        if (format === 'capitalize') 
          return value.charAt(0).toUpperCase() + value.slice(1);
        return value;
      },
    },
    
    // React options
    react: {
      // Wait for translations to load before rendering
      useSuspense: true,
      
      // Bind i18n to React component
      bindI18n: 'languageChanged loaded',
      
      // Bind store to React component
      bindI18nStore: 'added removed',
    },
    
    // Load options
    load: 'languageOnly', // Load only 'en' not 'en-US'
    
    // Preload languages
    preload: ['en', 'hi'], // Preload English and Hindi
    
    // Clean code
    cleanCode: true,
    
    // Return empty string for missing keys in development
    returnEmptyString: process.env.NODE_ENV === 'development',
    
    // Return key if translation is missing
    returnNull: false,
    
    // Save missing translations
    saveMissing: process.env.NODE_ENV === 'development',
    
    // Missing key handler
    missingKeyHandler: (lngs, ns, key, fallbackValue) => {
      if (process.env.NODE_ENV === 'development') {
        console.warn(`Missing translation: [${ns}] ${key} for languages: ${lngs.join(', ')}`);
      }
    },
  });

// Export configured i18n instance
export default i18n;

// Helper function to change language
export const changeLanguage = (language: string) => {
  return i18n.changeLanguage(language);
};

// Helper function to get current language
export const getCurrentLanguage = () => {
  return i18n.language || 'en';
};

// Helper function to get language display name
export const getLanguageDisplayName = (code: string) => {
  return SUPPORTED_LANGUAGES[code as keyof typeof SUPPORTED_LANGUAGES]?.nativeName || code;
};
