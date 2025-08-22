from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Device, SensorReading

def dashboard(request):
    dummy_data = [
        {
            'device': {'name': 'Raspberry Pi 4', 'status': 'online', 'battery_level': 92},

            'readings': {
                'air_temperature': 29.5,
                'air_humidity': 76,
                'soil_moisture': 68,
                'soil_ph': 6.8,
                'wind_speed': 12.5,
                'wind_direction': 'Tenggara',
                'nitrogen': 120,
                'phosphorus': 85,
                'potassium': 210,
                'rainfall': 0.5,
            }
        }
    ]

    context = {
        'devices_data': dummy_data,
        'active_page': 'dashboard',
    }
    
    return render(request, 'dashboard.html', context)

def water_pump(request):
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