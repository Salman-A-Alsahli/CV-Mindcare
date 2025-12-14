import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Activity, RefreshCw } from 'lucide-react';
import SensorCard from './SensorCard';
import WellnessScore from './WellnessScore';
import Charts from './Charts';
import Recommendations from './Recommendations';
import PatternInsights from './PatternInsights';
import SimulationControl from './SimulationControl';
import { getManagerStatus, getManagerHealth, startManager } from '../services/api';

function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshInterval, setRefreshInterval] = useState(5000);

  // Fetch manager status
  const { data: managerStatus, isLoading: statusLoading, refetch: refetchStatus } = useQuery({
    queryKey: ['managerStatus'],
    queryFn: getManagerStatus,
    refetchInterval: refreshInterval,
  });

  // Fetch manager health
  const { data: managerHealth, isLoading: healthLoading } = useQuery({
    queryKey: ['managerHealth'],
    queryFn: getManagerHealth,
    refetchInterval: refreshInterval,
  });

  const handleStartManager = async () => {
    try {
      await startManager();
      refetchStatus();
    } catch (error) {
      console.error('Failed to start manager:', error);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'analytics', label: 'Analytics' },
    { id: 'recommendations', label: 'Recommendations' },
    { id: 'patterns', label: 'Patterns' },
  ];

  if (statusLoading || healthLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-primary-600 dark:text-primary-400" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading dashboard...</span>
      </div>
    );
  }

  const isRunning = managerStatus?.manager?.status === 'running';
  const isSimulationMode = managerStatus?.manager?.simulation_mode || false;

  return (
    <div className="space-y-6">
      {/* Status Bar */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`h-3 w-3 rounded-full ${isRunning ? (isSimulationMode ? 'bg-yellow-500 animate-pulse' : 'bg-green-500 animate-pulse') : 'bg-gray-400'}`} />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              System Status: <span className="font-medium text-gray-900 dark:text-white">
                {isRunning ? (isSimulationMode ? 'Simulation' : 'Active') : 'Inactive'}
              </span>
            </span>
            {managerStatus?.manager?.uptime && (
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Uptime: {Math.floor(managerStatus.manager.uptime)}s
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {!isRunning && (
              <button
                onClick={handleStartManager}
                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
              >
                Start Monitoring
              </button>
            )}
            <button
              onClick={() => refetchStatus()}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <RefreshCw className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Simulation Control Panel */}
      <SimulationControl />

      {/* Tab Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Wellness Score */}
              <WellnessScore />

              {/* Sensor Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <SensorCard
                  sensorType="camera"
                  title="Camera / Greenery"
                  status={managerStatus?.sensors?.camera?.status}
                />
                <SensorCard
                  sensorType="microphone"
                  title="Microphone / Noise"
                  status={managerStatus?.sensors?.microphone?.status}
                />
              </div>

              {/* Health Score */}
              {managerHealth && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                    System Health
                  </h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Health Score:</span>
                      <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                        {managerHealth.health_score}/100
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-primary-600 dark:bg-primary-400 h-2 rounded-full transition-all"
                        style={{ width: `${managerHealth.health_score}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'analytics' && <Charts />}
          {activeTab === 'recommendations' && <Recommendations />}
          {activeTab === 'patterns' && <PatternInsights />}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
