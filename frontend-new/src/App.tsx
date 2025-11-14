import { Button } from '@/components/atoms';
import { Navbar } from '@/components/Navbar';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

const App = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-900 dark:to-gray-800">
      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <div className="flex items-center justify-center min-h-screen p-4 pt-20">
        <div className="max-w-2xl w-full">
        <div className="text-center space-y-6 animate-fade-in">
          {/* Logo/Icon */}
          <div className="flex justify-center">
            <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center shadow-lg animate-scale-in">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="w-12 h-12 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
          </div>

          {/* Title */}
          <div className="space-y-4">
            <h1 className="text-5xl font-bold text-gradient animate-slide-in-from-bottom animation-delay-100 leading-tight break-words">
              {t('common.appName')}
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 font-medium animate-slide-in-from-bottom animation-delay-150 leading-relaxed break-words px-4">
              {t('common.tagline')}
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8 animate-slide-in-from-bottom animation-delay-300">
            <FeatureCard
              icon={
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-6 h-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
              }
              title={t('features.aiChatbot')}
              description={t('features.aiChatbotDesc')}
            />
            <FeatureCard
              icon={
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-6 h-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
                  />
                </svg>
              }
              title={t('features.languages')}
              description={t('features.languagesDesc')}
            />
            <FeatureCard
              icon={
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-6 h-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
              }
              title={t('features.voiceVision')}
              description={t('features.voiceVisionDesc')}
            />
          </div>

          {/* Loading Indicator */}
          <div className="flex justify-center gap-2 mt-6 animate-pulse">
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce animation-delay-100" />
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce animation-delay-200" />
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce animation-delay-300" />
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mt-8 justify-center animate-slide-in-from-bottom animation-delay-500">
            <Button
              variant="primary"
              size="lg"
              className="shadow-xl"
              onClick={() => navigate('/login')}
            >
              {t('actions.getStarted')}
            </Button>
            <Button variant="outline" size="lg" onClick={() => navigate('/register')}>
              {t('actions.registerNow')}
            </Button>
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

// Feature Card Component
const FeatureCard = ({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) => {
  return (
    <div className="glass p-6 rounded-xl card-shadow hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
      <div className="flex flex-col items-center text-center space-y-3">
        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center text-white">
          {icon}
        </div>
        <h3 className="font-semibold text-gray-900 dark:text-white leading-normal break-words">{title}</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed break-words">{description}</p>
      </div>
    </div>
  );
};

export default App;
