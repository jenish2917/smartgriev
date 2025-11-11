import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
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
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter] = useState<string>('all');

  // Fetch complaints with React Query
  const { data, isLoading, error } = useQuery({
    queryKey: ['complaints', statusFilter, categoryFilter],
    queryFn: () => complaintApi.getComplaints(),
    staleTime: 30000, // 30 seconds
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
    { value: 'all', label: 'All Status', count: totalCount },
    { value: 'pending', label: 'Pending', count: complaints.filter((c: Complaint) => c.status === 'pending').length },
    { value: 'in_progress', label: 'In Progress', count: complaints.filter((c: Complaint) => c.status === 'in_progress').length },
    { value: 'resolved', label: 'Resolved', count: complaints.filter((c: Complaint) => c.status === 'resolved').length },
    { value: 'rejected', label: 'Rejected', count: complaints.filter((c: Complaint) => c.status === 'rejected').length },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              My Complaints
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Track and manage all your submitted complaints
            </p>
          </div>
          <Button variant="primary" onClick={() => window.location.href = '/chat'}>
            + New Complaint
          </Button>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <Input
                type="text"
                placeholder="Search complaints..."
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
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
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
          <div className="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-6 text-center">
            <p className="text-error-700 dark:text-error-400">
              Failed to load complaints. Please try again.
            </p>
          </div>
        ) : filteredComplaints && filteredComplaints.length > 0 ? (
          <div className="space-y-4">
            {filteredComplaints.map((complaint, index) => (
              <motion.div
                key={complaint.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Title and Status */}
                    <div className="flex items-start gap-3 mb-3">
                      <div
                        className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                          complaint.status
                        )}`}
                      >
                        {getStatusIcon(complaint.status)}
                        {complaint.status.replace('_', ' ').toUpperCase()}
                      </div>
                      {complaint.urgency && (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-error-100 text-error-700 dark:bg-error-900/20 dark:text-error-400">
                          {complaint.urgency}
                        </span>
                      )}
                    </div>

                    {/* Title */}
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {complaint.title}
                    </h3>

                    {/* Description */}
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                      {complaint.description}
                    </p>

                    {/* Meta Info */}
                    <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {complaint.address || 'Location not specified'}
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {new Date(complaint.created_at).toLocaleDateString()}
                      </div>
                      <div className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                        {complaint.category}
                      </div>
                      <div className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                        {complaint.department}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 ml-4">
                    <Button variant="ghost" size="sm" leftIcon={<Eye className="w-4 h-4" />}>
                      View
                    </Button>
                    <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-12 text-center border-2 border-dashed border-gray-200 dark:border-gray-700">
            <div className="w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No complaints found
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              {searchQuery || statusFilter !== 'all' || categoryFilter !== 'all'
                ? 'Try adjusting your filters'
                : 'Start by filing your first complaint'}
            </p>
            <Button variant="primary" onClick={() => window.location.href = '/chat'}>
              File New Complaint
            </Button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};
