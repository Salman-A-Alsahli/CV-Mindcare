// Constants
const API_ENDPOINTS = {
    live: '/api/live',
    stats: '/api/stats',
    sensors: '/api/sensors'
};

const REFRESH_INTERVAL = 5000; // 5 seconds

// Utility functions
const formatDecimal = (num) => Number(num).toFixed(1);
const formatPercentage = (num) => `${formatDecimal(num)}%`;

// Charts configuration
const createEmotionChart = (ctx, data) => {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    '#4CAF50', // happy
                    '#F44336', // angry
                    '#2196F3', // sad
                    '#FFC107', // surprised
                    '#9C27B0', // fearful
                    '#795548', // disgusted
                    '#9E9E9E'  // neutral
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
};

// API handlers
async function fetchWithTimeout(endpoint, timeout = 5000) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        const response = await fetch(endpoint, {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

// Main dashboard class
class Dashboard {
    constructor() {
        this.charts = {};
        this.data = {};
        this.initialize();
    }

    async initialize() {
        // Initial data fetch
        await this.updateData();
        
        // Set up refresh interval
        setInterval(() => this.updateData(), REFRESH_INTERVAL);
        
        // Set up event listeners
        document.getElementById('stop-collection')?.addEventListener('click', this.handleStopCollection.bind(this));
    }

    async updateData() {
        const liveData = await fetchWithTimeout(API_ENDPOINTS.live);
        if (!liveData) {
            this.updateSystemStatus('offline');
            return;
        }

        this.updateSystemStatus('online');
        this.data = liveData;
        this.updateUI();
    }

    updateSystemStatus(status) {
        const statusEl = document.getElementById('system-status');
        if (!statusEl) return;

        statusEl.textContent = status;
        statusEl.className = `status-${status}`;
    }

    updateUI() {
        // Update emotion data
        const emotionCtx = document.getElementById('emotion-chart')?.getContext('2d');
        if (emotionCtx && this.data.emotions) {
            if (!this.charts.emotion) {
                this.charts.emotion = createEmotionChart(emotionCtx, this.data.emotions);
            } else {
                this.charts.emotion.data.datasets[0].data = Object.values(this.data.emotions);
                this.charts.emotion.update();
            }
        }

        // Update stats
        const statsContainer = document.getElementById('stats-container');
        if (statsContainer && this.data.stats) {
            statsContainer.innerHTML = `
                <div class="stat-item">
                    <label>CPU Usage:</label>
                    <span>${formatPercentage(this.data.stats.cpu_percent)}</span>
                </div>
                <div class="stat-item">
                    <label>Memory Usage:</label>
                    <span>${formatPercentage(this.data.stats.memory_percent)}</span>
                </div>
            `;
        }
    }

    async handleStopCollection() {
        try {
            await fetch('/api/control/stop', { method: 'POST' });
            this.updateSystemStatus('stopped');
        } catch (error) {
            console.error('Failed to stop collection:', error);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});