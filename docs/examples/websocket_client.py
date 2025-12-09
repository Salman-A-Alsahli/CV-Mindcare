"""WebSocket Client Example for CV-Mindcare Live Streaming.

This example demonstrates how to connect to the CV-Mindcare WebSocket endpoint
and receive real-time sensor data updates.

Usage:
    python websocket_client.py [--host localhost] [--port 8000] [--rate 5.0]

Requirements:
    pip install websockets asyncio
"""

import asyncio
import json
import argparse
import logging
from datetime import datetime
from typing import Dict

try:
    import websockets
except ImportError:
    print("Error: websockets library not installed.")
    print("Install with: pip install websockets")
    exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CVMindcareClient:
    """WebSocket client for CV-Mindcare live sensor streaming."""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialize client with server connection details.
        
        Args:
            host: Server hostname or IP
            port: Server port number
        """
        self.host = host
        self.port = port
        self.ws_url = f"ws://{host}:{port}/ws/live"
        self.websocket = None
        self.running = False
    
    async def connect(self):
        """Connect to the WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.running = True
            logger.info(f"Connected to {self.ws_url}")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from server")
    
    async def set_rate(self, rate_hz: float):
        """Update the data streaming rate.
        
        Args:
            rate_hz: Desired rate in Hz (1-10)
        """
        if not self.websocket:
            logger.error("Not connected")
            return
        
        command = {
            "command": "set_rate",
            "rate": rate_hz
        }
        
        try:
            await self.websocket.send(json.dumps(command))
            logger.info(f"Requested rate change to {rate_hz} Hz")
        except Exception as e:
            logger.error(f"Failed to set rate: {e}")
    
    async def receive_messages(self, callback=None):
        """Receive and process messages from the server.
        
        Args:
            callback: Optional callback function(message_dict)
        """
        if not self.websocket:
            logger.error("Not connected")
            return
        
        try:
            while self.running:
                message_str = await self.websocket.recv()
                message = json.loads(message_str)
                
                # Log received message
                msg_type = message.get("type", "unknown")
                timestamp = message.get("timestamp", "N/A")
                
                if msg_type == "sensor_data":
                    self._handle_sensor_data(message)
                elif msg_type == "status":
                    self._handle_status(message)
                elif msg_type == "error":
                    self._handle_error(message)
                else:
                    logger.warning(f"Unknown message type: {msg_type}")
                
                # Call custom callback if provided
                if callback:
                    callback(message)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed by server")
            self.running = False
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")
            self.running = False
    
    def _handle_sensor_data(self, message: Dict):
        """Handle sensor data messages."""
        sensors = message.get("sensors", {})
        
        logger.info("=" * 60)
        logger.info(f"Timestamp: {message.get('timestamp')}")
        
        # Camera data
        if "camera" in sensors:
            camera = sensors["camera"]
            greenery = camera.get("greenery_percentage", "N/A")
            status = camera.get("status", "N/A")
            logger.info(f"  Camera: {greenery}% greenery (status: {status})")
        
        # Microphone data
        if "microphone" in sensors:
            mic = sensors["microphone"]
            db = mic.get("db_level", "N/A")
            classification = mic.get("noise_classification", "N/A")
            status = mic.get("status", "N/A")
            logger.info(f"  Microphone: {db} dB - {classification} (status: {status})")
        
        # System info
        if "system" in message:
            system = message["system"]
            cpu = system.get("cpu_percent", "N/A")
            memory = system.get("memory_mb", "N/A")
            logger.info(f"  System: CPU {cpu}%, Memory {memory:.0f} MB")
        
        logger.info("=" * 60)
    
    def _handle_status(self, message: Dict):
        """Handle status messages."""
        status = message.get("status", "unknown")
        details = message.get("details", {})
        logger.info(f"Status: {status}")
        if details:
            logger.info(f"  Details: {details}")
    
    def _handle_error(self, message: Dict):
        """Handle error messages."""
        error = message.get("error", "unknown error")
        code = message.get("code", "")
        logger.error(f"Server error [{code}]: {error}")
    
    async def run(self, rate_hz: float = None):
        """Run the client with automatic reconnection.
        
        Args:
            rate_hz: Optional data rate to request
        """
        try:
            await self.connect()
            
            # Set rate if specified
            if rate_hz:
                await self.set_rate(rate_hz)
            
            # Start receiving messages
            await self.receive_messages()
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            await self.disconnect()


async def main():
    """Main entry point for the WebSocket client."""
    parser = argparse.ArgumentParser(
        description="CV-Mindcare WebSocket Client for Live Sensor Streaming"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Server hostname (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=None,
        help="Data streaming rate in Hz (1-10, default: server default)"
    )
    
    args = parser.parse_args()
    
    # Create and run client
    client = CVMindcareClient(host=args.host, port=args.port)
    await client.run(rate_hz=args.rate)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient stopped by user")
