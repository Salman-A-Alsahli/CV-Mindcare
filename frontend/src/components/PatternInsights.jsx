import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, AlertTriangle, Clock } from 'lucide-react';
import { getPatterns } from '../services/api';

function PatternInsights() {
  const [days, setDays] = useState(14);
  const [patternType, setPatternType] = useState('all');

  const { data, isLoading } = useQuery({
    queryKey: ['patterns', days, patternType],
    queryFn: () => getPatterns(days, patternType),
  });

  const getPatternIcon = (type) => {
    switch (type) {
      case 'time_based':
        return Clock;
      case 'recurring_issue':
        return AlertTriangle;
      default:
        return TrendingUp;
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      high: 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200',
      medium: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200',
      low: 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
    };
    return colors[severity] || colors.low;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400" />
      </div>
    );
  }

  const patterns = data?.patterns || [];

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          Pattern Detection
        </h2>
        <div className="flex space-x-4">
          <select
            value={patternType}
            onChange={(e) => setPatternType(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="all">All Patterns</option>
            <option value="recurring">Recurring Issues</option>
            <option value="time_based">Time-Based</option>
          </select>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="7">Last 7 days</option>
            <option value="14">Last 14 days</option>
            <option value="30">Last 30 days</option>
          </select>
        </div>
      </div>

      {/* Patterns List */}
      {patterns.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
          <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            No patterns detected yet. More data needed for analysis.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {patterns.map((pattern, index) => {
            const Icon = getPatternIcon(pattern.type);
            return (
              <div
                key={index}
                className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
              >
                <div className="flex items-start space-x-4">
                  <div className="p-3 bg-primary-100 dark:bg-primary-900 rounded-lg">
                    <Icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(pattern.severity)}`}>
                        {pattern.severity?.toUpperCase()}
                      </span>
                      <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                        {pattern.category}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      {pattern.description}
                    </h3>
                    {pattern.frequency && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        Frequency: {pattern.frequency}
                      </p>
                    )}
                    {pattern.pattern && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        Pattern: {pattern.pattern}
                      </p>
                    )}
                    {pattern.recommendation && (
                      <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900 rounded-lg">
                        <p className="text-sm text-blue-800 dark:text-blue-200">
                          <strong>Recommendation:</strong> {pattern.recommendation}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Summary */}
      {patterns.length > 0 && (
        <div className="bg-primary-50 dark:bg-primary-900 rounded-lg p-4">
          <p className="text-sm text-gray-700 dark:text-gray-200">
            Found <strong>{patterns.length}</strong> pattern{patterns.length !== 1 ? 's' : ''} in the last {days} days
          </p>
        </div>
      )}
    </div>
  );
}

export default PatternInsights;
