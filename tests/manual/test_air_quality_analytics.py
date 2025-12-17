#!/usr/bin/env python3
"""
Test script to verify air quality analytics functionality.

This script tests the new air quality statistics features:
- Air quality data aggregation
- Statistics calculation
- Trend detection
- Anomaly detection
- Level distribution

Usage:
    python tests/manual/test_air_quality_analytics.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.analytics import Analytics, AggregationPeriod
from backend.database import init_db, insert_air_quality
from datetime import datetime, timedelta
import random


def setup_test_data():
    """Insert test air quality data."""
    print("Setting up test data...")
    init_db()
    
    # Clear existing data for clean test
    from backend.database import _get_connection
    from contextlib import closing
    
    with closing(_get_connection()) as conn:
        conn.execute("DELETE FROM air_quality")
        conn.commit()
    
    # Add varied test data
    levels = ["excellent", "good", "moderate", "poor", "hazardous"]
    for i in range(100):
        level = random.choice(levels)
        if level == "excellent":
            ppm = random.uniform(10, 50)
        elif level == "good":
            ppm = random.uniform(51, 100)
        elif level == "moderate":
            ppm = random.uniform(101, 150)
        elif level == "poor":
            ppm = random.uniform(151, 200)
        else:
            ppm = random.uniform(201, 300)
        
        raw_value = (ppm / 300.0) * 1023.0
        insert_air_quality(ppm, level, raw_value)
    
    print(f"Inserted 100 test air quality records")


def test_statistics():
    """Test statistics calculation for air quality."""
    print("\n=== Testing Air Quality Statistics ===")
    analytics = Analytics()
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    stats = analytics.calculate_statistics("air_quality", start_time=start_time, end_time=end_time)
    
    assert stats["count"] > 0, "Should have data points"
    assert stats["avg"] >= 0, "Average should be non-negative"
    assert stats["min"] >= 0, "Min should be non-negative"
    assert stats["max"] >= stats["min"], "Max should be >= min"
    
    print(f"✓ Statistics calculation passed")
    print(f"  Count: {stats['count']}")
    print(f"  Average PPM: {stats['avg']}")
    print(f"  Range: {stats['min']} - {stats['max']}")


def test_aggregation():
    """Test data aggregation for air quality."""
    print("\n=== Testing Air Quality Aggregation ===")
    analytics = Analytics()
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    # Test daily aggregation
    data = analytics.get_aggregated_data(
        "air_quality",
        AggregationPeriod.DAILY,
        start_time=start_time,
        end_time=end_time
    )
    
    assert len(data) >= 1, "Should have aggregated data"
    assert "avg" in data[0], "Should have average"
    assert "min" in data[0], "Should have min"
    assert "max" in data[0], "Should have max"
    
    print(f"✓ Aggregation passed")
    print(f"  Aggregated periods: {len(data)}")


def test_trends():
    """Test trend detection for air quality."""
    print("\n=== Testing Air Quality Trends ===")
    analytics = Analytics()
    
    trends = analytics.detect_trends("air_quality", AggregationPeriod.DAILY, days=7)
    
    assert "direction" in trends, "Should have direction"
    assert "slope" in trends, "Should have slope"
    assert trends["direction"] in ["increasing", "decreasing", "stable"], "Valid direction"
    
    print(f"✓ Trend detection passed")
    print(f"  Direction: {trends['direction']}")
    print(f"  Change: {trends.get('change_percent', 0)}%")


def test_anomalies():
    """Test anomaly detection for air quality."""
    print("\n=== Testing Air Quality Anomalies ===")
    analytics = Analytics()
    
    anomalies = analytics.detect_anomalies("air_quality", days=7, threshold_stddev=2.0)
    
    assert isinstance(anomalies, list), "Should return list"
    
    print(f"✓ Anomaly detection passed")
    print(f"  Anomalies found: {len(anomalies)}")
    if anomalies:
        print(f"  First anomaly PPM: {anomalies[0]['value']}")


def test_level_distribution():
    """Test air quality level distribution."""
    print("\n=== Testing Air Quality Level Distribution ===")
    analytics = Analytics()
    
    distribution = analytics.get_air_quality_level_distribution(days=7)
    
    assert "total_measurements" in distribution, "Should have total"
    assert "distribution" in distribution, "Should have distribution"
    assert distribution["total_measurements"] > 0, "Should have measurements"
    
    levels = distribution["distribution"]
    total_percentage = sum(level["percentage"] for level in levels.values())
    
    assert abs(total_percentage - 100.0) < 1.0, "Percentages should sum to ~100%"
    
    print(f"✓ Level distribution passed")
    print(f"  Total measurements: {distribution['total_measurements']}")
    print(f"  Distribution:")
    for level, data in levels.items():
        if data["count"] > 0:
            print(f"    {level}: {data['count']} ({data['percentage']}%)")


def test_database_air_quality_method():
    """Test Database.get_air_quality_data method."""
    print("\n=== Testing Database.get_air_quality_data ===")
    from backend.database import Database
    
    db = Database()
    data = db.get_air_quality_data()
    
    assert isinstance(data, list), "Should return list"
    assert len(data) > 0, "Should have data"
    assert len(data[0]) == 2, "Each entry should have timestamp and value"
    
    print(f"✓ Database method passed")
    print(f"  Records retrieved: {len(data)}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Air Quality Analytics Test Suite")
    print("=" * 60)
    
    try:
        setup_test_data()
        test_statistics()
        test_aggregation()
        test_trends()
        test_anomalies()
        test_level_distribution()
        test_database_air_quality_method()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
