import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Lightbulb, ThumbsUp, ThumbsDown, Check } from 'lucide-react';
import { getRecommendations, submitFeedback } from '../services/api';
import { getPriorityColor } from '../utils/formatters';

function Recommendations() {
  const [days, setDays] = useState(7);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['recommendations', days],
    queryFn: () => getRecommendations(days, 10),
  });

  const feedbackMutation = useMutation({
    mutationFn: submitFeedback,
    onSuccess: () => {
      queryClient.invalidateQueries(['recommendations']);
    },
  });

  const handleFeedback = (recommendationId, helpful) => {
    feedbackMutation.mutate({
      recommendation_id: recommendationId,
      helpful,
      implemented: false,
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400" />
      </div>
    );
  }

  const recommendations = data?.recommendations || [];

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          AI-Powered Recommendations
        </h2>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        >
          <option value="1">Last 24 hours</option>
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
        </select>
      </div>

      {/* Summary */}
      {data?.summary && (
        <div className="bg-primary-50 dark:bg-primary-900 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-700 dark:text-gray-200">
              Total recommendations: <strong>{data.summary.total}</strong>
            </span>
            <div className="flex space-x-4 text-sm">
              <span className="text-red-600 dark:text-red-400">
                High: {data.summary.by_priority?.high || 0}
              </span>
              <span className="text-yellow-600 dark:text-yellow-400">
                Medium: {data.summary.by_priority?.medium || 0}
              </span>
              <span className="text-blue-600 dark:text-blue-400">
                Low: {data.summary.by_priority?.low || 0}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations List */}
      {recommendations.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
          <Lightbulb className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            No recommendations at this time. Keep monitoring to receive personalized suggestions!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec, index) => (
            <div
              key={rec.id || index}
              className="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(rec.priority)}`}>
                      {rec.priority?.toUpperCase()}
                    </span>
                    <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                      {rec.type}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {rec.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {rec.description}
                  </p>
                </div>
              </div>

              {/* Actions */}
              {rec.actions && rec.actions.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Suggested Actions:
                  </h4>
                  <ul className="space-y-2">
                    {rec.actions.map((action, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <Check className="h-5 w-5 text-primary-600 dark:text-primary-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Impact */}
              {rec.impact && (
                <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900 rounded-lg">
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    <strong>Expected Impact:</strong> {rec.impact}
                  </p>
                </div>
              )}

              {/* Feedback Buttons */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  Confidence: {(rec.confidence * 100).toFixed(0)}%
                </span>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleFeedback(rec.id, true)}
                    className="px-3 py-1 text-sm bg-green-100 hover:bg-green-200 dark:bg-green-900 dark:hover:bg-green-800 text-green-700 dark:text-green-300 rounded-lg transition-colors flex items-center space-x-1"
                  >
                    <ThumbsUp className="h-4 w-4" />
                    <span>Helpful</span>
                  </button>
                  <button
                    onClick={() => handleFeedback(rec.id, false)}
                    className="px-3 py-1 text-sm bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:hover:bg-red-800 text-red-700 dark:text-red-300 rounded-lg transition-colors flex items-center space-x-1"
                  >
                    <ThumbsDown className="h-4 w-4" />
                    <span>Not Helpful</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Recommendations;
