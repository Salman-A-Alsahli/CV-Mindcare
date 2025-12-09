"""Unit tests for WebSocket Live Streaming functionality.

Tests connection management, data broadcasting, throttling, and message formatting.
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

from backend.websocket_routes import (
    ConnectionManager,
    DataThrottler,
    create_sensor_message,
    create_status_message,
    create_error_message,
)


class TestConnectionManager:
    """Tests for ConnectionManager class."""
    
    def test_init(self):
        """Test ConnectionManager initialization."""
        manager = ConnectionManager()
        assert manager.active_connections == []
        assert manager.get_connection_count() == 0
    
    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connecting a WebSocket client."""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        await manager.connect(websocket)
        
        websocket.accept.assert_awaited_once()
        assert manager.get_connection_count() == 1
        assert websocket in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting a WebSocket client."""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        await manager.connect(websocket)
        assert manager.get_connection_count() == 1
        
        await manager.disconnect(websocket)
        assert manager.get_connection_count() == 0
        assert websocket not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_disconnect_nonexistent(self):
        """Test disconnecting a client that's not connected."""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        # Should not raise an error
        await manager.disconnect(websocket)
        assert manager.get_connection_count() == 0
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self):
        """Test sending a message to a specific client."""
        manager = ConnectionManager()
        websocket = AsyncMock()
        await manager.connect(websocket)
        
        message = {"type": "test", "data": "hello"}
        await manager.send_personal_message(message, websocket)
        
        websocket.send_json.assert_awaited_once_with(message)
    
    @pytest.mark.asyncio
    async def test_send_personal_message_error(self):
        """Test handling errors when sending personal message."""
        manager = ConnectionManager()
        websocket = AsyncMock()
        websocket.send_json.side_effect = Exception("Send failed")
        await manager.connect(websocket)
        
        message = {"type": "test"}
        await manager.send_personal_message(message, websocket)
        
        # Should disconnect on error
        assert manager.get_connection_count() == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_single_client(self):
        """Test broadcasting to a single connected client."""
        manager = ConnectionManager()
        websocket = AsyncMock()
        await manager.connect(websocket)
        
        message = {"type": "broadcast", "data": "test"}
        count = await manager.broadcast(message)
        
        assert count == 1
        websocket.send_json.assert_awaited_once_with(message)
    
    @pytest.mark.asyncio
    async def test_broadcast_multiple_clients(self):
        """Test broadcasting to multiple connected clients."""
        manager = ConnectionManager()
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()
        websocket3 = AsyncMock()
        
        await manager.connect(websocket1)
        await manager.connect(websocket2)
        await manager.connect(websocket3)
        
        message = {"type": "broadcast", "data": "test"}
        count = await manager.broadcast(message)
        
        assert count == 3
        websocket1.send_json.assert_awaited_once_with(message)
        websocket2.send_json.assert_awaited_once_with(message)
        websocket3.send_json.assert_awaited_once_with(message)
    
    @pytest.mark.asyncio
    async def test_broadcast_with_errors(self):
        """Test broadcast handles client errors gracefully."""
        manager = ConnectionManager()
        websocket1 = AsyncMock()
        websocket2 = AsyncMock()
        websocket2.send_json.side_effect = Exception("Send failed")
        websocket3 = AsyncMock()
        
        await manager.connect(websocket1)
        await manager.connect(websocket2)
        await manager.connect(websocket3)
        
        message = {"type": "broadcast"}
        count = await manager.broadcast(message)
        
        # Only 2 successful sends (websocket2 failed)
        assert count == 2
        # Failed client should be removed
        assert manager.get_connection_count() == 2
        assert websocket2 not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_empty(self):
        """Test broadcasting with no connected clients."""
        manager = ConnectionManager()
        
        message = {"type": "broadcast"}
        count = await manager.broadcast(message)
        
        assert count == 0
    
    def test_get_status_idle(self):
        """Test get_status with no connections."""
        manager = ConnectionManager()
        status = manager.get_status()
        
        assert status["active_connections"] == 0
        assert status["status"] == "idle"
    
    @pytest.mark.asyncio
    async def test_get_status_running(self):
        """Test get_status with active connections."""
        manager = ConnectionManager()
        websocket = AsyncMock()
        await manager.connect(websocket)
        
        status = manager.get_status()
        
        assert status["active_connections"] == 1
        assert status["status"] == "running"


class TestDataThrottler:
    """Tests for DataThrottler class."""
    
    def test_init_default(self):
        """Test DataThrottler initialization with default rate."""
        throttler = DataThrottler()
        assert throttler.rate_hz == 5.0
        assert throttler.min_interval == 0.2
    
    def test_init_custom_rate(self):
        """Test DataThrottler initialization with custom rate."""
        throttler = DataThrottler(rate_hz=10.0)
        assert throttler.rate_hz == 10.0
        assert throttler.min_interval == 0.1
    
    def test_init_clamp_min(self):
        """Test rate clamping to minimum (1 Hz)."""
        throttler = DataThrottler(rate_hz=0.5)
        assert throttler.rate_hz == 1.0
        assert throttler.min_interval == 1.0
    
    def test_init_clamp_max(self):
        """Test rate clamping to maximum (10 Hz)."""
        throttler = DataThrottler(rate_hz=20.0)
        assert throttler.rate_hz == 10.0
        assert throttler.min_interval == 0.1
    
    def test_should_send_first_time(self):
        """Test should_send returns True on first call."""
        throttler = DataThrottler(rate_hz=5.0)
        
        # Mock event loop time
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.time.return_value = 1.0
            assert throttler.should_send() is True
    
    def test_should_send_too_soon(self):
        """Test should_send returns False if called too soon."""
        throttler = DataThrottler(rate_hz=5.0)  # min_interval = 0.2s
        
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.time.return_value = 1.0
            throttler.should_send()  # First call at t=1.0
            
            mock_loop.return_value.time.return_value = 1.1  # Only 0.1s later
            assert throttler.should_send() is False
    
    def test_should_send_after_interval(self):
        """Test should_send returns True after minimum interval."""
        throttler = DataThrottler(rate_hz=5.0)  # min_interval = 0.2s
        
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.time.return_value = 1.0
            throttler.should_send()  # First call at t=1.0
            
            mock_loop.return_value.time.return_value = 1.25  # 0.25s later
            assert throttler.should_send() is True
    
    def test_get_next_send_delay(self):
        """Test calculating delay until next send."""
        throttler = DataThrottler(rate_hz=5.0)  # min_interval = 0.2s
        
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.time.return_value = 1.0
            throttler.should_send()  # Set last_send_time to 1.0
            
            mock_loop.return_value.time.return_value = 1.1  # 0.1s elapsed
            delay = throttler.get_next_send_delay()
            assert abs(delay - 0.1) < 0.01  # Should be ~0.1s remaining
    
    def test_get_next_send_delay_ready(self):
        """Test delay is 0 when ready to send."""
        throttler = DataThrottler(rate_hz=5.0)  # min_interval = 0.2s
        
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.time.return_value = 1.0
            throttler.should_send()
            
            mock_loop.return_value.time.return_value = 1.3  # 0.3s elapsed
            delay = throttler.get_next_send_delay()
            assert delay == 0.0
    
    def test_reset(self):
        """Test resetting throttler state."""
        throttler = DataThrottler(rate_hz=5.0)
        throttler.last_send_time = 100.0
        
        throttler.reset()
        assert throttler.last_send_time == 0.0
    
    def test_set_rate(self):
        """Test updating transmission rate."""
        throttler = DataThrottler(rate_hz=5.0)
        
        throttler.set_rate(2.0)
        assert throttler.rate_hz == 2.0
        assert throttler.min_interval == 0.5
    
    def test_set_rate_clamps(self):
        """Test set_rate clamps values to 1-10 Hz."""
        throttler = DataThrottler(rate_hz=5.0)
        
        throttler.set_rate(0.5)
        assert throttler.rate_hz == 1.0
        
        throttler.set_rate(15.0)
        assert throttler.rate_hz == 10.0


class TestMessageCreation:
    """Tests for message creation functions."""
    
    def test_create_sensor_message_basic(self):
        """Test creating a basic sensor message."""
        sensor_data = {
            "camera": {"greenery_percentage": 25.5},
            "microphone": {"db_level": 45.0}
        }
        
        message = create_sensor_message(sensor_data)
        
        assert message["type"] == "sensor_data"
        assert "timestamp" in message
        assert message["sensors"] == sensor_data
        assert "system" not in message
    
    def test_create_sensor_message_with_system(self):
        """Test creating sensor message with system info."""
        sensor_data = {"camera": {"greenery_percentage": 30.0}}
        system_info = {"cpu_percent": 45.0, "memory_mb": 512}
        
        message = create_sensor_message(sensor_data, system_info)
        
        assert message["type"] == "sensor_data"
        assert message["sensors"] == sensor_data
        assert message["system"] == system_info
    
    def test_create_status_message_basic(self):
        """Test creating a basic status message."""
        message = create_status_message("connected")
        
        assert message["type"] == "status"
        assert "timestamp" in message
        assert message["status"] == "connected"
        assert "details" not in message
    
    def test_create_status_message_with_details(self):
        """Test creating status message with details."""
        details = {"rate_hz": 5.0, "connections": 3}
        message = create_status_message("running", details)
        
        assert message["type"] == "status"
        assert message["status"] == "running"
        assert message["details"] == details
    
    def test_create_error_message_basic(self):
        """Test creating a basic error message."""
        message = create_error_message("Connection failed")
        
        assert message["type"] == "error"
        assert "timestamp" in message
        assert message["error"] == "Connection failed"
        assert "code" not in message
    
    def test_create_error_message_with_code(self):
        """Test creating error message with error code."""
        message = create_error_message("Sensor unavailable", "SENSOR_ERROR")
        
        assert message["type"] == "error"
        assert message["error"] == "Sensor unavailable"
        assert message["code"] == "SENSOR_ERROR"
    
    def test_message_timestamp_format(self):
        """Test that timestamps are in ISO format with Z suffix."""
        message = create_sensor_message({})
        
        # Check timestamp format (ISO 8601 with Z)
        assert message["timestamp"].endswith("Z")
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(message["timestamp"].replace("Z", "+00:00"))


# Integration test placeholder for actual WebSocket endpoint
# Note: Full WebSocket endpoint testing requires FastAPI TestClient with WebSocket support
class TestWebSocketIntegration:
    """Integration tests for WebSocket endpoint (requires TestClient)."""
    
    def test_placeholder(self):
        """Placeholder for WebSocket integration tests.
        
        Full integration tests should be added when running with FastAPI TestClient.
        These would test:
        - WebSocket connection lifecycle
        - Real-time data streaming
        - Client commands (rate updates)
        - Error handling
        - Multiple concurrent clients
        """
        pass
