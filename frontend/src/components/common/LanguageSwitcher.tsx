import React from 'react';
import { useTranslation } from 'react-i18next';
import { Select, Space, Typography, message } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { SUPPORTED_LANGUAGES, changeLanguage, getCurrentLanguage } from '@/i18n';
import axios from 'axios';

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

  const handleLanguageChange = async (languageCode: string) => {
    try {
      await changeLanguage(languageCode);
      
      // Store user preference in localStorage
      localStorage.setItem('smartgriev_language', languageCode);
      
      // Update user profile if logged in
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await axios.post(
            'http://127.0.0.1:8000/api/users/update-language/',
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
          message.warning('Language changed locally. Please log in again to persist your preference.');
        }
      } else {
        // Show success for unauthenticated users
        message.success(`Language changed to ${SUPPORTED_LANGUAGES[languageCode as keyof typeof SUPPORTED_LANGUAGES].nativeName}`);
      }
    } catch (error) {
      console.error('Failed to change language:', error);
      message.error('Failed to change language. Please try again.');
    }
  };

  return (
    <Space style={style} className={className}>
      {showLabel && (
        <Text>
          <GlobalOutlined /> {t('selectLanguage')}
        </Text>
      )}
      <Select
        value={currentLanguage}
        onChange={handleLanguageChange}
        size={size}
        style={{ minWidth: 180 }}
        optionLabelProp="label"
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
              <span style={{ fontSize: '18px' }}>{lang.flag}</span>
              <div>
                <div>{lang.nativeName}</div>
                <div style={{ fontSize: '12px', color: '#999' }}>{lang.name}</div>
              </div>
            </Space>
          </Option>
        ))}
      </Select>
    </Space>
  );
};

export default LanguageSwitcher;
