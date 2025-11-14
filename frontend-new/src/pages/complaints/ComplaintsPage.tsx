import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import {
  Search,
  Filter,
  Calendar,
  MapPin,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Eye,
  MoreVertical,
} from 'lucide-react';

import { Button, Input } from '@/components/atoms';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { complaintApi } from '@/api/complaints';
import type { Complaint } from '@/types';

export const ComplaintsPage = () => {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter] = useState<string>('all');

  // Fetch complaints with React Query
  const { data, isLoading, error } = useQuery({
    queryKey: ['complaints', statusFilter, categoryFilter],
    queryFn: () => complaintApi.getComplaints(),
    staleTime: 60000,
    gcTime: 300000,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    refetchOnReconnect: false,
  });

  const complaints = data?.results || [];
  const totalCount = data?.count || 0;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5" />;
      case 'in_progress':
        return <AlertCircle className="w-5 h-5" />;
      case 'resolved':
        return <CheckCircle className="w-5 h-5" />;
      case 'rejected':
        return <XCircle className="w-5 h-5" />;
      default:
        return <Clock className="w-5 h-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-warning-100 text-warning-700 dark:bg-warning-900/20 dark:text-warning-400 border-warning-200 dark:border-warning-800';
      case 'in_progress':
        return 'bg-secondary-100 text-secondary-700 dark:bg-secondary-900/20 dark:text-secondary-400 border-secondary-200 dark:border-secondary-800';
      case 'resolved':
        return 'bg-success-100 text-success-700 dark:bg-success-900/20 dark:text-success-400 border-success-200 dark:border-success-800';
      case 'rejected':
        return 'bg-error-100 text-error-700 dark:bg-error-900/20 dark:text-error-400 border-error-200 dark:border-error-800';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 border-gray-200 dark:border-gray-600';
    }
  };

  const filteredComplaints = complaints.filter((complaint: Complaint) => {
    const matchesSearch =
      complaint.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      complaint.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || complaint.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || complaint.category === categoryFilter;
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const statusOptions = [
    { value: 'all', label: t('complaints.allStatus'), count: totalCount },
    { value: 'pending', label: t('complaints.pending'), count: complaints.filter((c: Complaint) => c.status === 'pending').length },
    { value: 'in_progress', label: t('complaints.inProgress'), count: complaints.filter((c: Complaint) => c.status === 'in_progress').length },
    { value: 'resolved', label: t('complaints.resolved'), count: complaints.filter((c: Complaint) => c.status === 'resolved').length },
    { value: 'rejected', label: t('complaints.rejected'), count: complaints.filter((c: Complaint) => c.status === 'rejected').length },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {t('complaints.pageTitle')}
            </h1>
          </div>
          <Button variant="primary" onClick={() => window.location.href = '/chat'}>
            {t('complaints.newComplaint')}
          </Button>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <Input
                type="text"
                placeholder={t('complaints.search')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                leftIcon={<Search className="w-4 h-4" />}
                wrapperClassName="mb-0"
              />
            </div>

            {/* Status Filter */}
            <div className="w-full md:w-48">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full h-10 px-4 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {statusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label} ({option.count})
                  </option>
                ))}
              </select>
            </div>

            {/* Category Filter */}
            <Button variant="outline" leftIcon={<Filter className="w-4 h-4" />}>
              More Filters
            </Button>
          </div>
        </div>

        {/* Status Tabs */}
        <div className="flex flex-wrap gap-2">
          {statusOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setStatusFilter(option.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === option.value
                  ? 'bg-primary-500 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 hover:shadow-sm'
              }`}
            >
              {option.label} <span className="ml-1 opacity-75">({option.count})</span>
            </button>
          ))}
        </div>

        {/* Complaints List */}
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 animate-pulse"
              >
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-4"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-800 dark:to-gray-850 rounded-2xl p-12 text-center border-2 border-dashed border-primary-200 dark:border-gray-700 shadow-lg"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="w-20 h-20 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl"
            >
              <Search className="w-10 h-10 text-white" />
            </motion.div>
            <motion.h3
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-2xl font-bold text-gray-900 dark:text-white mb-3"
            >
              {t('complaints.noComplaints')}
            </motion.h3>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto"
            >
              {t('complaints.emptyStateMessage')}
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Button
                variant="primary"
                size="lg"
                onClick={() => window.location.href = '/chat'}
                className="shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
              >
                {t('complaints.newComplaint')}
              </Button>
            </motion.div>
          </motion.div>
        ) : filteredComplaints && filteredComplaints.length > 0 ? (
          <div className="space-y-4">
            {filteredComplaints.map((complaint, index) => (
              <motion.div
                key={complaint.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ y: -4, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)' }}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700 transition-all duration-300 cursor-pointer group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Title and Status */}
                    <div className="flex items-start gap-3 mb-3">
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                          complaint.status
                        )}`}
                      >
                        {getStatusIcon(complaint.status)}
                        {complaint.status.replace('_', ' ').toUpperCase()}
                      </motion.div>
                      {complaint.urgency && (
                        <motion.span
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          whileHover={{ scale: 1.1 }}
                          className="px-2 py-1 rounded-full text-xs font-medium bg-error-100 text-error-700 dark:bg-error-900/20 dark:text-error-400"
                        >
                          {complaint.urgency}
                        </motion.span>
                      )}
                    </div>

                    {/* Title */}
                    <motion.h3
                      whileHover={{ x: 4 }}
                      className="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors"
                    >
                      {complaint.title}
                    </motion.h3>

                    {/* Description */}
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                      {complaint.description}
                    </p>

                    {/* Meta Info */}
                    <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                      <motion.div
                        whileHover={{ scale: 1.1 }}
                        className="flex items-center gap-1"
                      >
                        <MapPin className="w-4 h-4" />
                        {complaint.address || 'Location not specified'}
                      </motion.div>
                      <motion.div
                        whileHover={{ scale: 1.1 }}
                        className="flex items-center gap-1"
                      >
                        <Calendar className="w-4 h-4" />
                        {new Date(complaint.created_at).toLocaleDateString()}
                      </motion.div>
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded"
                      >
                        {complaint.category}
                      </motion.div>
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded"
                      >
                        {complaint.department}
                      </motion.div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 ml-4">
                    <Button variant="ghost" size="sm" leftIcon={<Eye className="w-4 h-4" />}>
                      View
                    </Button>
                    <motion.button
                      whileHover={{ scale: 1.1, rotate: 90 }}
                      whileTap={{ scale: 0.95 }}
                      className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <MoreVertical className="w-4 h-4" />
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-800 dark:to-gray-850 rounded-2xl p-12 text-center border-2 border-dashed border-primary-200 dark:border-gray-700 shadow-lg"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="w-20 h-20 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center mx-auto mb-6 shadow-xl"
            >
              <Search className="w-10 h-10 text-white" />
            </motion.div>
            <motion.h3
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-2xl font-bold text-gray-900 dark:text-white mb-3"
            >
              {t('complaints.noComplaints')}
            </motion.h3>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto"
            >
              {searchQuery || statusFilter !== 'all' || categoryFilter !== 'all'
                ? t('complaints.adjustFiltersMessage')
                : t('complaints.emptyStateMessage')}
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Button
                variant="primary"
                size="lg"
                onClick={() => window.location.href = '/chat'}
                className="shadow-lg hover:shadow-xl transform hover:scale-105 transition-all"
              >
                {t('complaints.newComplaint')}
              </Button>
            </motion.div>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  );
};
