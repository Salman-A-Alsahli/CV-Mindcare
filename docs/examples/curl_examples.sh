#!/bin/bash
#
# CV-Mindcare API Usage Examples - cURL Commands
#
# This script demonstrates how to interact with the CV-Mindcare API
# using cURL from the command line. All endpoints are covered.
#
# Usage:
#   chmod +x curl_examples.sh
#   ./curl_examples.sh
#

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "CV-Mindcare API - cURL Examples"
echo "=========================================="
echo ""

# ==========================================
# Health & Status Endpoints
# ==========================================

echo "=== Health Check ==="
curl -s "$BASE_URL/api/health" | jq .
echo ""

echo "=== Root Endpoint ==="
curl -s "$BASE_URL/" | jq .
echo ""

# ==========================================
# Sensor Endpoints
# ==========================================

echo "=== Get All Sensors Status ==="
curl -s "$BASE_URL/api/sensors" | jq .
echo ""

echo "=== Camera Sensor Status ==="
curl -s "$BASE_URL/api/sensors/camera/status" | jq .
echo ""

echo "=== Capture Camera Data (Greenery) ==="
curl -s "$BASE_URL/api/sensors/camera/capture" | jq .
echo ""

echo "=== Submit Manual Greenery Data ==="
curl -s -X POST "$BASE_URL/api/sensors/camera/greenery" \
  -H "Content-Type: application/json" \
  -d '{"greenery_percentage": 35.5}' | jq .
echo ""

echo "=== Microphone Sensor Status ==="
curl -s "$BASE_URL/api/sensors/microphone/status" | jq .
echo ""

echo "=== Capture Microphone Data (Noise Level) ==="
curl -s "$BASE_URL/api/sensors/microphone/capture?duration=1.0" | jq .
echo ""

echo "=== Submit Manual Noise Data ==="
curl -s -X POST "$BASE_URL/api/sensors/microphone/noise" \
  -H "Content-Type: application/json" \
  -d '{"db_level": 45.5}' | jq .
echo ""

echo "=== Air Quality Sensor Status ==="
curl -s "$BASE_URL/api/sensors/air_quality/status" | jq .
echo ""

echo "=== Capture Air Quality Data ==="
curl -s "$BASE_URL/api/sensors/air_quality/capture" | jq .
echo ""

echo "=== Submit Manual Air Quality Data ==="
curl -s -X POST "$BASE_URL/api/sensors/air_quality/data" \
  -H "Content-Type: application/json" \
  -d '{"ppm": 400.5, "air_quality_level": "Good"}' | jq .
echo ""

# ==========================================
# Sensor Manager Endpoints
# ==========================================

echo "=== Sensor Manager Status ==="
curl -s "$BASE_URL/api/sensors/manager/status" | jq .
echo ""

echo "=== Sensor Manager Health ==="
curl -s "$BASE_URL/api/sensors/manager/health" | jq .
echo ""

echo "=== Start Sensor Manager ==="
curl -s -X POST "$BASE_URL/api/sensors/manager/start" | jq .
echo ""

echo "=== Update Sensor Manager Config ==="
curl -s -X PUT "$BASE_URL/api/sensors/manager/config" \
  -H "Content-Type: application/json" \
  -d '{"polling_interval": 10.0}' | jq .
echo ""

echo "=== Stop Sensor Manager ==="
curl -s -X POST "$BASE_URL/api/sensors/manager/stop" | jq .
echo ""

# ==========================================
# Analytics Endpoints
# ==========================================

echo "=== Get Aggregated Data (Greenery - Hourly) ==="
curl -s "$BASE_URL/api/analytics/aggregated?sensor_type=greenery&period=hourly" | jq .
echo ""

echo "=== Get Aggregated Data (Noise - Daily) ==="
curl -s "$BASE_URL/api/analytics/aggregated?sensor_type=noise&period=daily" | jq .
echo ""

echo "=== Get Statistics (Greenery) ==="
curl -s "$BASE_URL/api/analytics/statistics?sensor_type=greenery" | jq .
echo ""

echo "=== Get Statistics (Noise) ==="
curl -s "$BASE_URL/api/analytics/statistics?sensor_type=noise" | jq .
echo ""

echo "=== Get Trends (Greenery - 7 days) ==="
curl -s "$BASE_URL/api/analytics/trends?sensor_type=greenery&period_days=7" | jq .
echo ""

echo "=== Get Anomalies (Greenery) ==="
curl -s "$BASE_URL/api/analytics/anomalies?sensor_type=greenery&threshold=2.0" | jq .
echo ""

echo "=== Get Correlation (Greenery vs Noise) ==="
curl -s "$BASE_URL/api/analytics/correlation" | jq .
echo ""

# ==========================================
# Legacy Endpoints (Compatibility)
# ==========================================

echo "=== Get Recent Sensor Data ==="
curl -s "$BASE_URL/api/sensors" | jq '.recent_data'
echo ""

echo "=== Get Face Detection Data ==="
curl -s "$BASE_URL/api/face" | jq .
echo ""

echo "=== Submit Face Detection Data ==="
curl -s -X POST "$BASE_URL/api/face" \
  -H "Content-Type: application/json" \
  -d '{"faces_detected": 1}' | jq .
echo ""

echo "=== Get Sound Analysis Data ==="
curl -s "$BASE_URL/api/sound" | jq .
echo ""

echo "=== Submit Sound Analysis Data ==="
curl -s -X POST "$BASE_URL/api/sound" \
  -H "Content-Type: application/json" \
  -d '{"avg_db": 50.0}' | jq .
echo ""

echo "=== Get System Statistics ==="
curl -s "$BASE_URL/api/stats" | jq .
echo ""

echo "=== Get Live Data ==="
curl -s "$BASE_URL/api/live" | jq .
echo ""

# ==========================================
# Air Quality Historical Data
# ==========================================

echo "=== Get Recent Air Quality Data ==="
curl -s "$BASE_URL/api/air_quality/recent?limit=10" | jq .
echo ""

echo "=== Get All Air Quality Data ==="
curl -s "$BASE_URL/api/air_quality" | jq .
echo ""

echo "=========================================="
echo "All Examples Completed!"
echo "=========================================="
echo ""
echo "Note: Install jq for pretty JSON output:"
echo "  Ubuntu/Debian: sudo apt install jq"
echo "  macOS: brew install jq"
echo ""
echo "For WebSocket examples, see websocket_client.py"
