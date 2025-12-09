"""Tests for analytics module."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import statistics

from backend.analytics import (
    Analytics,
    AggregationPeriod,
    TrendDirection
)


class TestAnalytics:
    """Test suite for Analytics class."""
    
    @pytest.fixture
    def analytics(self):
        """Create analytics instance with in-memory database."""
        return Analytics(db_path=":memory:")
    
    @pytest.fixture
    def sample_data(self):
        """Generate sample sensor data."""
        now = datetime.now()
        return [
            {'timestamp': now - timedelta(hours=i), 'value': 20.0 + i}
            for i in range(10)
        ]
    
    def test_initialization(self, analytics):
        """Test analytics engine initialization."""
        assert analytics is not None
        assert analytics.db_path is not None
        assert analytics.TREND_THRESHOLD == 0.1
        assert analytics.ANOMALY_STDDEV_THRESHOLD == 2.0
        assert analytics.MIN_DATA_POINTS == 3
    
    def test_get_aggregated_data_hourly(self, analytics, sample_data):
        """Test hourly data aggregation."""
        with patch.object(analytics, '_get_raw_data', return_value=sample_data):
            result = analytics.get_aggregated_data(
                data_type='greenery',
                period=AggregationPeriod.HOURLY
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Check aggregation structure
            for item in result:
                assert 'timestamp' in item
                assert 'avg' in item
                assert 'min' in item
                assert 'max' in item
                assert 'count' in item
                assert 'stddev' in item
    
    def test_get_aggregated_data_daily(self, analytics, sample_data):
        """Test daily data aggregation."""
        with patch.object(analytics, '_get_raw_data', return_value=sample_data):
            result = analytics.get_aggregated_data(
                data_type='noise',
                period=AggregationPeriod.DAILY
            )
            
            assert isinstance(result, list)
            assert len(result) > 0
    
    def test_get_aggregated_data_weekly(self, analytics, sample_data):
        """Test weekly data aggregation."""
        with patch.object(analytics, '_get_raw_data', return_value=sample_data):
            result = analytics.get_aggregated_data(
                data_type='greenery',
                period=AggregationPeriod.WEEKLY
            )
            
            assert isinstance(result, list)
    
    def test_get_aggregated_data_empty(self, analytics):
        """Test aggregation with no data."""
        with patch.object(analytics, '_get_raw_data', return_value=[]):
            result = analytics.get_aggregated_data(
                data_type='greenery',
                period=AggregationPeriod.HOURLY
            )
            
            assert result == []
    
    def test_calculate_statistics(self, analytics, sample_data):
        """Test comprehensive statistics calculation."""
        with patch.object(analytics, '_get_raw_data', return_value=sample_data):
            stats = analytics.calculate_statistics('greenery')
            
            assert 'count' in stats
            assert 'avg' in stats
            assert 'min' in stats
            assert 'max' in stats
            assert 'stddev' in stats
            assert 'median' in stats
            assert 'range' in stats
            
            assert stats['count'] == len(sample_data)
            assert stats['avg'] > 0
            assert stats['min'] <= stats['avg'] <= stats['max']
            assert stats['range'] == stats['max'] - stats['min']
    
    def test_calculate_statistics_empty(self, analytics):
        """Test statistics with no data."""
        with patch.object(analytics, '_get_raw_data', return_value=[]):
            stats = analytics.calculate_statistics('noise')
            
            assert stats['count'] == 0
            assert stats['avg'] == 0.0
            assert stats['min'] == 0.0
            assert stats['max'] == 0.0
            assert stats['stddev'] == 0.0
    
    def test_calculate_statistics_single_value(self, analytics):
        """Test statistics with single data point."""
        now = datetime.now()
        data = [{'timestamp': now, 'value': 42.0}]
        
        with patch.object(analytics, '_get_raw_data', return_value=data):
            stats = analytics.calculate_statistics('greenery')
            
            assert stats['count'] == 1
            assert stats['avg'] == 42.0
            assert stats['min'] == 42.0
            assert stats['max'] == 42.0
            assert stats['stddev'] == 0.0  # Single value has no deviation
            assert stats['range'] == 0.0
    
    def test_detect_trends_increasing(self, analytics):
        """Test trend detection for increasing data."""
        now = datetime.now()
        # Create clearly increasing trend (oldest to newest)
        data = [
            {'timestamp': now - timedelta(days=10-i), 'value': 10.0 + i * 5.0}
            for i in range(10)
        ]
        
        with patch.object(analytics, '_get_raw_data', return_value=data):
            trends = analytics.detect_trends('greenery', days=10)
            
            assert trends['direction'] == TrendDirection.INCREASING.value
            assert trends['slope'] > 0
            assert trends['change_percent'] > 10  # Significant increase
            assert 0 <= trends['confidence'] <= 1.0
    
    def test_detect_trends_decreasing(self, analytics):
        """Test trend detection for decreasing data."""
        now = datetime.now()
        # Create clearly decreasing trend (oldest to newest)
        data = [
            {'timestamp': now - timedelta(days=10-i), 'value': 50.0 - i * 3.0}
            for i in range(10)
        ]
        
        with patch.object(analytics, '_get_raw_data', return_value=data):
            trends = analytics.detect_trends('noise', days=10)
            
            assert trends['direction'] == TrendDirection.DECREASING.value
            assert trends['slope'] < 0
            assert trends['change_percent'] < -10  # Significant decrease
    
    def test_detect_trends_stable(self, analytics):
        """Test trend detection for stable data."""
        now = datetime.now()
        # Create stable data with small variations
        data = [
            {'timestamp': now - timedelta(days=i), 'value': 25.0 + (i % 3) * 0.5}
            for i in range(10)
        ]
        
        with patch.object(analytics, '_get_raw_data', return_value=data):
            trends = analytics.detect_trends('greenery', days=10)
            
            assert trends['direction'] == TrendDirection.STABLE.value
            assert abs(trends['change_percent']) < 10  # Less than threshold
    
    def test_detect_trends_insufficient_data(self, analytics):
        """Test trend detection with insufficient data."""
        data = [{'timestamp': datetime.now(), 'value': 20.0}]
        
        with patch.object(analytics, '_get_raw_data', return_value=data):
            trends = analytics.detect_trends('greenery')
            
            assert trends['direction'] == TrendDirection.STABLE.value
            assert trends['slope'] == 0.0
            assert trends['confidence'] == 0.0
            assert 'Insufficient data' in trends['message']
    
    def test_detect_anomalies(self, analytics):
        """Test anomaly detection."""
        now = datetime.now()
        # Create data with outliers
        normal_values = [25.0 + i * 0.5 for i in range(20)]
        outliers = [100.0, 5.0]  # Clear outliers
        
        data = []
        for i, val in enumerate(normal_values + outliers):
            data.append({
                'timestamp': now - timedelta(hours=i),
                'value': val
            })
        
        with patch.object(analytics, '_get_raw_data', return_value=data):
            anomalies = analytics.detect_anomalies('greenery', days=1)
            
            assert len(anomalies) > 0
            
            # Check anomaly structure
            for anomaly in anomalies:
                assert 'timestamp' in anomaly
                assert 'value' in anomaly
                assert 'z_score' in anomaly
                assert 'deviation' in anomaly
                assert 'severity' in anomaly
                assert anomaly['z_score'] > analytics.ANOMALY_STDDEV_THRESHOLD
    
    def test_detect_anomalies_no_variation(self, analytics):
        """Test anomaly detection with no variation."""
        now = datetime.now()
        # All values the same
        data = [
            {'timestamp': now - timedelta(hours=i), 'value': 25.0}
            for i in range(10)
        ]
        
        with patch.object(analytics, '_get_raw_data', return_value=data):
            anomalies = analytics.detect_anomalies('noise')
            
            assert anomalies == []  # No anomalies when no variation
    
    def test_detect_anomalies_insufficient_data(self, analytics):
        """Test anomaly detection with insufficient data."""
        data = [{'timestamp': datetime.now(), 'value': 20.0}]
        
        with patch.object(analytics, '_get_raw_data', return_value=data):
            anomalies = analytics.detect_anomalies('greenery')
            
            assert anomalies == []
    
    def test_get_correlation_positive(self, analytics):
        """Test correlation detection for positive relationship."""
        now = datetime.now()
        # Create positively correlated data
        greenery_data = [
            {'timestamp': now - timedelta(hours=i), 'value': 20.0 + i * 2.0}
            for i in range(20)
        ]
        noise_data = [
            {'timestamp': now - timedelta(hours=i), 'value': 30.0 + i * 1.5}
            for i in range(20)
        ]
        
        with patch.object(analytics, '_get_raw_data') as mock_data:
            def side_effect(data_type, start_time, end_time):
                return greenery_data if data_type == 'greenery' else noise_data
            
            mock_data.side_effect = side_effect
            
            correlation = analytics.get_correlation(days=1)
            
            assert 'coefficient' in correlation
            assert 'strength' in correlation
            assert 'direction' in correlation
            assert correlation['coefficient'] > 0.5  # Positive correlation
            assert correlation['direction'] == 'positive'
    
    def test_get_correlation_negative(self, analytics):
        """Test correlation detection for negative relationship."""
        now = datetime.now()
        # Create negatively correlated data
        greenery_data = [
            {'timestamp': now - timedelta(hours=i), 'value': 50.0 - i * 2.0}
            for i in range(20)
        ]
        noise_data = [
            {'timestamp': now - timedelta(hours=i), 'value': 20.0 + i * 2.0}
            for i in range(20)
        ]
        
        with patch.object(analytics, '_get_raw_data') as mock_data:
            def side_effect(data_type, start_time, end_time):
                return greenery_data if data_type == 'greenery' else noise_data
            
            mock_data.side_effect = side_effect
            
            correlation = analytics.get_correlation(days=1)
            
            assert correlation['coefficient'] < -0.5  # Negative correlation
            assert correlation['direction'] == 'negative'
    
    def test_get_correlation_insufficient_data(self, analytics):
        """Test correlation with insufficient data."""
        data = [{'timestamp': datetime.now(), 'value': 20.0}]
        
        with patch.object(analytics, '_get_raw_data', return_value=data):
            correlation = analytics.get_correlation()
            
            assert correlation['coefficient'] == 0.0
            assert correlation['strength'] == 'insufficient_data'
    
    def test_get_chart_data(self, analytics, sample_data):
        """Test chart data formatting."""
        with patch.object(analytics, '_get_raw_data', return_value=sample_data):
            chart_data = analytics.get_chart_data(
                data_type='greenery',
                period=AggregationPeriod.HOURLY,
                days=1
            )
            
            assert 'labels' in chart_data
            assert 'datasets' in chart_data
            assert 'stats' in chart_data
            assert 'metadata' in chart_data
            
            # Check datasets structure
            assert len(chart_data['datasets']) == 3  # Average, Min, Max
            assert all('label' in ds for ds in chart_data['datasets'])
            assert all('data' in ds for ds in chart_data['datasets'])
            
            # Check metadata
            assert chart_data['metadata']['data_type'] == 'greenery'
            assert chart_data['metadata']['period'] == 'hourly'
    
    def test_get_chart_data_empty(self, analytics):
        """Test chart data with no data."""
        with patch.object(analytics, '_get_raw_data', return_value=[]):
            chart_data = analytics.get_chart_data('noise')
            
            assert chart_data['labels'] == []
            assert chart_data['datasets'] == []
            assert chart_data['stats'] == {}
    
    def test_group_by_period_hourly(self, analytics):
        """Test grouping data by hourly period."""
        now = datetime.now()
        data = [
            {'timestamp': now, 'value': 10.0},
            {'timestamp': now + timedelta(minutes=30), 'value': 15.0},
            {'timestamp': now + timedelta(hours=1, minutes=15), 'value': 20.0}
        ]
        
        grouped = analytics._group_by_period(data, AggregationPeriod.HOURLY)
        
        assert len(grouped) == 2  # Two different hours
    
    def test_group_by_period_daily(self, analytics):
        """Test grouping data by daily period."""
        now = datetime.now()
        data = [
            {'timestamp': now, 'value': 10.0},
            {'timestamp': now + timedelta(hours=12), 'value': 15.0},
            {'timestamp': now + timedelta(days=1), 'value': 20.0}
        ]
        
        grouped = analytics._group_by_period(data, AggregationPeriod.DAILY)
        
        assert len(grouped) == 2  # Two different days
    
    def test_calculate_slope(self, analytics):
        """Test slope calculation for linear regression."""
        # Perfect linear increase
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        slope = analytics._calculate_slope(values)
        
        assert slope == pytest.approx(1.0, rel=0.01)
    
    def test_calculate_slope_flat(self, analytics):
        """Test slope calculation for flat data."""
        values = [5.0, 5.0, 5.0, 5.0, 5.0]
        slope = analytics._calculate_slope(values)
        
        assert slope == pytest.approx(0.0, abs=0.01)
    
    def test_calculate_confidence(self, analytics):
        """Test R² confidence calculation."""
        # Perfect linear relationship
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        slope = 1.0
        confidence = analytics._calculate_confidence(values, slope)
        
        assert confidence > 0.95  # High confidence for perfect fit
    
    def test_calculate_confidence_poor_fit(self, analytics):
        """Test confidence for poor fit."""
        # Random-ish data
        values = [1.0, 5.0, 2.0, 4.0, 3.0]
        slope = analytics._calculate_slope(values)
        confidence = analytics._calculate_confidence(values, slope)
        
        assert 0.0 <= confidence <= 1.0
    
    def test_pearson_correlation_perfect(self, analytics):
        """Test Pearson correlation for perfect correlation."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        
        correlation = analytics._pearson_correlation(x, y)
        
        assert correlation == pytest.approx(1.0, abs=0.01)
    
    def test_pearson_correlation_negative(self, analytics):
        """Test Pearson correlation for negative correlation."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [10.0, 8.0, 6.0, 4.0, 2.0]
        
        correlation = analytics._pearson_correlation(x, y)
        
        assert correlation == pytest.approx(-1.0, abs=0.01)
    
    def test_pearson_correlation_no_correlation(self, analytics):
        """Test Pearson correlation for uncorrelated data."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [5.0, 5.0, 5.0, 5.0, 5.0]
        
        correlation = analytics._pearson_correlation(x, y)
        
        assert correlation == pytest.approx(0.0, abs=0.01)
    
    def test_align_data_points(self, analytics):
        """Test data point alignment by timestamp."""
        now = datetime.now()
        data1 = [
            {'timestamp': now, 'value': 10.0},
            {'timestamp': now + timedelta(minutes=5), 'value': 15.0}
        ]
        data2 = [
            {'timestamp': now + timedelta(seconds=30), 'value': 20.0},
            {'timestamp': now + timedelta(minutes=5, seconds=20), 'value': 25.0}
        ]
        
        aligned = analytics._align_data_points(data1, data2)
        
        assert len(aligned) == 2
        assert all(isinstance(pair, tuple) for pair in aligned)
        assert all(len(pair) == 2 for pair in aligned)
    
    def test_align_data_points_no_matches(self, analytics):
        """Test alignment with no matching timestamps."""
        now = datetime.now()
        data1 = [{'timestamp': now, 'value': 10.0}]
        data2 = [{'timestamp': now + timedelta(hours=2), 'value': 20.0}]
        
        aligned = analytics._align_data_points(data1, data2, tolerance_minutes=1)
        
        assert aligned == []
    
    def test_format_trend_message_increasing(self, analytics):
        """Test trend message formatting for increasing trend."""
        message = analytics._format_trend_message(
            TrendDirection.INCREASING,
            25.0,
            0.85
        )
        
        assert 'increasing' in message.lower()
        assert '25.0%' in message
        assert 'high confidence' in message.lower()
    
    def test_format_trend_message_stable(self, analytics):
        """Test trend message formatting for stable trend."""
        message = analytics._format_trend_message(
            TrendDirection.STABLE,
            3.0,
            0.5
        )
        
        assert 'stable' in message.lower()
        assert '3.0%' in message
    
    def test_format_correlation_message(self, analytics):
        """Test correlation message formatting."""
        message = analytics._format_correlation_message(0.75, 'strong')
        
        assert 'strong' in message.lower()
        assert 'positive' in message.lower()
        assert '0.750' in message
