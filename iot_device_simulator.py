#!/usr/bin/env python3
"""
Script to simulate an IoT device sending sensor data to a Django WebSocket.
Use this script to test DeviceConsumer.
"""

import asyncio
import websockets
import json
import random
import time
import argparse
from datetime import datetime


class IoTDeviceSimulator:
    def __init__(self, device_uuid, server_url="ws://localhost:8000"):
        self.device_uuid = device_uuid
        self.server_url = f"{server_url}/ws/device/{device_uuid}/"
        self.websocket = None
        self.is_running = False
        
    async def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            print(f"✅ Device {self.device_uuid} connected to {self.server_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Close the WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            print(f"🔌 Device {self.device_uuid} disconnected")
    
    async def send_sensor_data(self):
        """Send simulated sensor data"""
        if not self.websocket:
            return False
            
        # Generate simulated sensor data
        sensor_data = {
            "type": "sensor_data",
            "data": {
                "air_temperature": round(random.uniform(20.0, 35.0), 1),
                "air_humidity": round(random.uniform(40.0, 90.0), 1),
                "soil_moisture": round(random.uniform(30.0, 80.0), 1),
                "soil_ph": round(random.uniform(5.5, 8.0), 1),
                "wind_speed": round(random.uniform(0.0, 25.0), 1),
                "wind_direction": random.choice(["Barat", "Timur Laut", "Utara", "Tenggara", "Selatan", "Barat Daya", "Barat Laut"]),
                "nitrogen": round(random.uniform(80.0, 200.0), 0),
                "phosphorus": round(random.uniform(50.0, 150.0), 0),
                "potassium": round(random.uniform(150.0, 300.0), 0),
                "rainfall": round(random.uniform(0.0, 5.0), 2),
                "battery_level": random.randint(10, 100)
            }
        }
        
        try:
            await self.websocket.send(json.dumps(sensor_data))
            print(f"📊 Sent sensor data: T={sensor_data['data']['air_temperature']}°C, "
                  f"H={sensor_data['data']['air_humidity']}%, "
                  f"SM={sensor_data['data']['soil_moisture']}%")
            return True
        except Exception as e:
            print(f"❌ Failed to send data: {e}")
            return False
    
    async def send_heartbeat(self):
        """Send a heartbeat to keep the connection alive"""
        if not self.websocket:
            return False
            
        heartbeat = {
            "type": "heartbeat",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            await self.websocket.send(json.dumps(heartbeat))
            print(f"💓 Heartbeat sent")
            return True
        except Exception as e:
            print(f"❌ Failed to send heartbeat: {e}")
            return False
    
    async def listen_for_messages(self):
        """Listen for messages from the server"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                print(f"📨 Received: {data}")
                
                # Handle different response types
                if data.get('type') == 'connection_established':
                    print(f"✅ Connection confirmed by server")
                elif data.get('type') == 'data_received':
                    print(f"✅ Server confirmed data receipt (ID: {data.get('reading_id')})")
                elif data.get('type') == 'error':
                    print(f"❌ Server error: {data.get('message')}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed by server")
        except Exception as e:
            print(f"❌ Error listening for messages: {e}")
    
    async def run_simulation(self, duration_minutes=10, data_interval=30, heartbeat_interval=60):
        """
        Run the IoT device simulation.

        Args:
            duration_minutes: Simulation duration in minutes.
            data_interval: Interval for sending sensor data (seconds).
            heartbeat_interval: Heartbeat interval (seconds).
        """
        if not await self.connect():
            return
        
        self.is_running = True
        start_time = time.time()
        last_data_time = 0
        last_heartbeat_time = 0
        
        print(f"🚀 Starting simulation for {duration_minutes} minutes")
        print(f"📊 Data interval: {data_interval}s, Heartbeat interval: {heartbeat_interval}s")
        
        # Start listening task
        listen_task = asyncio.create_task(self.listen_for_messages())
        
        try:
            while self.is_running and (time.time() - start_time) < (duration_minutes * 60):
                current_time = time.time()
                
                # Send sensor data
                if current_time - last_data_time >= data_interval:
                    await self.send_sensor_data()
                    last_data_time = current_time
                
                # Send heartbeat
                if current_time - last_heartbeat_time >= heartbeat_interval:
                    await self.send_heartbeat()
                    last_heartbeat_time = current_time
                
                # Sleep briefly to avoid blocking
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️ Simulation stopped by user")
        finally:
            self.is_running = False
            listen_task.cancel()
            await self.disconnect()
    
    async def send_single_reading(self):
        """Send a single reading for testing"""
        if await self.connect():
            await self.send_sensor_data()
            await asyncio.sleep(2)  # Wait for response
            await self.disconnect()


async def main():
    parser = argparse.ArgumentParser(description='IoT Device Simulator for Django WebSocket')
    parser.add_argument('device_uuid', help='Device UUID for identification')
    parser.add_argument('--server', default='ws://localhost:8000', 
                       help='WebSocket server URL (default: ws://localhost:8000)')
    parser.add_argument('--duration', type=int, default=10, 
                       help='Simulation duration in minutes (default: 10)')
    parser.add_argument('--data-interval', type=int, default=30, 
                       help='Data sending interval in seconds (default: 30)')
    parser.add_argument('--heartbeat-interval', type=int, default=60, 
                       help='Heartbeat interval in seconds (default: 60)')
    parser.add_argument('--single', action='store_true', 
                       help='Send single reading and exit')
    
    args = parser.parse_args()
    
    device = IoTDeviceSimulator(args.device_uuid, args.server)
    
    if args.single:
        print(f"📤 Sending single reading from device {args.device_uuid}")
        await device.send_single_reading()
    else:
        await device.run_simulation(
            duration_minutes=args.duration,
            data_interval=args.data_interval,
            heartbeat_interval=args.heartbeat_interval
        )


if __name__ == "__main__":
    # Install dependencies: pip install websockets
    asyncio.run(main())


"""
How to use:

1. Install dependencies:
   pip install websockets

2. Make sure the device is registered in the Django database:
   python manage.py shell
   >>> from core.models import Device
   >>> Device.objects.create(device_uuid='device-001', name='Test Device 1')

3. Run the simulation:
   python iot_device_simulator.py device-001
   
   Or with custom parameters:
   python iot_device_simulator.py device-001 --duration 5 --data-interval 10
   
   Or send a single reading:
   python iot_device_simulator.py device-001 --single

4. View the data on the dashboard: http://localhost:8000/dashboard
"""
