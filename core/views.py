from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Device, SensorReading
from django.utils import timezone
import json


def dashboard(request):
    """
    Displays the main dashboard page.
    Loads initial data for a single device only.
    Further updates are handled by WebSocket.
    """
    device = Device.objects.first()
    latest_reading = None
    historical_data = []
    
    if device:
        latest_reading = SensorReading.objects.filter(device=device).order_by('-timestamp').first()
        
        # Get last 20 readings for charts
        readings = SensorReading.objects.filter(device=device).order_by('-timestamp')[:20]
        
        # Reverse to get chronological order
        readings = reversed(readings)
        
        # Prepare data for charts
        for reading in readings:
            # Convert to Asia/Jakarta timezone
            local_time = timezone.localtime(reading.timestamp)
            
            historical_data.append({
                'timestamp': local_time.strftime('%H:%M:%S'),
                'air_temperature': float(reading.air_temperature) if reading.air_temperature else 0,
                'air_humidity': float(reading.air_humidity) if reading.air_humidity else 0,
                'soil_moisture': float(reading.soil_moisture) if reading.soil_moisture else 0,
                'soil_ph': float(reading.soil_ph) if reading.soil_ph else 7,
                'wind_speed': float(reading.wind_speed) if reading.wind_speed else 0,
                'wind_direction': reading.wind_direction if reading.wind_direction else 'N/A',
                'rainfall': float(reading.rainfall) if reading.rainfall else 0,
                'nitrogen': float(reading.nitrogen) if reading.nitrogen else 0,
                'phosphorus': float(reading.phosphorus) if reading.phosphorus else 0,
                'potassium': float(reading.potassium) if reading.potassium else 0,
            })

    context = {
        'device': device,
        'reading': latest_reading,
        'historical_data_json': json.dumps(historical_data),
        'active_page': 'dashboard',
    }
    return render(request, 'dashboard.html', context)

def water_pump(request):
    if request.method == 'POST':
        # Example: Toggle water pump status
        pump_id = request.POST.get('pump_id', 'pump_01')
        action = request.POST.get('action', 'toggle')
        
        # Simulate pump toggle
        is_active = action == 'on'
        
        # Send confirmation message
        status_message = f"Water pump has been {'turned on' if is_active else 'turned off'}"
        messages.success(request, status_message)
        return redirect('water-pump')
    
    context = {
        'active_page': 'water-pump',
    }
    return render(request, 'water-pump.html', context)

def device(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        try:
            if action == 'add':
                # Check if user already has a device (limit to 1 device)
                if Device.objects.exists():
                    messages.error(request, 'You can only have 1 device. Delete the existing device to add a new one.')
                    return redirect('device')
                
                name = request.POST.get('name', '').strip()
                mac_address = request.POST.get('mac_address', '').strip()
                
                # Enhanced validation
                if not name or not mac_address:
                    messages.error(request, 'Name and MAC Address cannot be empty.')
                elif len(name) > 255:
                    messages.error(request, 'Device name is too long (maximum 255 characters).')
                elif len(mac_address) > 100:
                    messages.error(request, 'MAC Address is too long (maximum 100 characters).')
                elif Device.objects.filter(device_uuid=mac_address).exists():
                    messages.error(request, f'Device with MAC Address {mac_address} already exists.')
                else:
                    Device.objects.create(name=name, device_uuid=mac_address)
                    messages.success(request, f'Device "{name}" successfully added.')
            
            elif action == 'edit':
                device_id = request.POST.get('device_id', '').strip()
                name = request.POST.get('name', '').strip()
                mac_address = request.POST.get('mac_address', '').strip()
                
                if not device_id:
                    messages.error(request, 'Device ID not found.')
                elif not name or not mac_address:
                    messages.error(request, 'Name and MAC Address cannot be empty.')
                elif len(name) > 255:
                    messages.error(request, 'Device name is too long (maximum 255 characters).')
                elif len(mac_address) > 100:
                    messages.error(request, 'MAC Address is too long (maximum 100 characters).')
                else:
                    try:
                        device = get_object_or_404(Device, pk=device_id)
                        
                        # Check if MAC Address is used by another device
                        if Device.objects.filter(device_uuid=mac_address).exclude(pk=device_id).exists():
                            messages.error(request, f'Device with MAC Address {mac_address} already exists.')
                        else:
                            old_name = device.name
                            device.name = name
                            device.device_uuid = mac_address
                            device.save()
                            messages.success(request, f'Device "{old_name}" successfully updated to "{name}".')
                    except ValueError:
                        messages.error(request, 'Invalid device ID.')
                    except Exception as e:
                        messages.error(request, f'An error occurred while updating the device: {str(e)}')

            elif action == 'delete':
                device_id = request.POST.get('device_id', '').strip()
                
                if not device_id:
                    messages.error(request, 'Device ID not found.')
                else:
                    try:
                        device = get_object_or_404(Device, pk=device_id)
                        device_name = device.name
                        device.delete()
                        messages.success(request, f'Device "{device_name}" successfully deleted.')
                    except ValueError:
                        messages.error(request, 'Invalid device ID.')
                    except Exception as e:
                        messages.error(request, f'An error occurred while deleting the device: {str(e)}')
            else:
                messages.error(request, f'Action "{action}" is not recognized.')
                
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')

        return redirect('device')

    # GET request - display device list
    devices = Device.objects.all().order_by('name')
    context = {
        'devices': devices,
        'active_page': 'device',
    }
    return render(request, 'device.html', context)