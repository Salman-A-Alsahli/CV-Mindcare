# Frontend

This directory contains the web dashboard for CV-Mindcare.

## Structure

- `index.html` - Main HTML entry point
- `css/` - Stylesheets
  - `styles.css` - Custom CSS beyond Tailwind
- `js/` - JavaScript modules
  - `dashboard.js` - Main dashboard logic and API interaction
- `src/` - Source files for React/modern framework (if applicable)

## Features

### Dashboard Components
- **Live Metrics Display** - Real-time sensor data visualization
- **Emotion Chart** - Doughnut chart showing emotion distribution
- **System Stats** - CPU and memory usage indicators
- **Sensor Status** - Camera, microphone, and resource availability
- **Control Panel** - Stop/start data collection

## Technology Stack

- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Data visualization
- **Vanilla JavaScript** - Dashboard logic and API polling

## API Integration

The dashboard polls the backend API every 5 seconds:
- `GET /api/live` - Fetches current readings, emotions, and stats
- `GET /api/stats` - Retrieves system statistics
- `GET /api/sensors` - Gets sensor status
- `POST /api/control/stop` - Stops data collection

## Running the Frontend

### Development Server
```bash
cd frontend
npm install
npm run dev
```

### Production Build
```bash
npm run build
npm run serve
```

### Standalone Mode
Simply open `index.html` in a browser, ensuring the backend is running at `http://localhost:8000`.

## Configuration

- API endpoint base URL can be configured in `js/dashboard.js`
- Refresh interval: 5000ms (5 seconds)
- Chart colors and themes are customizable in the Chart.js configuration

## Dependencies

- Tailwind CSS
- Chart.js
- Modern browser with ES6+ support
