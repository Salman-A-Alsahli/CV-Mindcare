"""WebSocket Live Streaming for Real-Time Sensor Data.

This module implements WebSocket endpoints for streaming sensor data in real-time
to connected clients. Supports multiple concurrent connections, data throttling,
and graceful disconnection handling.

Phase 6: WebSocket Live Streaming
Target Hardware: Raspberry Pi 5 (ARM64) optimized
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts sensor data.

    Features:
    - Multiple concurrent client connections
    - Thread-safe connection management
    - Automatic cleanup on disconnect
    - Broadcast to all active clients
    - Individual client messaging
    """

    def __init__(self):
        """Initialize connection manager with empty connection list."""
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection.

        Args:
            websocket: The WebSocket connection to register
        """
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
            logger.info(f"New WebSocket connection. Total active: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from active list.

        Args:
            websocket: The WebSocket connection to remove
        """
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                logger.info(f"WebSocket disconnected. Total active: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict, websocket: WebSocket) -> None:
        """Send a message to a specific client.

        Args:
            message: Dictionary to send as JSON
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self.disconnect(websocket)

    async def broadcast(self, message: Dict) -> int:
        """Broadcast a message to all connected clients.

        Args:
            message: Dictionary to broadcast as JSON

        Returns:
            Number of clients that successfully received the message
        """
        disconnected = []
        successful = 0

        async with self._lock:
            connections = self.active_connections.copy()

        for connection in connections:
            try:
                await connection.send_json(message)
                successful += 1
            except (WebSocketDisconnect, RuntimeError, Exception) as e:
                logger.warning(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        if disconnected:
            async with self._lock:
                for conn in disconnected:
                    if conn in self.active_connections:
                        self.active_connections.remove(conn)

        return successful

    def get_connection_count(self) -> int:
        """Get the number of active connections.

        Returns:
            Number of active WebSocket connections
        """
        return len(self.active_connections)

    def get_status(self) -> Dict:
        """Get current connection manager status.

        Returns:
            Dictionary with connection statistics
        """
        return {
            "active_connections": len(self.active_connections),
            "status": "running" if len(self.active_connections) > 0 else "idle",
        }


class DataThrottler:
    """Controls data transmission rate to prevent overwhelming clients.

    Features:
    - Configurable rate limit (Hz)
    - Last transmission tracking
    - Minimum interval enforcement
    """

    def __init__(self, rate_hz: float = 5.0):
        """Initialize throttler with specified rate.

        Args:
            rate_hz: Maximum transmission rate in Hz (1-10)
        """
        self.rate_hz = max(1.0, min(10.0, rate_hz))  # Clamp between 1-10 Hz
        self.min_interval = 1.0 / self.rate_hz
        self.last_send_time = 0.0

    def should_send(self) -> bool:
        """Check if enough time has passed to send next message.

        Returns:
            True if message should be sent, False otherwise
        """
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_send_time >= self.min_interval:
            self.last_send_time = current_time
            return True
        return False

    def get_next_send_delay(self) -> float:
        """Calculate delay until next message can be sent.

        Returns:
            Delay in seconds until next message
        """
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - self.last_send_time
        return max(0.0, self.min_interval - elapsed)

    def reset(self) -> None:
        """Reset throttler state."""
        self.last_send_time = 0.0

    def set_rate(self, rate_hz: float) -> None:
        """Update transmission rate.

        Args:
            rate_hz: New transmission rate in Hz (1-10)
        """
        self.rate_hz = max(1.0, min(10.0, rate_hz))
        self.min_interval = 1.0 / self.rate_hz


def create_sensor_message(sensor_data: Dict, system_info: Dict = None) -> Dict:
    """Create a standardized sensor data message for WebSocket transmission.

    Args:
        sensor_data: Dictionary containing sensor readings
        system_info: Optional system resource information

    Returns:
        Formatted message dictionary
    """
    message = {
        "type": "sensor_data",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sensors": sensor_data,
    }

    if system_info:
        message["system"] = system_info

    return message


def create_status_message(status: str, details: Dict = None) -> Dict:
    """Create a status message for WebSocket transmission.

    Args:
        status: Status string (e.g., "connected", "error", "stopped")
        details: Optional additional details

    Returns:
        Formatted status message dictionary
    """
    message = {"type": "status", "timestamp": datetime.utcnow().isoformat() + "Z", "status": status}

    if details:
        message["details"] = details

    return message


def create_error_message(error: str, code: str = None) -> Dict:
    """Create an error message for WebSocket transmission.

    Args:
        error: Error message string
        code: Optional error code

    Returns:
        Formatted error message dictionary
    """
    message = {"type": "error", "timestamp": datetime.utcnow().isoformat() + "Z", "error": error}

    if code:
        message["code"] = code

    return message


# Global connection manager instance
manager = ConnectionManager()

# Global throttler instance (5 Hz default)
throttler = DataThrottler(rate_hz=5.0)


async def websocket_endpoint(websocket: WebSocket, sensor_manager=None):
    """WebSocket endpoint for streaming live sensor data.

    Endpoint: /ws/live

    Features:
    - Real-time sensor data streaming
    - Configurable throttling (1-10 Hz)
    - Automatic reconnection support
    - Graceful disconnection handling

    Message Types:
    - sensor_data: Periodic sensor readings
    - status: Connection/system status updates
    - error: Error notifications

    Args:
        websocket: The WebSocket connection
        sensor_manager: Optional SensorManager instance for live data
    """
    await manager.connect(websocket)

    try:
        # Send welcome message
        await manager.send_personal_message(
            create_status_message(
                "connected",
                {"message": "WebSocket connection established", "rate_hz": throttler.rate_hz},
            ),
            websocket,
        )

        # Main streaming loop
        while True:
            # Wait for messages from client (for configuration updates)
            try:
                # Non-blocking receive with timeout
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)

                # Handle client commands
                if data.get("command") == "set_rate":
                    rate = float(data.get("rate", 5.0))
                    throttler.set_rate(rate)
                    await manager.send_personal_message(
                        create_status_message("rate_updated", {"rate_hz": throttler.rate_hz}),
                        websocket,
                    )

            except asyncio.TimeoutError:
                # No message received, continue streaming
                pass
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    create_error_message("Invalid JSON", "JSON_ERROR"), websocket
                )
                continue

            # Stream sensor data if throttle allows
            if throttler.should_send() and sensor_manager:
                try:
                    # Get sensor data from manager
                    sensor_data = sensor_manager.read_all()

                    # Get system info (optional)
                    import psutil

                    system_info = {
                        "cpu_percent": psutil.cpu_percent(interval=0.1),
                        "memory_mb": psutil.virtual_memory().used / (1024 * 1024),
                    }

                    # Create and send message
                    message = create_sensor_message(sensor_data, system_info)
                    await manager.send_personal_message(message, websocket)

                except Exception as e:
                    logger.error(f"Error reading sensor data: {e}")
                    await manager.send_personal_message(
                        create_error_message(str(e), "SENSOR_ERROR"), websocket
                    )

            # Small delay to prevent CPU spinning
            await asyncio.sleep(throttler.min_interval / 2)

    except WebSocketDisconnect:
        logger.info("Client disconnected normally")
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)
