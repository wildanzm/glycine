import json
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from .models import Device, SensorReading


class DeviceConsumer(AsyncWebsocketConsumer):
    """WebSocket Consumer to receive data from IoT devices"""
    
    async def connect(self):
        """Called when an IoT device connects to the WebSocket"""
        self.device_uuid = self.scope['url_route']['kwargs']['device_uuid']
        self.device = None
        
        try:
            self.device = await self.get_device(self.device_uuid)
            if self.device:
                await self.update_device_status(self.device, 'online')
                await self.accept()
                
                await self.send(text_data=json.dumps({
                    'type': 'connection_established',
                    'message': f'Device {self.device_uuid} connected successfully',
                    'timestamp': datetime.now().isoformat()
                }))
            else:
                await self.close(code=4004)
                
        except Exception:
            await self.close(code=4000)

    async def disconnect(self, close_code):
        """Called when the IoT device disconnects"""
        if self.device:
            await self.update_device_status(self.device, 'offline')

    async def receive(self, text_data):
        """Receives sensor data from the IoT device"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            
            if message_type == 'sensor_data':
                await self._handle_sensor_data(data.get('data', {}))
            elif message_type == 'heartbeat':
                await self._handle_heartbeat()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing data: {str(e)}'
            }))

    async def _handle_sensor_data(self, sensor_data):
        """Handle sensor data processing"""
        reading = await self.save_sensor_reading(self.device, sensor_data)
        
        if reading:
            # Update battery level if provided
            battery_level = sensor_data.get('battery_level')
            if battery_level is not None:
                await self.update_device_battery(self.device, battery_level)
            
            # Broadcast to dashboard
            await self.broadcast_to_dashboard(reading, sensor_data)
            
            # Send confirmation
            await self.send(text_data=json.dumps({
                'type': 'data_received',
                'message': 'Sensor data saved successfully',
                'reading_id': reading.id,
                'timestamp': reading.timestamp.isoformat()
            }))
        else:
            raise Exception("Failed to save sensor reading")

    async def _handle_heartbeat(self):
        """Handle heartbeat message"""
        await self.send(text_data=json.dumps({
            'type': 'heartbeat_ack',
            'timestamp': datetime.now().isoformat()
        }))

    @database_sync_to_async
    def get_device(self, device_uuid):
        """Get device by UUID"""
        try:
            return Device.objects.get(device_uuid=device_uuid)
        except ObjectDoesNotExist:
            return None

    @database_sync_to_async
    def update_device_status(self, device, status):
        """Update device status"""
        device.status = status
        device.save(update_fields=['status'])

    @database_sync_to_async
    def update_device_battery(self, device, battery_level):
        """Update device battery level"""
        device.battery_level = battery_level
        device.save(update_fields=['battery_level'])

    @database_sync_to_async
    def save_sensor_reading(self, device, sensor_data):
        """Save sensor reading to database"""
        try:
            return SensorReading.objects.create(
                device=device,
                air_temperature=sensor_data.get('air_temperature'),
                air_humidity=sensor_data.get('air_humidity'),
                soil_moisture=sensor_data.get('soil_moisture'),
                soil_ph=sensor_data.get('soil_ph'),
                wind_speed=sensor_data.get('wind_speed'),
                wind_direction=sensor_data.get('wind_direction'),
                nitrogen=sensor_data.get('nitrogen'),
                phosphorus=sensor_data.get('phosphorus'),
                potassium=sensor_data.get('potassium'),
                rainfall=sensor_data.get('rainfall')
            )
        except Exception:
            return None

    async def broadcast_to_dashboard(self, reading, sensor_data):
        """Broadcast sensor data to dashboard group"""
        try:
            message_data = {
                'type': 'sensor_update',
                'device_uuid': self.device_uuid,
                'device_name': self.device.name,
                'reading_id': reading.id,
                'timestamp': reading.timestamp.isoformat(),
                'data': sensor_data
            }
            
            await self.channel_layer.group_send(
                'dashboard_group',
                {
                    'type': 'sensor_data_update',
                    'message': message_data
                }
            )
        except Exception:
            pass  # Fail silently for broadcast errors


class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket Consumer for the browser dashboard"""
    
    async def connect(self):
        """Called when the browser connects to the dashboard WebSocket"""
        self.group_name = 'dashboard_group'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to dashboard',
            'timestamp': datetime.now().isoformat()
        }))
        
        await self.send_online_devices()

    async def disconnect(self, close_code):
        """Called when the dashboard disconnects"""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receives messages from the browser dashboard"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            
            if message_type == 'get_devices':
                await self.send_online_devices()
            elif message_type == 'get_latest_readings':
                device_uuid = data.get('device_uuid')
                await self.send_latest_readings(device_uuid)
            elif message_type == 'get_dashboard_data':
                await self.send_dashboard_data()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'echo',
                    'message': f'Received: {data.get("message", "")}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def sensor_data_update(self, event):
        """Handler to receive sensor data updates from DeviceConsumer"""
        message = event['message']
        await self.send(text_data=json.dumps(message))

    async def device_status_update(self, event):
        """Handler for device status updates"""
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def get_online_devices(self):
        """Get list of online devices"""
        return list(Device.objects.filter(status='online').values(
            'device_uuid', 'name', 'status', 'battery_level'
        ))

    @database_sync_to_async
    def get_dashboard_data(self):
        """Get complete dashboard data"""
        try:
            devices_data = []
            devices = Device.objects.all()
            
            for device in devices:
                latest_reading = SensorReading.objects.filter(device=device).order_by('-timestamp').first()
                
                device_data = {
                    'device': {
                        'uuid': device.device_uuid,
                        'name': device.name,
                        'status': device.status,
                        'battery_level': device.battery_level,
                        'created_at': device.created_at.isoformat() if device.created_at else None,
                    },
                    'readings': None
                }
                
                if latest_reading:
                    device_data['readings'] = {
                        'id': latest_reading.id,
                        'timestamp': latest_reading.timestamp.isoformat(),
                        'air_temperature': latest_reading.air_temperature,
                        'air_humidity': latest_reading.air_humidity,
                        'soil_moisture': latest_reading.soil_moisture,
                        'soil_ph': latest_reading.soil_ph,
                        'wind_speed': latest_reading.wind_speed,
                        'wind_direction': latest_reading.wind_direction,
                        'nitrogen': latest_reading.nitrogen,
                        'phosphorus': latest_reading.phosphorus,
                        'potassium': latest_reading.potassium,
                        'rainfall': latest_reading.rainfall,
                    }
                
                devices_data.append(device_data)
            
            # Calculate device counts
            total_devices = devices.count()
            online_devices = devices.filter(status='online').count()
            offline_devices = total_devices - online_devices
            
            return {
                'devices_data': devices_data,
                'total_devices_count': total_devices,
                'online_devices_count': online_devices,
                'offline_devices_count': offline_devices,
                'has_devices': total_devices > 0
            }
        except Exception:
            return {
                'devices_data': [],
                'total_devices_count': 0,
                'online_devices_count': 0,
                'offline_devices_count': 0,
                'has_devices': False
            }

    @database_sync_to_async
    def get_latest_readings_for_device(self, device_uuid, limit=10):
        """Get latest sensor readings for specific device"""
        try:
            readings = SensorReading.objects.filter(
                device__device_uuid=device_uuid
            ).order_by('-timestamp')[:limit]
            
            return [
                {
                    'id': reading.id,
                    'timestamp': reading.timestamp.isoformat(),
                    'air_temperature': reading.air_temperature,
                    'air_humidity': reading.air_humidity,
                    'soil_moisture': reading.soil_moisture,
                    'soil_ph': reading.soil_ph,
                    'wind_speed': reading.wind_speed,
                    'wind_direction': reading.wind_direction,
                    'nitrogen': reading.nitrogen,
                    'phosphorus': reading.phosphorus,
                    'potassium': reading.potassium,
                    'rainfall': reading.rainfall,
                }
                for reading in readings
            ]
        except:
            return []

    async def send_dashboard_data(self):
        """Send complete dashboard data to client"""
        dashboard_data = await self.get_dashboard_data()
        await self.send(text_data=json.dumps({
            'type': 'devices_data',
            **dashboard_data,
            'timestamp': datetime.now().isoformat()
        }))

    async def send_online_devices(self):
        """Send list of online devices to dashboard"""
        devices = await self.get_online_devices()
        await self.send(text_data=json.dumps({
            'type': 'online_devices',
            'devices': devices,
            'timestamp': datetime.now().isoformat()
        }))

    async def send_latest_readings(self, device_uuid):
        """Send latest sensor readings for specific device"""
        if device_uuid:
            readings = await self.get_latest_readings_for_device(device_uuid)
            await self.send(text_data=json.dumps({
                'type': 'latest_readings',
                'device_uuid': device_uuid,
                'readings': readings,
                'timestamp': datetime.now().isoformat()
            }))
