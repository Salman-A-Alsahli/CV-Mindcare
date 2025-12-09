export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatNumber = (num, decimals = 1) => {
  return Number(num).toFixed(decimals);
};

export const getStatusColor = (status) => {
  const colors = {
    ACTIVE: 'text-green-600 dark:text-green-400',
    MOCK_MODE: 'text-yellow-600 dark:text-yellow-400',
    ERROR: 'text-red-600 dark:text-red-400',
    INACTIVE: 'text-gray-600 dark:text-gray-400',
    UNAVAILABLE: 'text-orange-600 dark:text-orange-400',
  };
  return colors[status] || 'text-gray-600 dark:text-gray-400';
};

export const getStatusBgColor = (status) => {
  const colors = {
    ACTIVE: 'bg-green-100 dark:bg-green-900',
    MOCK_MODE: 'bg-yellow-100 dark:bg-yellow-900',
    ERROR: 'bg-red-100 dark:bg-red-900',
    INACTIVE: 'bg-gray-100 dark:bg-gray-900',
    UNAVAILABLE: 'bg-orange-100 dark:bg-orange-900',
  };
  return colors[status] || 'bg-gray-100 dark:bg-gray-900';
};

export const getRatingColor = (rating) => {
  const colors = {
    Excellent: 'text-green-600 dark:text-green-400',
    Good: 'text-blue-600 dark:text-blue-400',
    Fair: 'text-yellow-600 dark:text-yellow-400',
    Poor: 'text-red-600 dark:text-red-400',
  };
  return colors[rating] || 'text-gray-600 dark:text-gray-400';
};

export const getPriorityColor = (priority) => {
  const colors = {
    high: 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900',
    medium: 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900',
    low: 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900',
  };
  return colors[priority] || 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-900';
};
