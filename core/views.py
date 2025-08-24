from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Device, SensorReading


def dashboard(request):
    # Ambil data real dari database
    devices_data = []
    
    # Ambil semua device yang terdaftar
    devices = Device.objects.all()
    
    for device in devices:
        # Ambil reading terbaru untuk setiap device
        latest_reading = SensorReading.objects.filter(device=device).order_by('-timestamp').first()
        
        device_data = {
            'device': {
                'uuid': device.device_uuid,
                'name': device.name,
                'status': device.status,
                'battery_level': device.battery_level,
                'created_at': device.created_at,
            },
            'readings': None
        }
        
        if latest_reading:
            device_data['readings'] = {
                'id': latest_reading.id,
                'timestamp': latest_reading.timestamp,
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
    
    # Jika tidak ada device atau data, gunakan fallback
    if not devices_data:
        devices_data = [{
            'device': {
                'uuid': 'no-device',
                'name': 'Belum Ada Perangkat',
                'status': 'offline',
                'battery_level': 0,
                'created_at': None,
            },
            'readings': None
        }]

    context = {
        'devices_data': devices_data,
        'active_page': 'dashboard',
        'has_devices': len(devices) > 0,
        'online_devices_count': devices.filter(status='online').count(),
        'total_devices_count': devices.count(),
    }
    
    return render(request, 'dashboard.html', context)

def water_pump(request):
    if request.method == 'POST':
        # Contoh: Toggle status pompa air
        pump_id = request.POST.get('pump_id', 'pump_01')
        action = request.POST.get('action', 'toggle')
        
        # Simulasi toggle pompa
        is_active = action == 'on'
        
        # Kirim pesan konfirmasi
        status_message = f"Pompa air {'dinyalakan' if is_active else 'dimatikan'}"
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
                    messages.error(request, 'Anda hanya dapat memiliki 1 perangkat. Hapus perangkat yang ada untuk menambah yang baru.')
                    return redirect('device')
                
                name = request.POST.get('name', '').strip()
                mac_address = request.POST.get('mac_address', '').strip()
                
                # Enhanced validation
                if not name or not mac_address:
                    messages.error(request, 'Nama dan MAC Address tidak boleh kosong.')
                elif len(name) > 255:
                    messages.error(request, 'Nama perangkat terlalu panjang (maksimal 255 karakter).')
                elif len(mac_address) > 100:
                    messages.error(request, 'MAC Address terlalu panjang (maksimal 100 karakter).')
                elif Device.objects.filter(device_uuid=mac_address).exists():
                    messages.error(request, f'Perangkat dengan MAC Address {mac_address} sudah ada.')
                else:
                    Device.objects.create(name=name, device_uuid=mac_address)
                    messages.success(request, f'Perangkat "{name}" berhasil ditambahkan.')
            
            elif action == 'edit':
                device_id = request.POST.get('device_id', '').strip()
                name = request.POST.get('name', '').strip()
                mac_address = request.POST.get('mac_address', '').strip()
                
                if not device_id:
                    messages.error(request, 'ID perangkat tidak ditemukan.')
                elif not name or not mac_address:
                    messages.error(request, 'Nama dan MAC Address tidak boleh kosong.')
                elif len(name) > 255:
                    messages.error(request, 'Nama perangkat terlalu panjang (maksimal 255 karakter).')
                elif len(mac_address) > 100:
                    messages.error(request, 'MAC Address terlalu panjang (maksimal 100 karakter).')
                else:
                    try:
                        device = get_object_or_404(Device, pk=device_id)
                        
                        # Check if MAC Address is used by another device
                        if Device.objects.filter(device_uuid=mac_address).exclude(pk=device_id).exists():
                            messages.error(request, f'Perangkat dengan MAC Address {mac_address} sudah ada.')
                        else:
                            old_name = device.name
                            device.name = name
                            device.device_uuid = mac_address
                            device.save()
                            messages.success(request, f'Perangkat "{old_name}" berhasil diperbarui menjadi "{name}".')
                    except ValueError:
                        messages.error(request, 'ID perangkat tidak valid.')
                    except Exception as e:
                        messages.error(request, f'Terjadi kesalahan saat memperbarui perangkat: {str(e)}')

            elif action == 'delete':
                device_id = request.POST.get('device_id', '').strip()
                
                if not device_id:
                    messages.error(request, 'ID perangkat tidak ditemukan.')
                else:
                    try:
                        device = get_object_or_404(Device, pk=device_id)
                        device_name = device.name
                        device.delete()
                        messages.success(request, f'Perangkat "{device_name}" berhasil dihapus.')
                    except ValueError:
                        messages.error(request, 'ID perangkat tidak valid.')
                    except Exception as e:
                        messages.error(request, f'Terjadi kesalahan saat menghapus perangkat: {str(e)}')
            else:
                messages.error(request, f'Aksi "{action}" tidak dikenal.')
                
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan yang tidak terduga: {str(e)}')

        return redirect('device')

    # GET request - display device list
    devices = Device.objects.all().order_by('name')
    context = {
        'devices': devices,
        'active_page': 'device',
    }
    return render(request, 'device.html', context)