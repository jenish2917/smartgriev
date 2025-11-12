import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Select, Space, Typography, message } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { SUPPORTED_LANGUAGES, changeLanguage, getCurrentLanguage } from '@/i18n';
import axios from 'axios';
import { buildApiUrl } from '../../config/api.config';
import styles from './LanguageSwitcher.module.css';

const { Option } = Select;
const { Text } = Typography;

interface LanguageSwitcherProps {
  showLabel?: boolean;
  size?: 'small' | 'middle' | 'large';
  style?: React.CSSProperties;
  className?: string;
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({
  showLabel = true,
  size = 'middle',
  style,
  className,
}) => {
  const { t, i18n } = useTranslation('common');
  const currentLanguage = getCurrentLanguage();

  // Keep a local selected state to ensure Select value is always one of the
  // simple language codes (i18n.language may return values like "en-US").
  const normalize = (lng: string) => (lng ? lng.split('-')[0] : 'en');
  const [selected, setSelected] = useState<string>(normalize(currentLanguage));

  const handleLanguageChange = async (languageCode: string) => {
    try {
      // update i18n and local state
      await changeLanguage(languageCode);
      setSelected(normalize(languageCode));
      // Ensure translations are reloaded (useful when using HttpBackend)
      try {
        await (i18n as any).reloadResources?.([languageCode]);
      } catch (reloadErr) {
        // reloadResources may not return a promise in some i18next versions; ignore errors
      }
      
      // Store user preference in localStorage
      localStorage.setItem('smartgriev_language', languageCode);
      
      // Update user profile if logged in
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await axios.post(
            buildApiUrl('/api/users/update-language/'),
            { language: languageCode },
            {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            }
          );
          
          if (response.status === 200) {
            message.success(`Language changed to ${SUPPORTED_LANGUAGES[languageCode as keyof typeof SUPPORTED_LANGUAGES].nativeName}`);
          }
        } catch (apiError) {
          console.error('Failed to update user language preference:', apiError);
          // Still show success since language changed in UI
          message.info(`Language changed to ${SUPPORTED_LANGUAGES[languageCode as keyof typeof SUPPORTED_LANGUAGES].nativeName}. Your preference will sync when you log in next time.`);
        }
      } else {
        // Show success for unauthenticated users
          message.success(`${SUPPORTED_LANGUAGES[languageCode as keyof typeof SUPPORTED_LANGUAGES].nativeName} selected`);
      }
    } catch (error) {
      console.error('Failed to change language:', error);
      message.error('Failed to change language. Please try again.');
    }
  };

  return (
    <Space style={style} className={className}>
      {showLabel && (
        <Text className={styles.languageLabel} strong>
          <GlobalOutlined /> {t('selectLanguage')}
        </Text>
      )}
      <Select
        value={selected}
        onChange={handleLanguageChange}
        size={size}
        style={{ minWidth: 180 }}
        optionLabelProp="label"
        aria-label={t('selectLanguage')}
        placeholder={t('selectLanguage')}
        showSearch
        filterOption={(input, option) => {
          if (!input) return true;
          const searchStr = input.toLowerCase();
          const langCode = (option?.value as string) || '';
          const langData = SUPPORTED_LANGUAGES[langCode as keyof typeof SUPPORTED_LANGUAGES];
          
          // Search in native name, English name, and language code
          return (
            langData?.nativeName.toLowerCase().includes(searchStr) ||
            langData?.name.toLowerCase().includes(searchStr) ||
            langCode.toLowerCase().includes(searchStr)
          );
        }}
        notFoundContent={
          <div style={{ padding: '8px', textAlign: 'center', color: '#999' }}>
            No matching language found
          </div>
        }
      >
        {Object.entries(SUPPORTED_LANGUAGES).map(([code, lang]) => (
            <Option 
            key={code} 
            value={code}
            label={
              <Space>
                <span>{lang.flag}</span>
                <span>{lang.nativeName}</span>
              </Space>
            }
          >
            <Space>
              <span className={styles.languageFlag}>{lang.flag}</span>
              <div>
                <div>{lang.nativeName}</div>
                <div className={styles.languageSubtext}>{lang.name}</div>
              </div>
            </Space>
          </Option>
        ))}
      </Select>
    </Space>
  );
};

export default LanguageSwitcher;
