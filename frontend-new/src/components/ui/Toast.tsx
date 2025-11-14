import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react';
import { useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastProps {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  onClose: (id: string) => void;
}

const toastConfig = {
  success: {
    icon: CheckCircle,
    className: 'bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800 text-success-700 dark:text-success-400',
  },
  error: {
    icon: XCircle,
    className: 'bg-error-50 dark:bg-error-900/20 border-error-200 dark:border-error-800 text-error-700 dark:text-error-400',
  },
  warning: {
    icon: AlertCircle,
    className: 'bg-warning-50 dark:bg-warning-900/20 border-warning-200 dark:border-warning-800 text-warning-700 dark:text-warning-400',
  },
  info: {
    icon: Info,
    className: 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800 text-primary-700 dark:text-primary-400',
  },
};

export const Toast = ({ id, type, title, message, duration = 5000, onClose }: ToastProps) => {
  const config = toastConfig[type];
  const Icon = config.icon;

  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(id);
    }, duration);

    return () => clearTimeout(timer);
  }, [id, duration, onClose]);

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.3 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.5 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className={`flex items-start gap-3 p-4 rounded-lg border shadow-lg min-w-[320px] max-w-md ${config.className}`}
    >
      <motion.div
        initial={{ rotate: -180 }}
        animate={{ rotate: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
      </motion.div>
      
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-sm">{title}</h4>
        {message && <p className="text-sm mt-1 opacity-90">{message}</p>}
      </div>

      <motion.button
        whileHover={{ scale: 1.1, rotate: 90 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => onClose(id)}
        className="p-1 rounded hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
      >
        <X className="w-4 h-4" />
      </motion.button>

      {/* Progress bar */}
      <motion.div
        initial={{ scaleX: 1 }}
        animate={{ scaleX: 0 }}
        transition={{ duration: duration / 1000, ease: 'linear' }}
        className="absolute bottom-0 left-0 right-0 h-1 bg-current opacity-30 rounded-b-lg origin-left"
      />
    </motion.div>
  );
};

export const ToastContainer = ({ toasts }: { toasts: ToastProps[] }) => {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <Toast key={toast.id} {...toast} />
        ))}
      </AnimatePresence>
    </div>
  );
};
