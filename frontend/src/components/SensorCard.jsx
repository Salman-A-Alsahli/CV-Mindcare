import { useQuery } from '@tanstack/react-query';
import { Camera, Mic, TrendingUp } from 'lucide-react';
import { captureSensorData } from '../services/api';
import { formatNumber, getStatusColor, getStatusBgColor } from '../utils/formatters';

function SensorCard({ sensorType, title, status }) {
  const { data, isLoading } = useQuery({
    queryKey: ['sensorData', sensorType],
    queryFn: () => captureSensorData(sensorType),
    refetchInterval: 5000,
    enabled: status === 'ACTIVE' || status === 'MOCK_MODE',
  });

  const icon = sensorType === 'camera' ? Camera : Mic;
  const Icon = icon;

  const getValue = () => {
    if (!data) return 'N/A';
    if (sensorType === 'camera') {
      return `${formatNumber(data.greenery_percentage)}%`;
    }
    if (sensorType === 'microphone') {
      return `${formatNumber(data.db_level)} dB`;
    }
    return 'N/A';
  };

  const getLabel = () => {
    if (!data) return '';
    if (sensorType === 'microphone' && data.noise_classification) {
      return data.noise_classification;
    }
    return '';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
            <Icon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
            {status && (
              <span className={`text-xs px-2 py-1 rounded ${getStatusBgColor(status)} ${getStatusColor(status)}`}>
                {status}
              </span>
            )}
          </div>
        </div>
        <TrendingUp className="h-5 w-5 text-gray-400" />
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-24">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400" />
        </div>
      ) : (
        <div className="space-y-2">
          <div className="text-3xl font-bold text-gray-900 dark:text-white">
            {getValue()}
          </div>
          {getLabel() && (
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {getLabel()}
            </div>
          )}
          {data?.timestamp && (
            <div className="text-xs text-gray-500 dark:text-gray-500">
              Last updated: {new Date(data.timestamp).toLocaleTimeString()}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SensorCard;
