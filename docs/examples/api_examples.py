"""
CV-Mindcare API Usage Examples - Python Client

This module demonstrates how to interact with the CV-Mindcare API
using Python's requests library. Examples cover all major endpoints
for sensors, analytics, WebSocket streaming, and more.

Requirements:
    pip install requests websockets

Usage:
    python api_examples.py
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# Base URL for the API (adjust if needed)
BASE_URL = "http://localhost:8000"


def example_health_check():
    """Check if the API is online and healthy."""
    print("\n=== Health Check Example ===")
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200


def example_get_sensors():
    """Get status of all sensors and recent data."""
    print("\n=== Get Sensors Example ===")
    
    response = requests.get(f"{BASE_URL}/api/sensors")
    data = response.json()
    
    print(f"Status Code: {response.status_code}")
    print(f"Sensors Available: {json.dumps(data['status'], indent=2)}")
    print(f"Recent Data Points: {len(data.get('recent_data', []))}")
    
    return data


def example_camera_status():
    """Get camera sensor status."""
    print("\n=== Camera Sensor Status ===")
    
    response = requests.get(f"{BASE_URL}/api/sensors/camera/status")
    data = response.json()
    
    print(f"Status: {data['status']}")
    print(f"Mock Mode: {data['mock_mode']}")
    print(f"Backend: {data.get('backend', 'N/A')}")
    
    return data


def example_camera_capture():
    """Capture greenery data from camera."""
    print("\n=== Camera Capture Example ===")
    
    response = requests.get(f"{BASE_URL}/api/sensors/camera/capture")
    data = response.json()
    
    print(f"Greenery Percentage: {data['greenery_percentage']:.2f}%")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Status: {data['status']}")
    
    return data


def example_post_greenery_data():
    """Manually submit greenery data."""
    print("\n=== Post Greenery Data Example ===")
    
    payload = {
        "greenery_percentage": 35.5
    }
    
    response = requests.post(
        f"{BASE_URL}/api/sensors/camera/greenery",
        json=payload
    )
    data = response.json()
    
    print(f"Status Code: {response.status_code}")
    print(f"Message: {data['message']}")
    
    return data


def example_microphone_capture(duration: float = 1.0):
    """Capture audio and analyze noise level."""
    print(f"\n=== Microphone Capture Example (duration={duration}s) ===")
    
    response = requests.get(
        f"{BASE_URL}/api/sensors/microphone/capture",
        params={"duration": duration}
    )
    data = response.json()
    
    print(f"Noise Level (dB): {data['db_level']:.2f}")
    print(f"Classification: {data['noise_classification']}")
    print(f"Timestamp: {data['timestamp']}")
    
    return data


def example_air_quality_status():
    """Get air quality sensor status."""
    print("\n=== Air Quality Sensor Status ===")
    
    response = requests.get(f"{BASE_URL}/api/sensors/air_quality/status")
    data = response.json()
    
    print(f"Status: {data['status']}")
    print(f"Mock Mode: {data['mock_mode']}")
    print(f"Calibrated: {data.get('calibrated', False)}")
    
    return data


def example_air_quality_capture():
    """Capture air quality measurement."""
    print("\n=== Air Quality Capture Example ===")
    
    response = requests.get(f"{BASE_URL}/api/sensors/air_quality/capture")
    data = response.json()
    
    print(f"PPM: {data['ppm']:.2f}")
    print(f"Air Quality Level: {data['air_quality_level']}")
    print(f"Timestamp: {data['timestamp']}")
    
    return data


def example_sensor_manager_status():
    """Get sensor manager status."""
    print("\n=== Sensor Manager Status ===")
    
    response = requests.get(f"{BASE_URL}/api/sensors/manager/status")
    data = response.json()
    
    print(f"Manager Status: {data['status']}")
    print(f"Running: {data['running']}")
    print(f"Active Sensors: {', '.join(data['sensors'].keys())}")
    
    for sensor_name, sensor_data in data['sensors'].items():
        print(f"  - {sensor_name}: {sensor_data['status']}")
    
    return data


def example_start_sensor_manager():
    """Start all sensors via sensor manager."""
    print("\n=== Start Sensor Manager ===")
    
    response = requests.post(f"{BASE_URL}/api/sensors/manager/start")
    data = response.json()
    
    print(f"Status Code: {response.status_code}")
    print(f"Message: {data['message']}")
    print(f"Manager Status: {data['status']}")
    
    return data


def example_get_analytics_aggregated(sensor_type: str = "greenery", period: str = "hourly"):
    """Get aggregated sensor data."""
    print(f"\n=== Analytics: {sensor_type.title()} - {period.title()} ===")
    
    response = requests.get(
        f"{BASE_URL}/api/analytics/aggregated",
        params={"sensor_type": sensor_type, "period": period}
    )
    data = response.json()
    
    print(f"Data Points: {len(data.get('data', []))}")
    if data.get('data'):
        first_point = data['data'][0]
        print(f"First Point: {json.dumps(first_point, indent=2)}")
    
    return data


def example_get_analytics_statistics(sensor_type: str = "greenery"):
    """Get statistical analysis of sensor data."""
    print(f"\n=== Analytics Statistics: {sensor_type.title()} ===")
    
    response = requests.get(
        f"{BASE_URL}/api/analytics/statistics",
        params={"sensor_type": sensor_type}
    )
    data = response.json()
    
    print(f"Average: {data.get('average', 0):.2f}")
    print(f"Min: {data.get('min', 0):.2f}")
    print(f"Max: {data.get('max', 0):.2f}")
    print(f"Std Dev: {data.get('std_dev', 0):.2f}")
    print(f"Total Points: {data.get('count', 0)}")
    
    return data


def example_get_trends(sensor_type: str = "greenery", period_days: int = 7):
    """Analyze trends in sensor data."""
    print(f"\n=== Trends Analysis: {sensor_type.title()} ({period_days} days) ===")
    
    response = requests.get(
        f"{BASE_URL}/api/analytics/trends",
        params={"sensor_type": sensor_type, "period_days": period_days}
    )
    data = response.json()
    
    print(f"Trend Direction: {data.get('direction', 'N/A')}")
    print(f"Slope: {data.get('slope', 0):.4f}")
    print(f"Message: {data.get('message', 'N/A')}")
    
    return data


def example_get_correlation():
    """Analyze correlation between greenery and noise."""
    print("\n=== Correlation Analysis: Greenery vs Noise ===")
    
    response = requests.get(f"{BASE_URL}/api/analytics/correlation")
    data = response.json()
    
    print(f"Correlation Coefficient: {data.get('correlation', 0):.4f}")
    print(f"Strength: {data.get('strength', 'N/A')}")
    print(f"Message: {data.get('message', 'N/A')}")
    
    return data


def run_all_examples():
    """Run all API examples in sequence."""
    print("=" * 60)
    print("CV-Mindcare API Examples")
    print("=" * 60)
    
    try:
        # Basic health check
        if not example_health_check():
            print("\nERROR: API is not responding. Is the server running?")
            print("Start the server with: uvicorn backend.app:app --reload")
            return
        
        # Sensor examples
        example_get_sensors()
        example_camera_status()
        example_camera_capture()
        example_post_greenery_data()
        example_microphone_capture(duration=0.5)
        example_air_quality_status()
        example_air_quality_capture()
        
        # Sensor manager examples
        example_sensor_manager_status()
        # example_start_sensor_manager()  # Uncomment to actually start
        
        # Analytics examples
        example_get_analytics_aggregated("greenery", "hourly")
        example_get_analytics_statistics("greenery")
        example_get_trends("greenery", 7)
        example_get_correlation()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to API server.")
        print("Please ensure the server is running on http://localhost:8000")
        print("Start with: uvicorn backend.app:app --reload")
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")


if __name__ == "__main__":
    run_all_examples()
