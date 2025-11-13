import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  User,
  Bell,
  Lock,
  Globe,
  Moon,
  Sun,
  Mic,
  Save,
  ChevronRight,
} from 'lucide-react';

import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { Button } from '@/components/atoms';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';

export const SettingsPage = () => {
  const { user } = useAuthStore();
  const { isDarkMode, toggleTheme } = useThemeStore();
  const { i18n, t } = useTranslation();

  const [activeTab, setActiveTab] = useState('general');
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    sms: false,
    complaintUpdates: true,
    systemAlerts: true,
  });

  const [voiceSettings, setVoiceSettings] = useState({
    enabled: true,
    language: i18n.language,
    autoPlay: false,
    speed: 1.0,
  });

  const tabs = [
    { id: 'general', label: 'General', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'language', label: 'Language & Region', icon: Globe },
    { id: 'voice', label: 'Voice Assistant', icon: Mic },
    { id: 'appearance', label: 'Appearance', icon: isDarkMode ? Moon : Sun },
  ];

  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'hi', name: 'हिंदी - Hindi', flag: '🇮🇳' },
    { code: 'bn', name: 'বাংলা - Bengali', flag: '🇧🇩' },
    { code: 'te', name: 'తెలుగు - Telugu', flag: '🇮🇳' },
    { code: 'mr', name: 'मराठी - Marathi', flag: '🇮🇳' },
    { code: 'ta', name: 'தமிழ் - Tamil', flag: '🇮🇳' },
    { code: 'gu', name: 'ગુજરાતી - Gujarati', flag: '🇮🇳' },
    { code: 'kn', name: 'ಕನ್ನಡ - Kannada', flag: '🇮🇳' },
    { code: 'ml', name: 'മലയാളം - Malayalam', flag: '🇮🇳' },
    { code: 'pa', name: 'ਪੰਜਾਬੀ - Punjabi', flag: '🇮🇳' },
    { code: 'ur', name: 'اردو - Urdu', flag: '🇵🇰' },
    { code: 'or', name: 'ଓଡ଼ିଆ - Odia', flag: '🇮🇳' },
  ];

  const handleSaveSettings = () => {
    // Save settings logic
    alert('Settings saved successfully!');
  };

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t('navigation.settings')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage your account settings and preferences
          </p>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar Tabs */}
          <div className="col-span-3">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  <span className="text-sm font-medium flex-1 text-left">
                    {tab.label}
                  </span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              ))}
            </div>
          </div>

          {/* Content Area */}
          <div className="col-span-9">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              {/* General Settings */}
              {activeTab === 'general' && (
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    General Settings
                  </h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Name
                      </label>
                      <input
                        type="text"
                        title="User name"
                        placeholder="Name"
                        value={`${user?.first_name} ${user?.last_name}`}
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        readOnly
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Email
                      </label>
                      <input
                        type="email"
                        title="User email"
                        placeholder="Email"
                        value={user?.email || ''}
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        readOnly
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Notifications */}
              {activeTab === 'notifications' && (
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Notification Preferences
                  </h2>
                  <div className="space-y-4">
                    {Object.entries(notifications).map(([key, value]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700 last:border-0"
                      >
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white capitalize">
                            {key.replace(/([A-Z])/g, ' $1').trim()}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Receive notifications via {key}
                          </p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={value}
                            onChange={(e) =>
                                  setNotifications({
                                ...notifications,
                                [key]: e.target.checked,
                              })
                            }
                            className="sr-only peer"
                            title={`Toggle ${key} notifications`}
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Security */}
              {activeTab === 'security' && (
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Security Settings
                  </h2>
                  <div className="space-y-4">
                    <button className="w-full flex items-center justify-between px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                      <div className="flex items-center gap-3">
                        <Lock className="w-5 h-5 text-gray-500" />
                        <div className="text-left">
                          <p className="font-medium text-gray-900 dark:text-white">
                            Change Password
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Last changed: Nov 12, 2025
                          </p>
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-gray-400" />
                    </button>
                  </div>
                </div>
              )}

              {/* Language */}
              {activeTab === 'language' && (
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Language & Region
                  </h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Display Language
                      </label>
                      <select
                        value={i18n.language}
                        onChange={(e) => {
                          i18n.changeLanguage(e.target.value);
                          localStorage.setItem('i18nextLng', e.target.value);
                        }}
                        title="Select display language"
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        {languages.map((lang) => (
                          <option key={lang.code} value={lang.code}>
                            {lang.flag} {lang.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Voice Assistant */}
              {activeTab === 'voice' && (
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Voice Assistant Settings
                  </h2>
                  <div className="space-y-6">
                    <div className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          Enable Voice Assistant
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Use voice commands in chatbot
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={voiceSettings.enabled}
                          onChange={(e) =>
                            setVoiceSettings({
                              ...voiceSettings,
                              enabled: e.target.checked,
                            })
                          }
                          className="sr-only peer"
                          title="Toggle voice assistant"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                      </label>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Voice Language
                      </label>
                      <select
                        value={voiceSettings.language}
                        onChange={(e) =>
                          setVoiceSettings({
                            ...voiceSettings,
                            language: e.target.value,
                          })
                        }
                        title="Select voice language"
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        {languages.map((lang) => (
                          <option key={lang.code} value={lang.code}>
                            {lang.flag} {lang.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Speech Speed: {voiceSettings.speed}x
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="2"
                        step="0.1"
                        value={voiceSettings.speed}
                        onChange={(e) =>
                          setVoiceSettings({
                            ...voiceSettings,
                            speed: parseFloat(e.target.value),
                          })
                        }
                        title="Adjust speech speed"
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Appearance */}
              {activeTab === 'appearance' && (
                <div className="p-6">
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Appearance
                  </h2>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <button
                        onClick={() => !isDarkMode && toggleTheme()}
                        className={`p-4 rounded-lg border-2 transition-colors ${
                          !isDarkMode
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
                        }`}
                      >
                        <Sun className="w-8 h-8 mx-auto mb-2" />
                        <p className="font-medium">Light Mode</p>
                      </button>
                      <button
                        onClick={() => isDarkMode && toggleTheme()}
                        className={`p-4 rounded-lg border-2 transition-colors ${
                          isDarkMode
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
                        }`}
                      >
                        <Moon className="w-8 h-8 mx-auto mb-2" />
                        <p className="font-medium">Dark Mode</p>
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Save Button */}
              <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
                <Button onClick={handleSaveSettings} className="flex items-center gap-2">
                  <Save className="w-4 h-4" />
                  Save Changes
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};
