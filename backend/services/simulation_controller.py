"""
Simulation Controller for CV-Mindcare

Provides robust simulation engine with scenario-based data generation.
Replaces basic mock mode with intelligent, scenario-driven simulation.
"""

import random
import math
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class SimulationScenario(str, Enum):
    """Predefined simulation scenarios."""
    
    CALM_FLOW = "calm"
    HIGH_STRESS = "stress"
    DYNAMIC = "dynamic"
    CUSTOM = "custom"


class SimulationController:
    """
    Simulation Engine for generating realistic sensor data patterns.
    
    Features:
    - Scenario-based data generation (Calm, Stress, Dynamic)
    - Time-series evolution with natural variation
    - Correlated multi-sensor data
    - Realistic noise and fluctuations
    
    Scenarios:
    - CALM_FLOW: High greenery (60-90%), Low noise (20-40dB), Positive emotions
    - HIGH_STRESS: Low greenery (5-20%), High noise (70-95dB), Negative emotions  
    - DYNAMIC: Fluctuates between calm and stress over time
    - CUSTOM: User-defined parameters
    
    Usage:
        controller = SimulationController()
        controller.set_scenario("calm")
        data = controller.generate_sensor_data()
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize simulation controller.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.active = False
        self.current_scenario = SimulationScenario.CALM_FLOW
        self.start_time: Optional[datetime] = None
        
        # Custom scenario parameters
        self.custom_params = {
            "greenery_range": (0, 100),
            "noise_range": (0, 100),
            "emotion_happy": 0.5,
            "emotion_neutral": 0.3,
            "emotion_sad": 0.2,
        }
        
        # Dynamic scenario state
        self._dynamic_phase = 0.0  # Phase for sinusoidal transitions
        self._dynamic_state = "calm"  # Current state in dynamic mode
        
        logger.info("SimulationController initialized")
    
    def start(self, scenario: str = "calm") -> bool:
        """
        Start simulation with specified scenario.
        
        Args:
            scenario: Scenario name ("calm", "stress", "dynamic", "custom")
            
        Returns:
            bool: True if started successfully
        """
        try:
            self.set_scenario(scenario)
            self.active = True
            self.start_time = datetime.now()
            self._dynamic_phase = 0.0
            logger.info(f"Simulation started with scenario: {scenario}")
            return True
        except Exception as e:
            logger.error(f"Failed to start simulation: {e}")
            return False
    
    def stop(self) -> bool:
        """
        Stop simulation.
        
        Returns:
            bool: True if stopped successfully
        """
        try:
            self.active = False
            self.start_time = None
            logger.info("Simulation stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop simulation: {e}")
            return False
    
    def set_scenario(self, scenario: str) -> None:
        """
        Set the current simulation scenario.
        
        Args:
            scenario: Scenario name
            
        Raises:
            ValueError: If scenario is invalid
        """
        scenario_lower = scenario.lower()
        
        if scenario_lower == "calm":
            self.current_scenario = SimulationScenario.CALM_FLOW
        elif scenario_lower == "stress":
            self.current_scenario = SimulationScenario.HIGH_STRESS
        elif scenario_lower == "dynamic":
            self.current_scenario = SimulationScenario.DYNAMIC
        elif scenario_lower == "custom":
            self.current_scenario = SimulationScenario.CUSTOM
        else:
            raise ValueError(f"Invalid scenario: {scenario}")
        
        logger.info(f"Scenario set to: {self.current_scenario}")
    
    def set_custom_parameters(self, params: Dict[str, Any]) -> None:
        """
        Set custom simulation parameters.
        
        Args:
            params: Dictionary of custom parameters
        """
        self.custom_params.update(params)
        logger.info(f"Custom parameters updated: {params}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current simulation status.
        
        Returns:
            Dict with simulation status information
        """
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "active": self.active,
            "scenario": self.current_scenario.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime": uptime,
            "dynamic_state": self._dynamic_state if self.current_scenario == SimulationScenario.DYNAMIC else None,
        }
    
    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """
        Get list of available scenarios with descriptions.
        
        Returns:
            List of scenario information dictionaries
        """
        return [
            {
                "id": "calm",
                "name": "Calm Flow",
                "description": "High greenery, low noise, positive emotions. Ideal workspace conditions.",
                "greenery": "60-90%",
                "noise": "20-40 dB (Quiet)",
                "emotion": "Positive (Happy, Content)",
            },
            {
                "id": "stress",
                "name": "High Stress",
                "description": "Low greenery, high noise, negative emotions. Stressful environment.",
                "greenery": "5-20%",
                "noise": "70-95 dB (Very Noisy)",
                "emotion": "Negative (Stressed, Anxious)",
            },
            {
                "id": "dynamic",
                "name": "Dynamic",
                "description": "Fluctuates between calm and stress over time. Simulates changing conditions.",
                "greenery": "Variable",
                "noise": "Variable",
                "emotion": "Variable",
            },
            {
                "id": "custom",
                "name": "Custom",
                "description": "User-defined parameters for testing specific scenarios.",
                "greenery": "Custom",
                "noise": "Custom",
                "emotion": "Custom",
            },
        ]
    
    def generate_sensor_data(self) -> Dict[str, Any]:
        """
        Generate complete sensor data based on current scenario.
        
        Returns:
            Dict containing camera, microphone, and emotion data
        """
        if not self.active:
            logger.warning("Attempting to generate data while simulation is inactive")
        
        # Update dynamic phase if in dynamic mode
        if self.current_scenario == SimulationScenario.DYNAMIC:
            self._update_dynamic_phase()
        
        return {
            "camera": self.generate_camera_data(),
            "microphone": self.generate_microphone_data(),
            "emotion": self.generate_emotion_data(),
            "timestamp": datetime.now().isoformat(),
            "scenario": self.current_scenario.value,
        }
    
    def generate_camera_data(self) -> Dict[str, Any]:
        """
        Generate camera sensor data (greenery detection).
        
        Returns:
            Dict with greenery percentage and metadata
        """
        greenery_pct = self._get_greenery_value()
        
        # Add realistic variation (±2%)
        variation = random.uniform(-2, 2)
        greenery_pct = max(0, min(100, greenery_pct + variation))
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "camera",
            "greenery_percentage": round(greenery_pct, 2),
            "resolution": (640, 480),
            "simulation_mode": True,
            "scenario": self.current_scenario.value,
        }
    
    def generate_microphone_data(self) -> Dict[str, Any]:
        """
        Generate microphone sensor data (noise analysis).
        
        Returns:
            Dict with dB levels and classification
        """
        db_level = self._get_noise_value()
        
        # Add realistic fluctuation (±3 dB)
        fluctuation = random.uniform(-3, 3)
        db_level = max(0, min(100, db_level + fluctuation))
        
        # Classify noise level
        if db_level < 30:
            classification = "Quiet"
        elif db_level < 50:
            classification = "Normal"
        elif db_level < 70:
            classification = "Moderate"
        elif db_level < 85:
            classification = "Noisy"
        else:
            classification = "Very Noisy"
        
        # Calculate raw dB (assuming reference of -60)
        db_reference = -60.0
        raw_db = db_reference + (db_level / 100.0) * abs(db_reference)
        rms = 10 ** (raw_db / 20.0)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "microphone",
            "db_level": round(db_level, 2),
            "raw_db": round(raw_db, 2),
            "rms_amplitude": round(rms, 6),
            "noise_classification": classification,
            "simulation_mode": True,
            "scenario": self.current_scenario.value,
        }
    
    def generate_emotion_data(self) -> Dict[str, Any]:
        """
        Generate emotion detection data.
        
        Returns:
            Dict with emotion probabilities
        """
        emotions = self._get_emotion_values()
        
        # Ensure probabilities sum to 1.0
        total = sum(emotions.values())
        if total > 0:
            emotions = {k: v / total for k, v in emotions.items()}
        
        # Determine dominant emotion
        dominant = max(emotions.items(), key=lambda x: x[1])[0]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "emotion",
            "emotions": {k: round(v, 3) for k, v in emotions.items()},
            "dominant_emotion": dominant,
            "simulation_mode": True,
            "scenario": self.current_scenario.value,
        }
    
    def _get_greenery_value(self) -> float:
        """Get greenery percentage based on current scenario."""
        if self.current_scenario == SimulationScenario.CALM_FLOW:
            return random.uniform(60, 90)
        elif self.current_scenario == SimulationScenario.HIGH_STRESS:
            return random.uniform(5, 20)
        elif self.current_scenario == SimulationScenario.DYNAMIC:
            return self._get_dynamic_greenery()
        else:  # CUSTOM
            range_min, range_max = self.custom_params["greenery_range"]
            return random.uniform(range_min, range_max)
    
    def _get_noise_value(self) -> float:
        """Get noise level (dB) based on current scenario."""
        if self.current_scenario == SimulationScenario.CALM_FLOW:
            return random.uniform(20, 40)
        elif self.current_scenario == SimulationScenario.HIGH_STRESS:
            return random.uniform(70, 95)
        elif self.current_scenario == SimulationScenario.DYNAMIC:
            return self._get_dynamic_noise()
        else:  # CUSTOM
            range_min, range_max = self.custom_params["noise_range"]
            return random.uniform(range_min, range_max)
    
    def _get_emotion_values(self) -> Dict[str, float]:
        """Get emotion probabilities based on current scenario."""
        if self.current_scenario == SimulationScenario.CALM_FLOW:
            return {
                "happy": random.uniform(0.6, 0.9),
                "neutral": random.uniform(0.1, 0.3),
                "sad": random.uniform(0.0, 0.1),
                "angry": random.uniform(0.0, 0.05),
                "surprised": random.uniform(0.0, 0.1),
            }
        elif self.current_scenario == SimulationScenario.HIGH_STRESS:
            return {
                "happy": random.uniform(0.0, 0.1),
                "neutral": random.uniform(0.1, 0.2),
                "sad": random.uniform(0.2, 0.4),
                "angry": random.uniform(0.3, 0.5),
                "surprised": random.uniform(0.0, 0.2),
            }
        elif self.current_scenario == SimulationScenario.DYNAMIC:
            return self._get_dynamic_emotions()
        else:  # CUSTOM
            return {
                "happy": self.custom_params["emotion_happy"],
                "neutral": self.custom_params["emotion_neutral"],
                "sad": self.custom_params["emotion_sad"],
                "angry": 1.0 - (self.custom_params["emotion_happy"] + 
                               self.custom_params["emotion_neutral"] + 
                               self.custom_params["emotion_sad"]),
                "surprised": 0.0,
            }
    
    def _update_dynamic_phase(self) -> None:
        """Update the dynamic phase for time-based transitions."""
        if not self.start_time:
            return
        
        # Calculate elapsed time in seconds
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        # Complete cycle every 2 minutes (120 seconds)
        # Phase ranges from 0 to 2π
        self._dynamic_phase = (elapsed / 120.0) * 2 * math.pi
        
        # Determine current state based on sine wave
        # Positive = calm, Negative = stress
        wave_value = math.sin(self._dynamic_phase)
        self._dynamic_state = "calm" if wave_value > 0 else "stress"
    
    def _get_dynamic_greenery(self) -> float:
        """Get greenery value for dynamic scenario."""
        # Smooth transition between calm (60-90) and stress (5-20) states
        wave = math.sin(self._dynamic_phase)  # -1 to 1
        
        # Map wave to greenery range
        # wave = 1 (calm): ~75% greenery
        # wave = -1 (stress): ~12.5% greenery
        # wave = 0 (transition): ~43.75% greenery
        calm_avg = 75  # Middle of 60-90
        stress_avg = 12.5  # Middle of 5-20
        
        base_value = stress_avg + (calm_avg - stress_avg) * (wave + 1) / 2
        
        # Add variation
        variation = random.uniform(-5, 5)
        return max(0, min(100, base_value + variation))
    
    def _get_dynamic_noise(self) -> float:
        """Get noise value for dynamic scenario."""
        # Inverse of greenery - high when stressed, low when calm
        wave = math.sin(self._dynamic_phase)  # -1 to 1
        
        # Map wave to noise range (inverse relationship)
        # wave = 1 (calm): ~30 dB
        # wave = -1 (stress): ~82.5 dB
        # wave = 0 (transition): ~56.25 dB
        calm_avg = 30  # Middle of 20-40
        stress_avg = 82.5  # Middle of 70-95
        
        base_value = stress_avg - (stress_avg - calm_avg) * (wave + 1) / 2
        
        # Add fluctuation
        fluctuation = random.uniform(-3, 3)
        return max(0, min(100, base_value + fluctuation))
    
    def _get_dynamic_emotions(self) -> Dict[str, float]:
        """Get emotion values for dynamic scenario."""
        wave = math.sin(self._dynamic_phase)  # -1 to 1
        
        # Smooth blend between calm and stress emotions
        # wave = 1 (calm): positive emotions
        # wave = -1 (stress): negative emotions
        blend_factor = (wave + 1) / 2  # 0 to 1
        
        # Blend between stress and calm emotions
        happy = 0.05 + blend_factor * 0.7  # 0.05 to 0.75
        sad = 0.3 - blend_factor * 0.25  # 0.05 to 0.3
        angry = 0.4 - blend_factor * 0.35  # 0.05 to 0.4
        neutral = 0.15 + blend_factor * 0.05  # 0.15 to 0.2
        surprised = 0.1 - blend_factor * 0.05  # 0.05 to 0.1
        
        return {
            "happy": max(0, happy + random.uniform(-0.05, 0.05)),
            "neutral": max(0, neutral + random.uniform(-0.05, 0.05)),
            "sad": max(0, sad + random.uniform(-0.05, 0.05)),
            "angry": max(0, angry + random.uniform(-0.05, 0.05)),
            "surprised": max(0, surprised + random.uniform(-0.05, 0.05)),
        }
