import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Mail, Lock, Eye, EyeOff, User, Phone, MapPin, Loader2, Globe } from 'lucide-react';
import { motion } from 'framer-motion';

import { Button, Input } from '@/components/atoms';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';
import { handleApiError } from '@/lib/axios';
import { LANGUAGES } from '@/utils/constants';

export const RegisterPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    mobile_number: '',
    address: '',
    language_preference: 'en',
    terms_accepted: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
    }

    if (!formData.terms_accepted) {
      newErrors.terms = 'You must accept the terms and conditions';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const response = await authApi.register(formData);

      if (response.access && response.refresh && response.user) {
        setAuth(response.user, response.access, response.refresh);
        navigate('/complaints');
      } else {
        setErrors({ general: 'Invalid response from server' });
      }
    } catch (err) {
      setErrors({ general: handleApiError(err) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl"
      >
        {/* Card */}
        <div className="glass rounded-2xl shadow-2xl p-8 space-y-6">
          {/* Logo & Title */}
          <div className="text-center space-y-2">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
              className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-500 text-white mb-4"
            >
              <User className="w-8 h-8" />
            </motion.div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {t('auth.register')}
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {t('auth.createAccount')}
            </p>
          </div>

          {/* Error Message */}
          {errors.general && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-lg p-3 text-sm text-error-700 dark:text-error-400"
            >
              {errors.general}
            </motion.div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Row 1: First & Last Name */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              <Input
                id="first_name"
                type="text"
                label={t('auth.firstName')}
                placeholder="Rahul"
                value={formData.first_name}
                onChange={(e) =>
                  setFormData({ ...formData, first_name: e.target.value })
                }
                leftIcon={<User className="w-4 h-4" />}
                required
                disabled={loading}
              />
              <Input
                id="last_name"
                type="text"
                label={t('auth.lastName')}
                placeholder="Sharma"
                value={formData.last_name}
                onChange={(e) =>
                  setFormData({ ...formData, last_name: e.target.value })
                }
                leftIcon={<User className="w-4 h-4" />}
                required
                disabled={loading}
              />
            </motion.div>

            {/* Row 2: Username & Email */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              <Input
                id="username"
                type="text"
                label={t('auth.username')}
                placeholder="rahulsharma"
                value={formData.username}
                onChange={(e) =>
                  setFormData({ ...formData, username: e.target.value })
                }
                leftIcon={<User className="w-4 h-4" />}
                required
                disabled={loading}
              />
              <Input
                id="email"
                type="email"
                label={t('auth.email')}
                placeholder="rahul@example.com"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                leftIcon={<Mail className="w-4 h-4" />}
                required
                disabled={loading}
              />
            </motion.div>

            {/* Row 3: Mobile & Language */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              <Input
                id="mobile_number"
                type="tel"
                label={t('auth.mobileNumber')}
                placeholder="+91 9876543210"
                value={formData.mobile_number}
                onChange={(e) =>
                  setFormData({ ...formData, mobile_number: e.target.value })
                }
                leftIcon={<Phone className="w-4 h-4" />}
                disabled={loading}
              />
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  <Globe className="w-4 h-4 inline mr-1" />
                  {t('auth.language')}
                </label>
                <select
                  value={formData.language_preference}
                  onChange={(e) =>
                    setFormData({ ...formData, language_preference: e.target.value })
                  }
                  title="Select language preference"
                  aria-label="Language preference"
                  className="flex w-full h-10 rounded-md border border-gray-300 dark:border-gray-600 bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={loading}
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.nativeName}
                    </option>
                  ))}
                </select>
              </div>
            </motion.div>

            {/* Address */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <Input
              id="address"
              type="text"
              label={t('auth.address')}
              placeholder="MG Road, Mumbai"
              value={formData.address}
              onChange={(e) =>
                setFormData({ ...formData, address: e.target.value })
              }
              leftIcon={<MapPin className="w-4 h-4" />}
              disabled={loading}
              />
            </motion.div>

            {/* Password Fields */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                label={t('auth.password')}
                placeholder="Min. 8 characters"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                leftIcon={<Lock className="w-4 h-4" />}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                }
                error={errors.password}
                required
                disabled={loading}
              />
              <Input
                id="password_confirm"
                type={showConfirmPassword ? 'text' : 'password'}
                label={t('auth.confirmPassword')}
                placeholder="Repeat password"
                value={formData.password_confirm}
                onChange={(e) =>
                  setFormData({ ...formData, password_confirm: e.target.value })
                }
                leftIcon={<Lock className="w-4 h-4" />}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                }
                error={errors.password_confirm}
                required
                disabled={loading}
              />
            </motion.div>

            {/* Terms & Conditions */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="space-y-1"
            >
              <label className="flex items-start gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.terms_accepted}
                  onChange={(e) =>
                    setFormData({ ...formData, terms_accepted: e.target.checked })
                  }
                  className="w-4 h-4 mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {t('auth.termsAccept')}{' '}
                  <Link
                    to="/terms"
                    className="text-primary-600 hover:text-primary-700 dark:text-primary-400"
                  >
                    {t('auth.termsConditions')}
                  </Link>{' '}
                  {t('auth.and')}{' '}
                  <Link
                    to="/privacy"
                    className="text-primary-600 hover:text-primary-700 dark:text-primary-400"
                  >
                    {t('auth.privacyPolicy')}
                  </Link>
                </span>
              </label>
              {errors.terms && (
                <p className="text-sm text-error-500">{errors.terms}</p>
              )}
            </motion.div>

            {/* Submit Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              disabled={loading}
              className="mt-6"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {t('auth.creatingAccount')}
                </>
              ) : (
                t('auth.register')
              )}
              </Button>
            </motion.div>
          </form>

          {/* Login Link */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.0 }}
            className="text-center text-sm text-gray-600 dark:text-gray-400"
          >
            {t('auth.alreadyHaveAccount')}{' '}
            <Link
              to="/login"
              className="font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
            >
              {t('auth.login')}
            </Link>
          </motion.p>
        </div>

        {/* Footer */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.1 }}
          className="text-center text-xs text-gray-500 mt-6"
        >
          © 2025 SmartGriev. All rights reserved.
        </motion.p>
      </motion.div>
    </div>
  );
};
