/**
 * CV-Mindcare API Usage Examples - JavaScript/Node.js
 * 
 * This module demonstrates how to interact with the CV-Mindcare API
 * using modern JavaScript (async/await) with fetch API.
 * 
 * Requirements:
 *   - Node.js 18+ (with native fetch support)
 *   - OR npm install node-fetch (for Node.js < 18)
 * 
 * Usage:
 *   node javascript_examples.js
 */

const BASE_URL = 'http://localhost:8000';

/**
 * Helper function to make API requests
 */
async function apiRequest(endpoint, options = {}) {
    try {
        const url = `${BASE_URL}${endpoint}`;
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`Error in API request to ${endpoint}:`, error.message);
        throw error;
    }
}

/**
 * Check API health
 */
async function exampleHealthCheck() {
    console.log('\n=== Health Check Example ===');
    const data = await apiRequest('/api/health');
    console.log('Status:', data.status);
    return data;
}

/**
 * Get all sensors status
 */
async function exampleGetSensors() {
    console.log('\n=== Get Sensors Example ===');
    const data = await apiRequest('/api/sensors');
    console.log('Available Sensors:', Object.keys(data.status));
    console.log('Recent Data Points:', data.recent_data?.length || 0);
    return data;
}

/**
 * Get camera sensor status
 */
async function exampleCameraStatus() {
    console.log('\n=== Camera Sensor Status ===');
    const data = await apiRequest('/api/sensors/camera/status');
    console.log(`Status: ${data.status}, Mock Mode: ${data.mock_mode}`);
    return data;
}

/**
 * Capture greenery data from camera
 */
async function exampleCameraCapture() {
    console.log('\n=== Camera Capture Example ===');
    const data = await apiRequest('/api/sensors/camera/capture');
    console.log(`Greenery: ${data.greenery_percentage.toFixed(2)}%`);
    console.log(`Timestamp: ${data.timestamp}`);
    return data;
}

/**
 * Submit manual greenery data
 */
async function examplePostGreeneryData() {
    console.log('\n=== Post Greenery Data Example ===');
    const data = await apiRequest('/api/sensors/camera/greenery', {
        method: 'POST',
        body: JSON.stringify({
            greenery_percentage: 35.5
        })
    });
    console.log('Message:', data.message);
    return data;
}

/**
 * Capture microphone data
 */
async function exampleMicrophoneCapture(duration = 1.0) {
    console.log(`\n=== Microphone Capture Example (${duration}s) ===`);
    const data = await apiRequest(
        `/api/sensors/microphone/capture?duration=${duration}`
    );
    console.log(`Noise Level: ${data.db_level.toFixed(2)} dB`);
    console.log(`Classification: ${data.noise_classification}`);
    return data;
}

/**
 * Get air quality sensor status
 */
async function exampleAirQualityStatus() {
    console.log('\n=== Air Quality Sensor Status ===');
    const data = await apiRequest('/api/sensors/air_quality/status');
    console.log(`Status: ${data.status}, Mock Mode: ${data.mock_mode}`);
    return data;
}

/**
 * Capture air quality measurement
 */
async function exampleAirQualityCapture() {
    console.log('\n=== Air Quality Capture Example ===');
    const data = await apiRequest('/api/sensors/air_quality/capture');
    console.log(`PPM: ${data.ppm.toFixed(2)}`);
    console.log(`Quality Level: ${data.air_quality_level}`);
    return data;
}

/**
 * Get sensor manager status
 */
async function exampleSensorManagerStatus() {
    console.log('\n=== Sensor Manager Status ===');
    const data = await apiRequest('/api/sensors/manager/status');
    console.log(`Manager Status: ${data.status}`);
    console.log(`Running: ${data.running}`);
    console.log('Active Sensors:', Object.keys(data.sensors).join(', '));
    return data;
}

/**
 * Start sensor manager
 */
async function exampleStartSensorManager() {
    console.log('\n=== Start Sensor Manager ===');
    const data = await apiRequest('/api/sensors/manager/start', {
        method: 'POST'
    });
    console.log('Message:', data.message);
    console.log('Status:', data.status);
    return data;
}

/**
 * Get aggregated analytics data
 */
async function exampleGetAnalyticsAggregated(sensorType = 'greenery', period = 'hourly') {
    console.log(`\n=== Analytics: ${sensorType} - ${period} ===`);
    const data = await apiRequest(
        `/api/analytics/aggregated?sensor_type=${sensorType}&period=${period}`
    );
    console.log('Data Points:', data.data?.length || 0);
    if (data.data && data.data.length > 0) {
        console.log('First Point:', JSON.stringify(data.data[0], null, 2));
    }
    return data;
}

/**
 * Get statistical analysis
 */
async function exampleGetAnalyticsStatistics(sensorType = 'greenery') {
    console.log(`\n=== Analytics Statistics: ${sensorType} ===`);
    const data = await apiRequest(
        `/api/analytics/statistics?sensor_type=${sensorType}`
    );
    console.log(`Average: ${data.average?.toFixed(2) || 'N/A'}`);
    console.log(`Min: ${data.min?.toFixed(2) || 'N/A'}`);
    console.log(`Max: ${data.max?.toFixed(2) || 'N/A'}`);
    console.log(`Std Dev: ${data.std_dev?.toFixed(2) || 'N/A'}`);
    return data;
}

/**
 * Get trends analysis
 */
async function exampleGetTrends(sensorType = 'greenery', periodDays = 7) {
    console.log(`\n=== Trends Analysis: ${sensorType} (${periodDays} days) ===`);
    const data = await apiRequest(
        `/api/analytics/trends?sensor_type=${sensorType}&period_days=${periodDays}`
    );
    console.log(`Direction: ${data.direction || 'N/A'}`);
    console.log(`Slope: ${data.slope?.toFixed(4) || 'N/A'}`);
    console.log(`Message: ${data.message || 'N/A'}`);
    return data;
}

/**
 * Get correlation analysis
 */
async function exampleGetCorrelation() {
    console.log('\n=== Correlation Analysis: Greenery vs Noise ===');
    const data = await apiRequest('/api/analytics/correlation');
    console.log(`Correlation: ${data.correlation?.toFixed(4) || 'N/A'}`);
    console.log(`Strength: ${data.strength || 'N/A'}`);
    console.log(`Message: ${data.message || 'N/A'}`);
    return data;
}

/**
 * WebSocket live streaming example
 */
async function exampleWebSocketStreaming() {
    console.log('\n=== WebSocket Live Streaming ===');
    console.log('Connecting to WebSocket...');
    
    const ws = new WebSocket('ws://localhost:8000/ws/live');
    
    ws.onopen = () => {
        console.log('WebSocket connected!');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received:', {
            type: data.type,
            timestamp: data.timestamp,
            sensors: Object.keys(data.sensors || {})
        });
        
        // Auto-close after receiving 5 messages
        if (ws.messageCount === undefined) {
            ws.messageCount = 0;
        }
        ws.messageCount++;
        
        if (ws.messageCount >= 5) {
            console.log('Received 5 messages, closing connection...');
            ws.close();
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
        console.log('WebSocket connection closed');
    };
    
    // Keep the script running for WebSocket
    await new Promise(resolve => setTimeout(resolve, 30000));
}

/**
 * Run all examples
 */
async function runAllExamples() {
    console.log('='.repeat(60));
    console.log('CV-Mindcare API Examples - JavaScript');
    console.log('='.repeat(60));
    
    try {
        // Check if API is available
        await exampleHealthCheck();
        
        // Sensor examples
        await exampleGetSensors();
        await exampleCameraStatus();
        await exampleCameraCapture();
        await examplePostGreeneryData();
        await exampleMicrophoneCapture(0.5);
        await exampleAirQualityStatus();
        await exampleAirQualityCapture();
        
        // Sensor manager examples
        await exampleSensorManagerStatus();
        // await exampleStartSensorManager(); // Uncomment to actually start
        
        // Analytics examples
        await exampleGetAnalyticsAggregated('greenery', 'hourly');
        await exampleGetAnalyticsStatistics('greenery');
        await exampleGetTrends('greenery', 7);
        await exampleGetCorrelation();
        
        console.log('\n' + '='.repeat(60));
        console.log('All examples completed successfully!');
        console.log('='.repeat(60));
        
        // Uncomment to test WebSocket streaming
        // await exampleWebSocketStreaming();
        
    } catch (error) {
        console.error('\nError running examples:', error.message);
        console.log('\nPlease ensure the API server is running:');
        console.log('  uvicorn backend.app:app --reload');
    }
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    runAllExamples().catch(console.error);
}

// Export for use as module
export {
    exampleHealthCheck,
    exampleGetSensors,
    exampleCameraStatus,
    exampleCameraCapture,
    examplePostGreeneryData,
    exampleMicrophoneCapture,
    exampleAirQualityStatus,
    exampleAirQualityCapture,
    exampleSensorManagerStatus,
    exampleStartSensorManager,
    exampleGetAnalyticsAggregated,
    exampleGetAnalyticsStatistics,
    exampleGetTrends,
    exampleGetCorrelation,
    exampleWebSocketStreaming
};
