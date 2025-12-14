import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Play, Square, Zap, AlertTriangle, Activity } from 'lucide-react';
import {
  getSimulationStatus,
  getSimulationScenarios,
  startSimulation,
  stopSimulation,
} from '../services/api';

function SimulationControl() {
  const queryClient = useQueryClient();
  const [selectedScenario, setSelectedScenario] = useState('calm');

  // Fetch simulation status
  const { data: simulationStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['simulationStatus'],
    queryFn: getSimulationStatus,
    refetchInterval: 3000,
  });

  // Fetch available scenarios
  const { data: scenariosData, isLoading: scenariosLoading } = useQuery({
    queryKey: ['simulationScenarios'],
    queryFn: getSimulationScenarios,
  });

  // Start simulation mutation
  const startMutation = useMutation({
    mutationFn: (scenario) => startSimulation(scenario),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['simulationStatus'] });
      queryClient.invalidateQueries({ queryKey: ['managerStatus'] });
    },
  });

  // Stop simulation mutation
  const stopMutation = useMutation({
    mutationFn: stopSimulation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['simulationStatus'] });
      queryClient.invalidateQueries({ queryKey: ['managerStatus'] });
    },
  });

  const handleStart = () => {
    startMutation.mutate(selectedScenario);
  };

  const handleStop = () => {
    stopMutation.mutate();
  };

  if (statusLoading || scenariosLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  const isActive = simulationStatus?.active || false;
  const currentScenario = simulationStatus?.scenario || 'calm';
  const scenarios = scenariosData?.scenarios || [];

  // Scenario icons and colors
  const scenarioConfig = {
    calm: { 
      icon: '🌿', 
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      borderColor: 'border-green-500',
    },
    stress: { 
      icon: '⚠️', 
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      borderColor: 'border-red-500',
    },
    dynamic: { 
      icon: '🔄', 
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      borderColor: 'border-blue-500',
    },
    custom: { 
      icon: '⚙️', 
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      borderColor: 'border-purple-500',
    },
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Zap className={`h-5 w-5 ${isActive ? 'text-yellow-500 animate-pulse' : 'text-gray-400'}`} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Simulation Engine
            </h3>
          </div>
          
          {isActive && (
            <div className="flex items-center space-x-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-yellow-500"></span>
              </span>
              <span className="text-sm font-medium text-yellow-600 dark:text-yellow-400">
                SIMULATION ACTIVE
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Status Alert */}
        {isActive && (
          <div className="flex items-start space-x-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                Not Real Data - Simulation Mode Active
              </p>
              <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                All sensor readings are simulated. Real hardware is disconnected.
              </p>
            </div>
          </div>
        )}

        {/* Mode Toggle */}
        <div className="flex items-center justify-between">
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Mode
            </label>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {isActive ? 'Generating simulated sensor data' : 'Using live sensor hardware'}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`text-sm ${!isActive ? 'font-medium text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}`}>
              Live
            </span>
            <button
              onClick={isActive ? handleStop : handleStart}
              disabled={startMutation.isPending || stopMutation.isPending}
              className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
                isActive ? 'bg-yellow-600' : 'bg-gray-200 dark:bg-gray-700'
              } ${startMutation.isPending || stopMutation.isPending ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  isActive ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
            <span className={`text-sm ${isActive ? 'font-medium text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}`}>
              Simulation
            </span>
          </div>
        </div>

        {/* Scenario Selector */}
        {!isActive && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Select Scenario
            </label>
            <div className="grid grid-cols-2 gap-2">
              {scenarios.map((scenario) => {
                const config = scenarioConfig[scenario.id] || scenarioConfig.calm;
                const isSelected = selectedScenario === scenario.id;
                
                return (
                  <button
                    key={scenario.id}
                    onClick={() => setSelectedScenario(scenario.id)}
                    className={`p-3 rounded-lg border-2 transition-all text-left ${
                      isSelected
                        ? `${config.borderColor} ${config.bgColor}`
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-lg">{config.icon}</span>
                      <span className="font-medium text-sm text-gray-900 dark:text-white">
                        {scenario.name}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {scenario.description.split('.')[0]}
                    </p>
                    <div className="mt-2 flex flex-wrap gap-1">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                        {scenario.greenery}
                      </span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                        {scenario.noise}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Current Scenario Info (when active) */}
        {isActive && (
          <div className={`p-3 rounded-lg ${scenarioConfig[currentScenario]?.bgColor || 'bg-gray-50 dark:bg-gray-900/20'}`}>
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-lg">{scenarioConfig[currentScenario]?.icon || '⚙️'}</span>
              <span className="font-medium text-sm text-gray-900 dark:text-white">
                Current Scenario: {scenarios.find(s => s.id === currentScenario)?.name || currentScenario}
              </span>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {scenarios.find(s => s.id === currentScenario)?.description || 'Simulating sensor data'}
            </p>
            {simulationStatus?.uptime && (
              <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Running for {Math.floor(simulationStatus.uptime)}s
              </div>
            )}
          </div>
        )}

        {/* Control Buttons */}
        <div className="flex space-x-2">
          {!isActive ? (
            <button
              onClick={handleStart}
              disabled={startMutation.isPending}
              className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
            >
              <Play className="h-4 w-4" />
              <span>{startMutation.isPending ? 'Starting...' : 'Start Simulation'}</span>
            </button>
          ) : (
            <button
              onClick={handleStop}
              disabled={stopMutation.isPending}
              className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
            >
              <Square className="h-4 w-4" />
              <span>{stopMutation.isPending ? 'Stopping...' : 'Stop Simulation'}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default SimulationControl;
