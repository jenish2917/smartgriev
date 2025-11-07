import React from 'react';
import { useTranslation } from 'react-i18next';
import { Select, Space, Typography } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { SUPPORTED_LANGUAGES, changeLanguage, getCurrentLanguage } from '@/i18n';

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
      
      // Store user preference
      localStorage.setItem('smartgriev_language', languageCode);
      
      // Update user profile if logged in
      const token = localStorage.getItem('token');
      if (token) {
        try {
          // TODO: Call API to update user language preference
          // await updateUserProfile({ preferred_language: languageCode });
        } catch (error) {
          console.error('Failed to update user language preference:', error);
        }
      }
      
      // Show success message
      console.log(`Language changed to ${SUPPORTED_LANGUAGES[languageCode as keyof typeof SUPPORTED_LANGUAGES].nativeName}`);
    } catch (error) {
      console.error('Failed to change language:', error);
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
