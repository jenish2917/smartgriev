import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  FileText,
  User,
  LogOut,
  Bell,
  Settings,
  Globe,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Button } from '@/components/atoms';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const navigate = useNavigate();
  const { user, clearAuth } = useAuthStore();
  const { isDarkMode, toggleTheme } = useThemeStore();
  const { t, i18n } = useTranslation();
  const [showNavbar, setShowNavbar] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLang = e.target.value;
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang); // Use 'language' key for consistency
  };

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी' },
    { code: 'bn', name: 'বাংলা' },
    { code: 'te', name: 'తెలుగు' },
    { code: 'mr', name: 'मराठी' },
    { code: 'ta', name: 'தமிழ்' },
    { code: 'gu', name: 'ગુજરાતી' },
    { code: 'kn', name: 'ಕನ್ನಡ' },
    { code: 'ml', name: 'മലയാളം' },
    { code: 'pa', name: 'ਪੰਜਾਬੀ' },
    { code: 'ur', name: 'اردو' },
    { code: 'or', name: 'ଓଡ଼ିଆ' },
  ];

  const menuItems = [
    { icon: FileText, label: t('navigation.myComplaints'), path: '/complaints' },
    { icon: MessageSquare, label: t('navigation.aiChat'), path: '/chat' },
    { icon: User, label: t('navigation.profile'), path: '/profile' },
    { icon: Settings, label: t('navigation.settings'), path: '/settings' },
  ];

  // Auto-hide navbar on scroll
  useEffect(() => {
    const handleScroll = (e: Event) => {
      const target = e.target as HTMLElement;
      if (!target) return;

      const currentScrollY = target.scrollTop;
      
      if (currentScrollY < 10) {
        setShowNavbar(true);
      } else if (currentScrollY < lastScrollY) {
        // Scrolling up
        setShowNavbar(true);
      } else if (currentScrollY > lastScrollY && currentScrollY > 100) {
        // Scrolling down
        setShowNavbar(false);
      }
      
      setLastScrollY(currentScrollY);
    };

    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.addEventListener('scroll', handleScroll);
      return () => mainContent.removeEventListener('scroll', handleScroll);
    }
  }, [lastScrollY]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Fixed Sidebar */}
      <aside className="fixed left-0 top-0 h-screen w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col z-30">
        {/* Logo */}
        <div className="h-16 flex items-center px-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white text-sm font-bold">
              SG
            </div>
            <span className="font-bold text-gray-900 dark:text-white">
              SmartGriev
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {menuItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                window.location.pathname === item.path
                  ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* User Section */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="space-y-2">
            <div className="flex items-center gap-3 p-2 rounded-lg bg-gray-50 dark:bg-gray-700/50">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center text-white font-medium">
                {user?.first_name?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {user?.email}
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              fullWidth
              onClick={handleLogout}
              className="justify-start"
            >
              <LogOut className="w-4 h-4 mr-2" />
              {t('navigation.logout')}
            </Button>
          </div>
        </div>
      </aside>

      {/* Main Content with offset for fixed sidebar */}
      <div className="flex-1 ml-64 flex flex-col min-w-0">
        {/* Auto-hide Header */}
        <header 
          className={`fixed top-0 right-0 left-64 h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-6 z-20 transition-transform duration-300 ${
            showNavbar ? 'translate-y-0' : '-translate-y-full'
          }`}
        >
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">
            {menuItems.find((item) => item.path === window.location.pathname)
              ?.label || 'Dashboard'}
          </h1>

          <div className="flex items-center gap-3">
            {/* Language Selector */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700">
              <Globe className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              <select
                value={i18n.language}
                onChange={handleLanguageChange}
                title="Select language"
                aria-label="Select language"
                className="text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none cursor-pointer [&>option]:bg-white [&>option]:dark:bg-gray-800 [&>option]:text-gray-900 [&>option]:dark:text-white"
              >
                {languages.map((lang) => (
                  <option key={lang.code} value={lang.code} className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>

            <button 
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 relative"
              title="Notifications"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-error-500 rounded-full"></span>
            </button>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
              title={isDarkMode ? 'Light mode' : 'Dark mode'}
            >
              {isDarkMode ? '🌙' : '☀️'}
            </button>
          </div>
        </header>

        {/* Page Content with padding for header */}
        <main 
          id="main-content"
          className="flex-1 overflow-auto pt-16"
        >
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
