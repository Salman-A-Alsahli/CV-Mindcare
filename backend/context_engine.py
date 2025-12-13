"""
Enhanced Context Engine for CV-Mindcare

Provides intelligent analysis including:
- Pattern detection (recurring issues, time-based patterns)
- Personalized baseline learning
- Correlation analysis
- Actionable recommendations
- Wellness score calculation

Privacy-first: All processing happens locally.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics

from backend.database import Database

logger = logging.getLogger(__name__)


class ContextEngine:
    """Enhanced context engine with AI-powered insights and recommendations."""

    # Wellness score weights
    GREENERY_WEIGHT = 0.4
    NOISE_WEIGHT = 0.4
    TREND_WEIGHT = 0.2

    # Thresholds
    EXCELLENT_THRESHOLD = 90
    GOOD_THRESHOLD = 70
    FAIR_THRESHOLD = 50

    # Pattern detection thresholds
    MIN_SAMPLES_FOR_PATTERN = 10
    RECURRING_ISSUE_THRESHOLD = 0.3  # 30% of time
    TIME_PATTERN_THRESHOLD = 0.6  # 60% occurrence in time slot

    # Baseline learning
    MIN_SAMPLES_FOR_BASELINE = 20
    BASELINE_CONFIDENCE_THRESHOLD = 0.7

    def __init__(self, db_path: str = "data/cv_mindcare.db"):
        """
        Initialize context engine.

        Args:
            db_path: Path to SQLite database
        """
        self.db = Database(db_path)
        self.baselines = {}
        self.feedback_history = []
        logger.info("ContextEngine initialized")

    def calculate_wellness_score(self, days: int = 1) -> Dict:
        """
        Calculate overall wellness score (0-100).

        Args:
            days: Number of days to analyze

        Returns:
            Dict with score, rating, components, and message
        """
        try:
            # Get recent data
            since = datetime.now() - timedelta(days=days)
            greenery_data = self.db.get_greenery_data(since=since)
            noise_data = self.db.get_noise_data(since=since)

            if not greenery_data and not noise_data:
                return {
                    "score": 50,
                    "rating": "Unknown",
                    "components": {},
                    "message": "Insufficient data to calculate wellness score",
                    "compared_to_baseline": 0,
                }

            # Calculate component scores
            greenery_score = self._calculate_greenery_score(greenery_data)
            noise_score = self._calculate_noise_score(noise_data)
            trend_score = self._calculate_trend_score(greenery_data, noise_data)

            # Weighted overall score
            overall_score = (
                greenery_score * self.GREENERY_WEIGHT
                + noise_score * self.NOISE_WEIGHT
                + trend_score * self.TREND_WEIGHT
            )

            # Get rating
            rating = self._get_wellness_rating(overall_score)

            # Compare to baseline
            baseline_diff = self._compare_to_baseline(overall_score)

            # Generate message
            message = self._generate_wellness_message(overall_score, greenery_score, noise_score)

            return {
                "score": round(overall_score, 1),
                "rating": rating,
                "components": {
                    "greenery_score": round(greenery_score, 1),
                    "noise_score": round(noise_score, 1),
                    "trend_score": round(trend_score, 1),
                },
                "message": message,
                "compared_to_baseline": round(baseline_diff, 1),
            }

        except Exception as e:
            logger.error(f"Error calculating wellness score: {e}")
            return {
                "score": 50,
                "rating": "Error",
                "components": {},
                "message": f"Error calculating score: {str(e)}",
                "compared_to_baseline": 0,
            }

    def generate_recommendations(
        self, days: int = 7, limit: int = 10, priority_filter: Optional[str] = None
    ) -> Dict:
        """
        Generate personalized recommendations.

        Args:
            days: Days of data to analyze
            limit: Maximum recommendations to return
            priority_filter: Filter by priority (high/medium/low)

        Returns:
            Dict with recommendations and summary
        """
        try:
            recommendations = []

            # Get recent data
            since = datetime.now() - timedelta(days=days)
            greenery_data = self.db.get_greenery_data(since=since)
            noise_data = self.db.get_noise_data(since=since)

            # Generate recommendations
            recommendations.extend(self._recommend_greenery(greenery_data))
            recommendations.extend(self._recommend_noise(noise_data))
            recommendations.extend(self._recommend_habits(greenery_data, noise_data))
            recommendations.extend(self._recommend_wellness(greenery_data, noise_data))

            # Filter by priority if specified
            if priority_filter:
                recommendations = [r for r in recommendations if r["priority"] == priority_filter]

            # Sort by priority and confidence
            priority_order = {"high": 0, "medium": 1, "low": 2}
            recommendations.sort(
                key=lambda x: (priority_order[x["priority"]], -x.get("confidence", 0))
            )

            # Limit results
            recommendations = recommendations[:limit]

            # Generate summary
            summary = {
                "total": len(recommendations),
                "by_priority": {
                    "high": sum(1 for r in recommendations if r["priority"] == "high"),
                    "medium": sum(1 for r in recommendations if r["priority"] == "medium"),
                    "low": sum(1 for r in recommendations if r["priority"] == "low"),
                },
            }

            return {"recommendations": recommendations, "summary": summary}

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {"recommendations": [], "summary": {"total": 0, "by_priority": {}}}

    def detect_patterns(self, days: int = 14, pattern_type: str = "all") -> Dict:
        """
        Detect patterns in sensor data.

        Args:
            days: Days of data to analyze
            pattern_type: Type of patterns (all/recurring/time_based/trends)

        Returns:
            Dict with detected patterns
        """
        try:
            patterns = []

            # Get data
            since = datetime.now() - timedelta(days=days)
            greenery_data = self.db.get_greenery_data(since=since)
            noise_data = self.db.get_noise_data(since=since)

            if pattern_type in ["all", "recurring"]:
                patterns.extend(self._detect_recurring_issues(greenery_data, noise_data))

            if pattern_type in ["all", "time_based"]:
                patterns.extend(self._detect_time_patterns(greenery_data, noise_data))

            if pattern_type in ["all", "trends"]:
                patterns.extend(self._detect_trend_patterns(greenery_data, noise_data))

            return {"patterns": patterns}

        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {"patterns": []}

    def get_baselines(self) -> Dict:
        """
        Get personalized baselines for the user.

        Returns:
            Dict with baseline values and confidence
        """
        try:
            # Update baselines
            self._update_baselines()

            return {
                "baselines": self.baselines,
                "last_updated": datetime.now().isoformat(),
                "recommendations": self._baseline_recommendations(),
            }

        except Exception as e:
            logger.error(f"Error getting baselines: {e}")
            return {
                "baselines": {},
                "last_updated": datetime.now().isoformat(),
                "recommendations": "Error retrieving baselines",
            }

    def submit_feedback(
        self,
        recommendation_id: str,
        helpful: bool,
        implemented: bool = False,
        comment: Optional[str] = None,
    ) -> Dict:
        """
        Submit feedback on a recommendation.

        Args:
            recommendation_id: ID of the recommendation
            helpful: Whether the recommendation was helpful
            implemented: Whether the recommendation was implemented
            comment: Optional comment

        Returns:
            Dict with confirmation
        """
        try:
            feedback = {
                "recommendation_id": recommendation_id,
                "helpful": helpful,
                "implemented": implemented,
                "comment": comment,
                "timestamp": datetime.now().isoformat(),
            }

            self.feedback_history.append(feedback)
            logger.info(f"Feedback submitted for recommendation {recommendation_id}")

            return {"status": "success", "message": "Feedback recorded successfully"}

        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            return {"status": "error", "message": str(e)}

    # Private helper methods

    def _calculate_greenery_score(self, data: List[Tuple]) -> float:
        """Calculate greenery component score (0-100)."""
        if not data:
            return 50.0

        percentages = [row[1] for row in data]
        avg = statistics.mean(percentages)

        # Score based on percentage (optimal: 20-50%)
        if avg >= 20:
            score = 100
        elif avg >= 10:
            score = 70 + (avg - 10) * 3  # 70-100
        elif avg >= 5:
            score = 50 + (avg - 5) * 4  # 50-70
        else:
            score = max(0, avg * 10)  # 0-50

        return min(100, score)

    def _calculate_noise_score(self, data: List[Tuple]) -> float:
        """Calculate noise component score (0-100)."""
        if not data:
            return 50.0

        db_levels = [row[1] for row in data]
        avg = statistics.mean(db_levels)

        # Score based on dB levels (optimal: 30-50 dB)
        if avg <= 50:
            score = 100
        elif avg <= 70:
            score = 100 - (avg - 50) * 2  # 100-60
        elif avg <= 85:
            score = 60 - (avg - 70) * 2  # 60-30
        else:
            score = max(0, 30 - (avg - 85))

        return min(100, score)

    def _calculate_trend_score(self, greenery_data: List[Tuple], noise_data: List[Tuple]) -> float:
        """Calculate trend component score (0-100)."""
        score = 50.0  # Default neutral

        # Check if improving or degrading
        if len(greenery_data) >= 2:
            recent = statistics.mean([row[1] for row in greenery_data[-5:]])
            older = statistics.mean([row[1] for row in greenery_data[:5]])
            if recent > older:
                score += 25

        if len(noise_data) >= 2:
            recent = statistics.mean([row[1] for row in noise_data[-5:]])
            older = statistics.mean([row[1] for row in noise_data[:5]])
            if recent < older:  # Lower noise is better
                score += 25

        return min(100, score)

    def _get_wellness_rating(self, score: float) -> str:
        """Get rating label for wellness score."""
        if score >= self.EXCELLENT_THRESHOLD:
            return "Excellent"
        elif score >= self.GOOD_THRESHOLD:
            return "Good"
        elif score >= self.FAIR_THRESHOLD:
            return "Fair"
        else:
            return "Poor"

    def _compare_to_baseline(self, score: float) -> float:
        """Compare current score to baseline."""
        if "wellness" in self.baselines:
            return score - self.baselines["wellness"].get("mean", score)
        return 0.0

    def _generate_wellness_message(self, overall: float, greenery: float, noise: float) -> str:
        """Generate human-readable wellness message."""
        rating = self._get_wellness_rating(overall)

        if rating == "Excellent":
            return "Your wellness is excellent! Keep up the good work."
        elif rating == "Good":
            if greenery < 70:
                return "Your wellness is good. Consider improving greenery levels."
            elif noise < 70:
                return "Your wellness is good. Consider reducing noise levels."
            else:
                return "Your wellness is good overall."
        elif rating == "Fair":
            issues = []
            if greenery < 50:
                issues.append("greenery")
            if noise < 50:
                issues.append("noise")
            return f"Your wellness is fair. Focus on improving: {', '.join(issues)}."
        else:
            return "Your wellness needs attention. Multiple factors require improvement."

    def _recommend_greenery(self, data: List[Tuple]) -> List[Dict]:
        """Generate greenery-related recommendations."""
        recommendations = []

        if not data:
            return recommendations

        percentages = [row[1] for row in data]
        avg = statistics.mean(percentages)

        if avg < 10:
            recommendations.append(
                {
                    "id": f"greenery_low_{datetime.now().timestamp()}",
                    "type": "greenery",
                    "priority": "high",
                    "title": "Very low greenery detected",
                    "description": f"Your workspace greenery is at {avg:.1f}%, well below healthy levels",
                    "actions": [
                        "Add at least one desk plant (pothos or snake plant are low-maintenance)",
                        "Position desk near a window if possible",
                        "Consider a green wallpaper or nature poster",
                    ],
                    "impact": "Studies show 20%+ greenery correlates with improved focus and mood",
                    "confidence": 0.9,
                }
            )
        elif avg < 15:
            baseline = self.baselines.get("greenery", {}).get("mean", 15)
            if avg < baseline * 0.7:
                recommendations.append(
                    {
                        "id": f"greenery_below_baseline_{datetime.now().timestamp()}",
                        "type": "greenery",
                        "priority": "medium",
                        "title": "Greenery below your baseline",
                        "description": f"Current greenery ({avg:.1f}%) is below your usual level ({baseline:.1f}%)",
                        "actions": [
                            "Check if plants need watering or repositioning",
                            "Add seasonal plants or flowers",
                            "Ensure natural light reaches your workspace",
                        ],
                        "impact": "Maintaining your baseline greenery supports consistent wellness",
                        "confidence": 0.75,
                    }
                )

        return recommendations

    def _recommend_noise(self, data: List[Tuple]) -> List[Dict]:
        """Generate noise-related recommendations."""
        recommendations = []

        if not data:
            return recommendations

        db_levels = [row[1] for row in data]
        avg = statistics.mean(db_levels)

        if avg > 70:
            recommendations.append(
                {
                    "id": f"noise_high_{datetime.now().timestamp()}",
                    "type": "noise",
                    "priority": "high",
                    "title": "High noise levels detected",
                    "description": f"Average noise level is {avg:.1f} dB, which may impact concentration",
                    "actions": [
                        "Use noise-cancelling headphones during focus work",
                        "Add soft furnishings to absorb sound",
                        "Consider white noise or ambient sounds",
                        "Identify and reduce noise sources if possible",
                    ],
                    "impact": "Reducing noise to <60 dB can improve focus by up to 25%",
                    "confidence": 0.85,
                }
            )
        elif avg > 60:
            recommendations.append(
                {
                    "id": f"noise_moderate_{datetime.now().timestamp()}",
                    "type": "noise",
                    "priority": "medium",
                    "title": "Moderate noise levels",
                    "description": f"Noise levels at {avg:.1f} dB may occasionally distract",
                    "actions": [
                        "Use background music or white noise",
                        "Schedule focus time during quieter hours",
                        "Consider soft earplugs for deep work",
                    ],
                    "impact": "Optimizing noise levels can enhance productivity",
                    "confidence": 0.7,
                }
            )

        return recommendations

    def _recommend_habits(self, greenery_data: List[Tuple], noise_data: List[Tuple]) -> List[Dict]:
        """Generate habit-related recommendations."""
        recommendations = []

        # Check data consistency
        if len(greenery_data) < 5 and len(noise_data) < 5:
            recommendations.append(
                {
                    "id": f"habit_consistency_{datetime.now().timestamp()}",
                    "type": "habits",
                    "priority": "low",
                    "title": "Increase monitoring consistency",
                    "description": "More frequent monitoring helps detect patterns and trends",
                    "actions": [
                        "Enable automatic sensor polling",
                        "Check wellness dashboard daily",
                        "Review weekly reports",
                    ],
                    "impact": "Consistent monitoring enables better insights and recommendations",
                    "confidence": 0.8,
                }
            )

        return recommendations

    def _recommend_wellness(
        self, greenery_data: List[Tuple], noise_data: List[Tuple]
    ) -> List[Dict]:
        """Generate general wellness recommendations."""
        recommendations = []

        # Add a general wellness tip
        recommendations.append(
            {
                "id": f"wellness_general_{datetime.now().timestamp()}",
                "type": "wellness",
                "priority": "low",
                "title": "Maintain workspace wellness",
                "description": "Regular breaks and environmental awareness support overall wellbeing",
                "actions": [
                    "Take 5-minute breaks every hour",
                    "Practice the 20-20-20 rule for eye health",
                    "Adjust lighting to reduce glare",
                    "Stay hydrated throughout the day",
                ],
                "impact": "Holistic workspace health supports sustained productivity",
                "confidence": 0.9,
            }
        )

        return recommendations

    def _detect_recurring_issues(
        self, greenery_data: List[Tuple], noise_data: List[Tuple]
    ) -> List[Dict]:
        """Detect recurring issues in the data."""
        patterns = []

        # Check for recurring low greenery
        if len(greenery_data) >= self.MIN_SAMPLES_FOR_PATTERN:
            low_count = sum(1 for row in greenery_data if row[1] < 10)
            if low_count / len(greenery_data) > self.RECURRING_ISSUE_THRESHOLD:
                patterns.append(
                    {
                        "type": "recurring_issue",
                        "category": "greenery",
                        "description": f"Low greenery detected {low_count} times in past {len(greenery_data)} measurements",
                        "frequency": f"{(low_count / len(greenery_data) * 100):.0f}% of the time",
                        "severity": "high" if low_count / len(greenery_data) > 0.5 else "medium",
                        "recommendation": "Consider permanent greenery improvements",
                    }
                )

        # Check for recurring high noise
        if len(noise_data) >= self.MIN_SAMPLES_FOR_PATTERN:
            high_count = sum(1 for row in noise_data if row[1] > 70)
            if high_count / len(noise_data) > self.RECURRING_ISSUE_THRESHOLD:
                patterns.append(
                    {
                        "type": "recurring_issue",
                        "category": "noise",
                        "description": f"High noise levels detected {high_count} times in past {len(noise_data)} measurements",
                        "frequency": f"{(high_count / len(noise_data) * 100):.0f}% of the time",
                        "severity": "high" if high_count / len(noise_data) > 0.5 else "medium",
                        "recommendation": "Consider noise-cancelling solutions or quieter workspace",
                    }
                )

        return patterns

    def _detect_time_patterns(
        self, greenery_data: List[Tuple], noise_data: List[Tuple]
    ) -> List[Dict]:
        """Detect time-based patterns."""
        patterns = []

        # Analyze by hour of day
        if len(noise_data) >= self.MIN_SAMPLES_FOR_PATTERN:
            by_hour = defaultdict(list)
            for row in noise_data:
                hour = datetime.fromisoformat(row[0]).hour
                by_hour[hour].append(row[1])

            # Find hours with consistently high noise
            for hour, values in by_hour.items():
                if len(values) >= 3:
                    avg = statistics.mean(values)
                    if avg > 65:
                        patterns.append(
                            {
                                "type": "time_based",
                                "category": "noise",
                                "description": f"Noise consistently higher around {hour:02d}:00 ({avg:.1f} dB average)",
                                "pattern": "time_of_day",
                                "recommendation": f"Schedule focus work outside of {hour:02d}:00 hour, or use noise protection",
                            }
                        )

        return patterns

    def _detect_trend_patterns(
        self, greenery_data: List[Tuple], noise_data: List[Tuple]
    ) -> List[Dict]:
        """Detect trend patterns."""
        patterns = []

        # Check greenery trends
        if len(greenery_data) >= self.MIN_SAMPLES_FOR_PATTERN:
            values = [row[1] for row in greenery_data]
            first_half = statistics.mean(values[: len(values) // 2])
            second_half = statistics.mean(values[len(values) // 2 :])

            if second_half < first_half * 0.8:
                patterns.append(
                    {
                        "type": "trend",
                        "category": "greenery",
                        "description": f"Greenery declining over time ({first_half:.1f}% → {second_half:.1f}%)",
                        "direction": "declining",
                        "recommendation": "Review and refresh plant health, add new greenery",
                    }
                )

        return patterns

    def _update_baselines(self):
        """Update personalized baselines from historical data."""
        try:
            # Get 30 days of data for baseline
            since = datetime.now() - timedelta(days=30)
            greenery_data = self.db.get_greenery_data(since=since)
            noise_data = self.db.get_noise_data(since=since)

            # Calculate greenery baseline
            if len(greenery_data) >= self.MIN_SAMPLES_FOR_BASELINE:
                values = [row[1] for row in greenery_data]
                self.baselines["greenery"] = {
                    "mean": statistics.mean(values),
                    "stddev": statistics.stdev(values) if len(values) > 1 else 0,
                    "confidence": min(1.0, len(values) / 50),
                    "sample_size": len(values),
                }

            # Calculate noise baseline
            if len(noise_data) >= self.MIN_SAMPLES_FOR_BASELINE:
                values = [row[1] for row in noise_data]
                self.baselines["noise"] = {
                    "mean": statistics.mean(values),
                    "stddev": statistics.stdev(values) if len(values) > 1 else 0,
                    "confidence": min(1.0, len(values) / 50),
                    "sample_size": len(values),
                }

            logger.info(f"Baselines updated: {len(self.baselines)} metrics")

        except Exception as e:
            logger.error(f"Error updating baselines: {e}")

    def _baseline_recommendations(self) -> str:
        """Generate recommendations about baseline quality."""
        if not self.baselines:
            return "Continue monitoring to establish personalized baselines"

        low_confidence = [
            metric
            for metric, data in self.baselines.items()
            if data.get("confidence", 0) < self.BASELINE_CONFIDENCE_THRESHOLD
        ]

        if low_confidence:
            return f"Baselines for {', '.join(low_confidence)} need more data for high confidence"

        return "Baselines are well-established with high confidence"
