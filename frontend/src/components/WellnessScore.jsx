import { useQuery } from '@tantml:query';
import { Heart, TrendingUp, TrendingDown } from 'lucide-react';
import { getWellnessScore } from '../services/api';
import { getRatingColor } from '../utils/formatters';

function WellnessScore() {
  const { data, isLoading } = useQuery({
    queryKey: ['wellnessScore'],
    queryFn: () => getWellnessScore(1),
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="animate-pulse h-32" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <p className="text-center text-gray-500 dark:text-gray-400">
          Collecting wellness data...
        </p>
      </div>
    );
  }

  const { score, rating, components, message, compared_to_baseline } = data;
  const isImproving = compared_to_baseline > 0;

  return (
    <div className="bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900 dark:to-primary-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
            <Heart className="h-8 w-8 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Wellness Score</h2>
            <p className={`text-sm font-medium ${getRatingColor(rating)}`}>{rating}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-5xl font-bold text-primary-600 dark:text-primary-400">{score}</div>
          <div className="text-sm text-gray-600 dark:text-gray-300">out of 100</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
          <div
            className="bg-primary-600 dark:bg-primary-400 h-3 rounded-full transition-all duration-500"
            style={{ width: `${score}%` }}
          />
        </div>
      </div>

      {/* Components Breakdown */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">Greenery</div>
          <div className="text-xl font-bold text-gray-900 dark:text-white">
            {components?.greenery_score || 0}
          </div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">Noise</div>
          <div className="text-xl font-bold text-gray-900 dark:text-white">
            {components?.noise_score || 0}
          </div>
        </div>
        <div className="text-center">
          <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">Trends</div>
          <div className="text-xl font-bold text-gray-900 dark:text-white">
            {components?.trend_score || 0}
          </div>
        </div>
      </div>

      {/* Message and Trend */}
      <div className="space-y-2">
        <p className="text-sm text-gray-700 dark:text-gray-200">{message}</p>
        {compared_to_baseline !== undefined && (
          <div className="flex items-center space-x-2">
            {isImproving ? (
              <TrendingUp className="h-4 w-4 text-green-600 dark:text-green-400" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600 dark:text-red-400" />
            )}
            <span className={`text-sm font-medium ${isImproving ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              {isImproving ? '+' : ''}{compared_to_baseline.toFixed(1)} vs baseline
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export default WellnessScore;
