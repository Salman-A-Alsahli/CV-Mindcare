"""
Data Visualization & Analytics Module

Provides historical data aggregation, statistics calculation, trend analysis,
and chart-ready data formatting for the CV-Mindcare wellness monitoring system.

Phase 7 of the v0.2.0 development roadmap.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import statistics
import math
import sqlite3
from contextlib import closing

from backend.database import DB_PATH

logger = logging.getLogger(__name__)


class AggregationPeriod(Enum):
    """Time periods for data aggregation."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrendDirection(Enum):
    """Direction of data trends."""

    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"


class Analytics:
    """
    Analytics engine for historical data analysis and visualization.

    Provides aggregation, statistics, trend detection, and chart-ready
    data formatting for all sensor data.
    """

    # Constants
    TREND_THRESHOLD = 0.1  # 10% change to be considered a trend
    ANOMALY_STDDEV_THRESHOLD = 2.0  # Standard deviations for anomaly detection
    MIN_DATA_POINTS = 3  # Minimum data points for statistics

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize analytics engine.

        Args:
            db_path: Path to database file. If None, uses default.
        """
        self.db_path = db_path if db_path is not None else DB_PATH
        logger.info("Analytics engine initialized")

    def get_aggregated_data(
        self,
        data_type: str,
        period: AggregationPeriod,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Aggregate sensor data by time period.

        Args:
            data_type: Type of data ('greenery' or 'noise')
            period: Aggregation period (hourly, daily, weekly, monthly)
            start_time: Start of time range (default: 7 days ago)
            end_time: End of time range (default: now)
            limit: Maximum number of aggregated points

        Returns:
            List of aggregated data points with timestamp and statistics
        """
        if end_time is None:
            end_time = datetime.now()

        if start_time is None:
            # Default to last 7 days
            start_time = end_time - timedelta(days=7)

        # Get raw data from database
        raw_data = self._get_raw_data(data_type, start_time, end_time)

        if not raw_data:
            logger.warning(f"No {data_type} data found for specified time range")
            return []

        # Group data by period
        grouped_data = self._group_by_period(raw_data, period)

        # Calculate statistics for each group
        aggregated = []
        for timestamp, values in sorted(grouped_data.items())[:limit]:
            if values:
                aggregated.append(
                    {
                        "timestamp": timestamp.isoformat(),
                        "avg": round(statistics.mean(values), 2),
                        "min": round(min(values), 2),
                        "max": round(max(values), 2),
                        "count": len(values),
                        "stddev": round(statistics.stdev(values), 2) if len(values) > 1 else 0.0,
                    }
                )

        logger.info(f"Aggregated {len(aggregated)} {period.value} data points for {data_type}")
        return aggregated

    def calculate_statistics(
        self,
        data_type: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics for sensor data.

        Args:
            data_type: Type of data ('greenery' or 'noise')
            start_time: Start of time range (default: 7 days ago)
            end_time: End of time range (default: now)

        Returns:
            Dictionary with statistical metrics
        """
        if end_time is None:
            end_time = datetime.now()

        if start_time is None:
            start_time = end_time - timedelta(days=7)

        raw_data = self._get_raw_data(data_type, start_time, end_time)

        if not raw_data:
            return {
                "count": 0,
                "avg": 0.0,
                "min": 0.0,
                "max": 0.0,
                "stddev": 0.0,
                "median": 0.0,
                "mode": None,
                "range": 0.0,
            }

        values = [item["value"] for item in raw_data]

        stats = {
            "count": len(values),
            "avg": round(statistics.mean(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "stddev": round(statistics.stdev(values), 2) if len(values) > 1 else 0.0,
            "median": round(statistics.median(values), 2),
            "range": round(max(values) - min(values), 2),
        }

        # Calculate mode (most common value, rounded to 1 decimal)
        try:
            rounded_values = [round(v, 1) for v in values]
            stats["mode"] = round(statistics.mode(rounded_values), 2)
        except statistics.StatisticsError:
            stats["mode"] = None  # No unique mode

        logger.info(f"Calculated statistics for {data_type}: {stats['count']} data points")
        return stats

    def detect_trends(
        self, data_type: str, period: AggregationPeriod = AggregationPeriod.DAILY, days: int = 7
    ) -> Dict[str, Any]:
        """
        Detect trends in sensor data over time.

        Args:
            data_type: Type of data ('greenery' or 'noise')
            period: Aggregation period for trend analysis
            days: Number of days to analyze

        Returns:
            Trend analysis with direction, slope, and confidence
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        aggregated = self.get_aggregated_data(data_type, period, start_time, end_time)

        if len(aggregated) < self.MIN_DATA_POINTS:
            return {
                "direction": TrendDirection.STABLE.value,
                "slope": 0.0,
                "confidence": 0.0,
                "start_avg": 0.0,
                "end_avg": 0.0,
                "change_percent": 0.0,
                "message": f"Insufficient data points ({len(aggregated)} < {self.MIN_DATA_POINTS})",
            }

        # Calculate linear regression
        values = [item["avg"] for item in aggregated]
        slope = self._calculate_slope(values)

        # Determine trend direction
        start_avg = statistics.mean(values[: len(values) // 3]) if len(values) >= 3 else values[0]
        end_avg = statistics.mean(values[-len(values) // 3 :]) if len(values) >= 3 else values[-1]
        change_percent = ((end_avg - start_avg) / start_avg * 100) if start_avg != 0 else 0.0

        if abs(change_percent) < self.TREND_THRESHOLD * 100:
            direction = TrendDirection.STABLE
        elif change_percent > 0:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING

        # Calculate confidence (based on R²)
        confidence = self._calculate_confidence(values, slope)

        result = {
            "direction": direction.value,
            "slope": round(slope, 4),
            "confidence": round(confidence, 2),
            "start_avg": round(start_avg, 2),
            "end_avg": round(end_avg, 2),
            "change_percent": round(change_percent, 2),
            "message": self._format_trend_message(direction, change_percent, confidence),
        }

        logger.info(
            f"Detected {direction.value} trend for {data_type}: {change_percent:.1f}% change"
        )
        return result

    def detect_anomalies(
        self, data_type: str, days: int = 7, threshold_stddev: float = ANOMALY_STDDEV_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous data points that deviate significantly from normal.

        Args:
            data_type: Type of data ('greenery' or 'noise')
            days: Number of days to analyze
            threshold_stddev: Number of standard deviations for anomaly threshold

        Returns:
            List of anomalous data points with details
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        raw_data = self._get_raw_data(data_type, start_time, end_time)

        if len(raw_data) < self.MIN_DATA_POINTS:
            return []

        values = [item["value"] for item in raw_data]
        mean_val = statistics.mean(values)
        stddev = statistics.stdev(values) if len(values) > 1 else 0.0

        if stddev == 0:
            return []  # No variation, no anomalies

        # Find anomalies
        anomalies = []
        for item in raw_data:
            z_score = abs((item["value"] - mean_val) / stddev)
            if z_score > threshold_stddev:
                anomalies.append(
                    {
                        "timestamp": item["timestamp"].isoformat(),
                        "value": round(item["value"], 2),
                        "z_score": round(z_score, 2),
                        "deviation": round(item["value"] - mean_val, 2),
                        "severity": "high" if z_score > threshold_stddev * 1.5 else "medium",
                    }
                )

        logger.info(f"Detected {len(anomalies)} anomalies for {data_type}")
        return anomalies

    def get_correlation(self, days: int = 7) -> Dict[str, Any]:
        """
        Calculate correlation between greenery and noise levels.

        Args:
            days: Number of days to analyze

        Returns:
            Correlation coefficient and interpretation
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        greenery_data = self._get_raw_data("greenery", start_time, end_time)
        noise_data = self._get_raw_data("noise", start_time, end_time)

        if len(greenery_data) < self.MIN_DATA_POINTS or len(noise_data) < self.MIN_DATA_POINTS:
            return {
                "coefficient": 0.0,
                "strength": "insufficient_data",
                "message": "Not enough data points for correlation analysis",
            }

        # Align data points by timestamp (within 1 minute)
        aligned_pairs = self._align_data_points(greenery_data, noise_data)

        if len(aligned_pairs) < self.MIN_DATA_POINTS:
            return {
                "coefficient": 0.0,
                "strength": "insufficient_aligned_data",
                "message": "Not enough aligned data points for correlation",
            }

        greenery_values = [pair[0] for pair in aligned_pairs]
        noise_values = [pair[1] for pair in aligned_pairs]

        coefficient = self._pearson_correlation(greenery_values, noise_values)

        # Interpret strength
        abs_coef = abs(coefficient)
        if abs_coef < 0.3:
            strength = "weak"
        elif abs_coef < 0.7:
            strength = "moderate"
        else:
            strength = "strong"

        result = {
            "coefficient": round(coefficient, 3),
            "strength": strength,
            "direction": "positive" if coefficient > 0 else "negative",
            "aligned_points": len(aligned_pairs),
            "message": self._format_correlation_message(coefficient, strength),
        }

        logger.info(f"Correlation analysis: {strength} {result['direction']} ({coefficient:.3f})")
        return result

    def get_chart_data(
        self, data_type: str, period: AggregationPeriod = AggregationPeriod.HOURLY, days: int = 1
    ) -> Dict[str, Any]:
        """
        Get data formatted for chart visualization libraries.

        Args:
            data_type: Type of data ('greenery' or 'noise')
            period: Aggregation period
            days: Number of days to include

        Returns:
            Chart-ready data with labels, datasets, and metadata
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        aggregated = self.get_aggregated_data(data_type, period, start_time, end_time)

        if not aggregated:
            return {"labels": [], "datasets": [], "stats": {}}

        # Format labels (timestamps)
        if period == AggregationPeriod.HOURLY:
            label_format = "%H:%M"
        elif period == AggregationPeriod.DAILY:
            label_format = "%m/%d"
        elif period == AggregationPeriod.WEEKLY:
            label_format = "Week %W"
        else:
            label_format = "%Y-%m"

        labels = [
            datetime.fromisoformat(item["timestamp"]).strftime(label_format) for item in aggregated
        ]

        # Prepare datasets
        avg_values = [item["avg"] for item in aggregated]
        min_values = [item["min"] for item in aggregated]
        max_values = [item["max"] for item in aggregated]

        # Choose colors based on data type
        if data_type == "greenery":
            color = "rgba(75, 192, 192, 0.8)"  # Green
            bg_color = "rgba(75, 192, 192, 0.2)"
        else:  # noise
            color = "rgba(255, 99, 132, 0.8)"  # Red
            bg_color = "rgba(255, 99, 132, 0.2)"

        datasets = [
            {
                "label": f"{data_type.capitalize()} Average",
                "data": avg_values,
                "borderColor": color,
                "backgroundColor": bg_color,
                "fill": True,
            },
            {
                "label": "Min",
                "data": min_values,
                "borderColor": "rgba(201, 203, 207, 0.5)",
                "backgroundColor": "transparent",
                "borderDash": [5, 5],
                "fill": False,
            },
            {
                "label": "Max",
                "data": max_values,
                "borderColor": "rgba(201, 203, 207, 0.5)",
                "backgroundColor": "transparent",
                "borderDash": [5, 5],
                "fill": False,
            },
        ]

        # Calculate overall statistics
        stats = {
            "avg": round(statistics.mean(avg_values), 2),
            "min": round(min(min_values), 2),
            "max": round(max(max_values), 2),
            "stddev": round(statistics.stdev(avg_values), 2) if len(avg_values) > 1 else 0.0,
            "data_points": sum(item["count"] for item in aggregated),
        }

        return {
            "labels": labels,
            "datasets": datasets,
            "stats": stats,
            "metadata": {
                "data_type": data_type,
                "period": period.value,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
        }

    # Private helper methods

    def _get_raw_data(
        self, data_type: str, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Get raw sensor data from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            with closing(conn):
                # Query sensor_data table
                query = """
                    SELECT value, timestamp 
                    FROM sensor_data 
                    WHERE sensor_type = ? 
                    AND datetime(timestamp) >= datetime(?)
                    AND datetime(timestamp) <= datetime(?)
                    ORDER BY timestamp
                    LIMIT 10000
                """

                cursor = conn.execute(
                    query, (data_type, start_time.isoformat(), end_time.isoformat())
                )

                rows = cursor.fetchall()

                filtered = []
                for row in rows:
                    filtered.append(
                        {
                            "timestamp": datetime.fromisoformat(row["timestamp"]),
                            "value": float(row["value"]),
                        }
                    )

                return filtered

        except Exception as e:
            logger.error(f"Error getting raw data for {data_type}: {e}")
            return []

    def _group_by_period(
        self, data: List[Dict[str, Any]], period: AggregationPeriod
    ) -> Dict[datetime, List[float]]:
        """Group data points by aggregation period."""
        grouped = {}

        for item in data:
            timestamp = item["timestamp"]

            # Round timestamp to period boundary
            if period == AggregationPeriod.HOURLY:
                key = timestamp.replace(minute=0, second=0, microsecond=0)
            elif period == AggregationPeriod.DAILY:
                key = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == AggregationPeriod.WEEKLY:
                # Round to Monday of the week
                key = timestamp - timedelta(days=timestamp.weekday())
                key = key.replace(hour=0, minute=0, second=0, microsecond=0)
            else:  # MONTHLY
                key = timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item["value"])

        return grouped

    def _calculate_slope(self, values: List[float]) -> float:
        """Calculate slope of linear regression."""
        n = len(values)
        x = list(range(n))

        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        return numerator / denominator if denominator != 0 else 0.0

    def _calculate_confidence(self, values: List[float], slope: float) -> float:
        """Calculate R² confidence score for trend."""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = list(range(n))
        y_mean = statistics.mean(values)

        # Calculate predicted values
        x_mean = statistics.mean(x)
        intercept = y_mean - slope * x_mean
        predicted = [slope * x[i] + intercept for i in range(n)]

        # Calculate R²
        ss_res = sum((values[i] - predicted[i]) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))

        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

        return max(0.0, min(1.0, r_squared))  # Clamp to [0, 1]

    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(x)
        if n == 0:
            return 0.0

        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        x_var = sum((x[i] - x_mean) ** 2 for i in range(n))
        y_var = sum((y[i] - y_mean) ** 2 for i in range(n))

        denominator = math.sqrt(x_var * y_var)

        return numerator / denominator if denominator != 0 else 0.0

    def _align_data_points(
        self, data1: List[Dict[str, Any]], data2: List[Dict[str, Any]], tolerance_minutes: int = 1
    ) -> List[Tuple[float, float]]:
        """Align two datasets by timestamp."""
        aligned = []
        tolerance = timedelta(minutes=tolerance_minutes)

        for item1 in data1:
            # Find closest matching timestamp in data2
            closest = None
            min_diff = None

            for item2 in data2:
                diff = abs(item1["timestamp"] - item2["timestamp"])
                if diff <= tolerance:
                    if min_diff is None or diff < min_diff:
                        min_diff = diff
                        closest = item2

            if closest is not None:
                aligned.append((item1["value"], closest["value"]))

        return aligned

    def _format_trend_message(
        self, direction: TrendDirection, change_percent: float, confidence: float
    ) -> str:
        """Format human-readable trend message."""
        if direction == TrendDirection.STABLE:
            return f"Data remains stable with minimal change ({abs(change_percent):.1f}%)"

        direction_word = "increasing" if direction == TrendDirection.INCREASING else "decreasing"
        confidence_word = "high" if confidence > 0.7 else "moderate" if confidence > 0.4 else "low"

        return f"Data is {direction_word} by {abs(change_percent):.1f}% with {confidence_word} confidence ({confidence:.0%})"

    def _format_correlation_message(self, coefficient: float, strength: str) -> str:
        """Format human-readable correlation message."""
        direction = "positive" if coefficient > 0 else "negative"
        return f"There is a {strength} {direction} correlation ({coefficient:.3f}) between greenery and noise levels"
