import { motion } from 'framer-motion';
import {
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  MessageSquare,
  FileText,
} from 'lucide-react';

import { Button } from '@/components/atoms';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { useAuthStore } from '@/store/authStore';
import { useNavigate } from 'react-router-dom';

export const DashboardPage = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const stats = [
    {
      icon: FileText,
      label: 'Total Complaints',
      value: '12',
      change: '+2 this week',
      color: 'primary',
    },
    {
      icon: Clock,
      label: 'Pending',
      value: '5',
      change: '2 need attention',
      color: 'warning',
    },
    {
      icon: TrendingUp,
      label: 'In Progress',
      value: '4',
      change: 'Updated today',
      color: 'secondary',
    },
    {
      icon: CheckCircle,
      label: 'Resolved',
      value: '3',
      change: '100% satisfaction',
      color: 'success',
    },
  ];

  const recentComplaints = [
    {
      id: 1,
      title: 'Street Light Not Working',
      status: 'in_progress',
      date: '2 hours ago',
      department: 'Electricity',
    },
    {
      id: 2,
      title: 'Garbage Not Collected',
      status: 'pending',
      date: '1 day ago',
      department: 'Sanitation',
    },
    {
      id: 3,
      title: 'Road Pothole Issue',
      status: 'resolved',
      date: '3 days ago',
      department: 'Public Works',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-warning-100 text-warning-700 dark:bg-warning-900/20 dark:text-warning-400';
      case 'in_progress':
        return 'bg-secondary-100 text-secondary-700 dark:bg-secondary-900/20 dark:text-secondary-400';
      case 'resolved':
        return 'bg-success-100 text-success-700 dark:bg-success-900/20 dark:text-success-400';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl p-8 text-white"
        >
          <h2 className="text-3xl font-bold mb-2">
            Welcome back, {user?.first_name}! 👋
          </h2>
          <p className="text-primary-100 mb-6">
            You have 2 complaints that need your attention today.
          </p>
          <div className="flex gap-4">
            <Button
              variant="secondary"
              size="lg"
              onClick={() => navigate('/chat')}
              leftIcon={<MessageSquare className="w-5 h-5" />}
            >
              Chat with AI
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="border-white text-white hover:bg-white/10"
            >
              View All Complaints
            </Button>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center justify-between mb-4">
                <div
                  className={`w-12 h-12 rounded-lg bg-${stat.color}-100 dark:bg-${stat.color}-900/20 flex items-center justify-center`}
                >
                  <stat.icon
                    className={`w-6 h-6 text-${stat.color}-600 dark:text-${stat.color}-400`}
                  />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {stat.value}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                {stat.label}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                {stat.change}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700"
        >
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Recent Complaints
            </h3>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {recentComplaints.map((complaint) => (
              <div
                key={complaint.id}
                className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-1">
                      {complaint.title}
                    </h4>
                    <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
                      <span>{complaint.department}</span>
                      <span>•</span>
                      <span>{complaint.date}</span>
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                      complaint.status
                    )}`}
                  >
                    {complaint.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <Button variant="ghost" fullWidth>
              View All Complaints
            </Button>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <MessageSquare className="w-8 h-8 text-primary-500 mb-4" />
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
              AI Assistant
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Chat with our AI to file complaints or get help
            </p>
            <Button
              variant="outline"
              size="sm"
              fullWidth
              onClick={() => navigate('/chat')}
            >
              Start Chat
            </Button>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <FileText className="w-8 h-8 text-secondary-500 mb-4" />
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
              Track Complaints
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              View and track all your submitted complaints
            </p>
            <Button variant="outline" size="sm" fullWidth>
              View Complaints
            </Button>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <AlertCircle className="w-8 h-8 text-warning-500 mb-4" />
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
              Need Help?
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Get support and learn how to use the platform
            </p>
            <Button variant="outline" size="sm" fullWidth>
              Help Center
            </Button>
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};
