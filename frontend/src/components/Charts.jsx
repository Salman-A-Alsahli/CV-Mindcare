import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getAggregatedData, getStatistics } from '../services/api';
import { formatDate } from '../utils/formatters';

function Charts() {
  const [dataType, setDataType] = useState('greenery');
  const [period, setPeriod] = useState('hourly');
  const [days, setDays] = useState(1);

  const { data: aggregatedData, isLoading: aggLoading } = useQuery({
    queryKey: ['aggregatedData', dataType, period, days],
    queryFn: () => getAggregatedData(dataType, period, days),
  });

  const { data: statistics } = useQuery({
    queryKey: ['statistics', dataType, days],
    queryFn: () => getStatistics(dataType, days),
  });

  const chartData = aggregatedData?.data?.map(item => ({
    time: formatDate(item.timestamp),
    value: item.avg,
    min: item.min,
    max: item.max,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Data Type
          </label>
          <select
            value={dataType}
            onChange={(e) => setDataType(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="greenery">Greenery</option>
            <option value="noise">Noise</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Period
          </label>
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="hourly">Hourly</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Days
          </label>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="1">1 Day</option>
            <option value="7">7 Days</option>
            <option value="30">30 Days</option>
          </select>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Average</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {statistics.avg?.toFixed(1)}
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Minimum</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {statistics.min?.toFixed(1)}
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Maximum</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {statistics.max?.toFixed(1)}
            </div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Std Dev</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {statistics.stddev?.toFixed(1)}
            </div>
          </div>
        </div>
      )}

      {/* Line Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          {dataType === 'greenery' ? 'Greenery Trends' : 'Noise Levels'}
        </h3>
        {aggLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400" />
          </div>
        ) : chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '0.5rem',
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#22C55E" strokeWidth={2} name="Average" />
              <Line type="monotone" dataKey="min" stroke="#3B82F6" strokeWidth={1} name="Min" />
              <Line type="monotone" dataKey="max" stroke="#EF4444" strokeWidth={1} name="Max" />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-center text-gray-500 dark:text-gray-400 py-12">
            No data available for this time period
          </p>
        )}
      </div>

      {/* Bar Chart */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Distribution
        </h3>
        {aggLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400" />
          </div>
        ) : chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '0.5rem',
                }}
              />
              <Legend />
              <Bar dataKey="value" fill="#22C55E" name="Average" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-center text-gray-500 dark:text-gray-400 py-12">
            No data available for this time period
          </p>
        )}
      </div>
    </div>
  );
}

export default Charts;
