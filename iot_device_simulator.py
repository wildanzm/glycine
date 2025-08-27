#!/usr/bin/env python3
"""
Script untuk simulasi perangkat IoT yang mengirim data sensor ke Django WebSocket.
Versi ini menghasilkan data yang lebih realistis dengan perubahan bertahap.
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
        # Menyimpan state data terakhir untuk simulasi yang lebih smooth
        self.last_reading = {
            "air_temperature": 28.0,
            "air_humidity": 75.0,
            "soil_moisture": 60.0,
            "soil_ph": 6.5,
            "wind_speed": 10.0,
            "nitrogen": 150.0,
            "phosphorus": 90.0,
            "potassium": 200.0,
            "rainfall": 0.0,
            "battery_level": 95
        }

    def _generate_smooth_value(self, current_value, min_val, max_val, max_change):
        """Menghasilkan nilai baru yang tidak jauh dari nilai sebelumnya."""
        change = random.uniform(-max_change, max_change)
        new_value = current_value + change
        # Pastikan nilai tetap dalam rentang yang wajar
        return max(min_val, min(new_value, max_val))

    async def connect(self):
        """Koneksi ke WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            print(f"✅ Device {self.device_uuid} connected to {self.server_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Tutup koneksi WebSocket"""
        if self.websocket:
            await self.websocket.close()
            print(f"🔌 Device {self.device_uuid} disconnected")
    
    async def send_sensor_data(self):
        """Kirim data sensor simulasi yang lebih realistis"""
        if not self.websocket:
            return False
        
        # Hasilkan data baru berdasarkan data terakhir
        self.last_reading["air_temperature"] = self._generate_smooth_value(self.last_reading["air_temperature"], 20, 35, 0.5)
        self.last_reading["air_humidity"] = self._generate_smooth_value(self.last_reading["air_humidity"], 40, 90, 2)
        self.last_reading["soil_moisture"] = self._generate_smooth_value(self.last_reading["soil_moisture"], 30, 80, 3)
        self.last_reading["soil_ph"] = self._generate_smooth_value(self.last_reading["soil_ph"], 5.5, 8.0, 0.1)
        self.last_reading["wind_speed"] = self._generate_smooth_value(self.last_reading["wind_speed"], 0, 25, 1)
        self.last_reading["nitrogen"] = self._generate_smooth_value(self.last_reading["nitrogen"], 80, 200, 5)
        self.last_reading["phosphorus"] = self._generate_smooth_value(self.last_reading["phosphorus"], 50, 150, 3)
        self.last_reading["potassium"] = self._generate_smooth_value(self.last_reading["potassium"], 150, 300, 5)
        self.last_reading["battery_level"] -= random.uniform(0.1, 0.5) # Baterai berkurang perlahan
        if self.last_reading["battery_level"] < 10: self.last_reading["battery_level"] = 95
        
        sensor_data_payload = {
            "type": "sensor_data",
            "data": {
                "air_temperature": round(self.last_reading["air_temperature"], 1),
                "air_humidity": round(self.last_reading["air_humidity"], 1),
                "soil_moisture": round(self.last_reading["soil_moisture"], 1),
                "soil_ph": round(self.last_reading["soil_ph"], 1),
                "wind_speed": round(self.last_reading["wind_speed"], 1),
                "wind_direction": random.choice(["Utara", "Tenggara", "Selatan", "Barat"]),
                "nitrogen": round(self.last_reading["nitrogen"], 0),
                "phosphorus": round(self.last_reading["phosphorus"], 0),
                "potassium": round(self.last_reading["potassium"], 0),
                "rainfall": round(random.uniform(0.0, 1.0), 2),
                "battery_level": int(self.last_reading["battery_level"])
            }
        }
        
        try:
            await self.websocket.send(json.dumps(sensor_data_payload))
            print(f"📊 Sent realistic sensor data: T={sensor_data_payload['data']['air_temperature']}°C, SM={sensor_data_payload['data']['soil_moisture']}%")
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
        """Listen untuk pesan dari server"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                print(f"📨 Received: {data}")
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed by server")
        except Exception as e:
            print(f"❌ Error listening for messages: {e}")

    async def run_simulation(self, data_interval=10):
        if not await self.connect():
            return
        
        self.is_running = True
        listen_task = asyncio.create_task(self.listen_for_messages())
        
        try:
            while self.is_running:
                await self.send_sensor_data()
                await asyncio.sleep(data_interval)
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
    parser = argparse.ArgumentParser(description='Realistic IoT Device Simulator')
    parser.add_argument('device_uuid', help='Device UUID for identification')
    parser.add_argument('--server', default='ws://localhost:8000', help='WebSocket server URL')
    parser.add_argument('--interval', type=int, default=5, help='Data sending interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    device = IoTDeviceSimulator(args.device_uuid, args.server)
    await device.run_simulation(data_interval=args.interval)

if __name__ == "__main__":
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
