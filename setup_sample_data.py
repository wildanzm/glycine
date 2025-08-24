#!/usr/bin/env python3
"""
Script untuk membuat sample devices dan data sensor untuk testing dashboard
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glycine.settings.development')
django.setup()

from core.models import Device, SensorReading


def create_sample_devices():
    """Buat sample devices untuk testing"""
    
    # Device 1 - Online
    device1, created = Device.objects.get_or_create(
        device_uuid='AA:BB:CC:DD:EE:FF',
        defaults={
            'name': 'Raspberry Pi 4',
            'status': 'online',
            'battery_level': 90
        }
    )
    if created:
        print(f"✅ Created device: {device1.name}")
    else:
        print(f"ℹ️  Device already exists: {device1.name}")
    
    # Device 2 - Offline
    device2, created = Device.objects.get_or_create(
        device_uuid='device-002',
        defaults={
            'name': 'Sensor Lahan B',
            'status': 'offline',
            'battery_level': 25
        }
    )
    if created:
        print(f"✅ Created device: {device2.name}")
    else:
        print(f"ℹ️  Device already exists: {device2.name}")
    
    # Device 3 - Online
    device3, created = Device.objects.get_or_create(
        device_uuid='device-003',
        defaults={
            'name': 'Sensor Greenhouse',
            'status': 'online',
            'battery_level': 92
        }
    )
    if created:
        print(f"✅ Created device: {device3.name}")
    else:
        print(f"ℹ️  Device already exists: {device3.name}")
    
    return [device1, device2, device3]


def create_sample_readings(devices, num_readings=5):
    """Buat sample sensor readings untuk testing"""
    
    for device in devices:
        if device.status == 'offline':
            print(f"⏸️  Skipping readings for offline device: {device.name}")
            continue
            
        print(f"📊 Creating {num_readings} readings for {device.name}")
        
        for i in range(num_readings):
            # Generate realistic sensor data
            timestamp = datetime.now() - timedelta(minutes=i*10)
            
            reading = SensorReading.objects.create(
                device=device,
                air_temperature=round(random.uniform(22.0, 32.0), 1),
                air_humidity=round(random.uniform(50.0, 85.0), 1),
                soil_moisture=round(random.uniform(35.0, 75.0), 1),
                soil_ph=round(random.uniform(6.0, 7.5), 1),
                wind_speed=round(random.uniform(0.0, 20.0), 1),
                wind_direction=random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
                nitrogen=round(random.uniform(100.0, 180.0), 0),
                phosphorus=round(random.uniform(60.0, 120.0), 0),
                potassium=round(random.uniform(180.0, 280.0), 0),
                rainfall=round(random.uniform(0.0, 3.0), 2)
            )
            
            # Update timestamp manually untuk historical data
            SensorReading.objects.filter(id=reading.id).update(timestamp=timestamp)
            
        print(f"✅ Created {num_readings} readings for {device.name}")


def update_device_status():
    """Update status devices"""
    devices = Device.objects.all()
    
    for device in devices:
        if device.device_uuid in ['device-001', 'device-003']:
            device.status = 'online'
        else:
            device.status = 'offline'
        device.save()
        print(f"🔄 Updated {device.name} status to {device.status}")


def show_summary():
    """Tampilkan ringkasan data"""
    print("\n" + "="*50)
    print("📋 SUMMARY")
    print("="*50)
    
    devices = Device.objects.all()
    print(f"Total Devices: {devices.count()}")
    print(f"Online Devices: {devices.filter(status='online').count()}")
    print(f"Offline Devices: {devices.filter(status='offline').count()}")
    
    total_readings = SensorReading.objects.count()
    print(f"Total Sensor Readings: {total_readings}")
    
    print("\nDevices:")
    for device in devices:
        readings_count = SensorReading.objects.filter(device=device).count()
        latest_reading = SensorReading.objects.filter(device=device).order_by('-timestamp').first()
        last_update = latest_reading.timestamp if latest_reading else "No data"
        
        print(f"  • {device.name} ({device.device_uuid})")
        print(f"    Status: {device.status} | Battery: {device.battery_level}%")
        print(f"    Readings: {readings_count} | Last: {last_update}")
    
    print("\n🚀 Ready for testing!")
    print("1. Start server: python manage.py runserver")
    print("2. Open dashboard: http://localhost:8000/dashboard")
    print("3. Test IoT simulator: python iot_device_simulator.py device-001")


def main():
    print("🔧 Setting up sample data for Glycine Dashboard...")
    print("="*50)
    
    try:
        # Create devices
        devices = create_sample_devices()
        
        # Create sample readings
        create_sample_readings(devices, num_readings=3)
        
        # Update device status
        update_device_status()
        
        # Show summary
        show_summary()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
