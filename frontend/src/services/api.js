import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Sensor APIs
export const getSensorStatus = async (sensorType) => {
  const response = await api.get(`/api/sensors/${sensorType}/status`);
  return response.data;
};

export const captureSensorData = async (sensorType, params = {}) => {
  const response = await api.get(`/api/sensors/${sensorType}/capture`, { params });
  return response.data;
};

// Manager APIs
export const getManagerStatus = async () => {
  const response = await api.get('/api/sensors/manager/status');
  return response.data;
};

export const getManagerHealth = async () => {
  const response = await api.get('/api/sensors/manager/health');
  return response.data;
};

export const startManager = async () => {
  const response = await api.post('/api/sensors/manager/start');
  return response.data;
};

export const stopManager = async () => {
  const response = await api.post('/api/sensors/manager/stop');
  return response.data;
};

// Analytics APIs
export const getStatistics = async (dataType, days = 7) => {
  const response = await api.get(`/api/analytics/statistics/${dataType}`, {
    params: { days },
  });
  return response.data;
};

export const getTrends = async (dataType, period = 'daily', days = 7) => {
  const response = await api.get(`/api/analytics/trends/${dataType}`, {
    params: { period, days },
  });
  return response.data;
};

export const getAggregatedData = async (dataType, period = 'hourly', days = 1) => {
  const response = await api.get(`/api/analytics/aggregate/${dataType}`, {
    params: { period, days },
  });
  return response.data;
};

// Context Engine APIs
export const getWellnessScore = async (days = 1) => {
  const response = await api.get('/api/context/wellness_score', {
    params: { days },
  });
  return response.data;
};

export const getRecommendations = async (days = 7, limit = 5) => {
  const response = await api.get('/api/context/recommendations', {
    params: { days, limit },
  });
  return response.data;
};

export const getPatterns = async (days = 14, type = 'all') => {
  const response = await api.get('/api/context/patterns', {
    params: { days, type },
  });
  return response.data;
};

export const submitFeedback = async (feedbackData) => {
  const response = await api.post('/api/context/feedback', feedbackData);
  return response.data;
};

// Simulation APIs
export const getSimulationStatus = async () => {
  const response = await api.get('/api/simulation/status');
  return response.data;
};

export const getSimulationScenarios = async () => {
  const response = await api.get('/api/simulation/scenarios');
  return response.data;
};

export const startSimulation = async (scenario = 'calm') => {
  const response = await api.post('/api/simulation/start', { scenario });
  return response.data;
};

export const stopSimulation = async () => {
  const response = await api.post('/api/simulation/stop');
  return response.data;
};

export default api;
