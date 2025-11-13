from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Device, SensorReading
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from datetime import datetime, time
import json
import os
import threading

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Global cache for TFLite model (thread-safe)
_interpreter_cache = None
_rekomendasi_cache = None
_model_lock = threading.Lock()
_model_loaded = False


def dashboard(request):
    """
    Displays the main dashboard page with TODAY'S data only.
    Data automatically resets when the day changes.
    Further real-time updates are handled by WebSocket.
    """
    device = Device.objects.first()
    latest_reading = None
    historical_data = []
    
    if device:
        # Get current date in Asia/Jakarta timezone
        jakarta_tz = timezone.get_current_timezone()
        now = timezone.now()
        today = timezone.localtime(now).date()
        
        # Define start and end of today in Jakarta timezone
        start_of_day = timezone.make_aware(datetime.combine(today, time.min))
        end_of_day = timezone.make_aware(datetime.combine(today, time.max))
        
        # Get latest reading from today only
        latest_reading = SensorReading.objects.filter(
            device=device,
            timestamp__gte=start_of_day,
            timestamp__lte=end_of_day
        ).order_by('-timestamp').first()
        
        # Get all readings from today for charts (limit to last 100 for performance)
        readings = SensorReading.objects.filter(
            device=device,
            timestamp__gte=start_of_day,
            timestamp__lte=end_of_day
        ).order_by('-timestamp')[:100]
        
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
        'current_date': timezone.localtime(timezone.now()).strftime('%d %B %Y'),
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


def soysmart_ai(request):
    """
    SoySmart AI - Soybean disease detection using TensorFlow Lite
    Supports 8 disease classes with confidence scoring
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            with _model_lock:
                global _interpreter_cache, _rekomendasi_cache, _model_loaded
                
                # Lazy load model on first request
                if _interpreter_cache is None and not _model_loaded:
                    try:
                        import tensorflow as tf
                        from PIL import Image
                        import io
                        import numpy as np
                        
                        BASE_DIR = Path(__file__).resolve().parent.parent
                        model_path = os.path.join(BASE_DIR, 'model', 'model_kedelai_v1.tflite')
                        rekomendasi_path = os.path.join(BASE_DIR, 'model', 'rekomendasi.json')
                        
                        if not os.path.exists(model_path):
                            return JsonResponse({'error': 'Model tidak ditemukan'}, status=500)
                        
                        # Initialize TFLite interpreter
                        _interpreter_cache = tf.lite.Interpreter(model_path=model_path)
                        _interpreter_cache.allocate_tensors()
                        
                        # Load disease information
                        with open(rekomendasi_path, 'r', encoding='utf-8') as f:
                            _rekomendasi_cache = json.load(f)
                        
                        _model_loaded = True
                        
                    except Exception as e:
                        return JsonResponse({'error': f'Gagal memuat model: {str(e)}'}, status=500)
                
                if _interpreter_cache is None:
                    return JsonResponse({'error': 'Model belum berhasil dimuat'}, status=500)
                
                # Import required libraries
                from PIL import Image
                import io
                import numpy as np
                
                # Validate image upload
                if 'image' not in request.FILES:
                    return JsonResponse({'error': 'Tidak ada file gambar'}, status=400)
                
                img_file = request.FILES['image']
                if not img_file.content_type.startswith('image/'):
                    return JsonResponse({'error': 'File harus berupa gambar'}, status=400)
                
                # Preprocess image for model input (224x224 RGB)
                img = Image.open(io.BytesIO(img_file.read()))
                img = img.convert('RGB')
                img = img.resize((224, 224), Image.BILINEAR)
                img_array = np.array(img, dtype=np.float32) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                
                # Perform inference
                try:
                    input_details = _interpreter_cache.get_input_details()
                    output_details = _interpreter_cache.get_output_details()
                    
                    _interpreter_cache.set_tensor(input_details[0]['index'], img_array)
                    _interpreter_cache.invoke()
                    predictions = _interpreter_cache.get_tensor(output_details[0]['index'])
                    
                    # Extract prediction results
                    labels = list(_rekomendasi_cache.keys())
                    predicted_index = np.argmax(predictions[0])
                    confidence = float(predictions[0][predicted_index])
                    predicted_class = labels[predicted_index]
                    
                    # Return disease information with recommendations
                    disease_info = _rekomendasi_cache[predicted_class]
                    return JsonResponse({
                        'penyakit': predicted_class,
                        'nama_ilmiah': disease_info['nama_ilmiah'],
                        'deskripsi': disease_info['deskripsi'],
                        'rekomendasi': disease_info['rekomendasi'],
                        'confidence': confidence
                    })
                    
                except Exception as e:
                    return JsonResponse({'error': f'Gagal melakukan prediksi: {str(e)}'}, status=500)
            
        except Exception as e:
            return JsonResponse({'error': f'Terjadi kesalahan: {str(e)}'}, status=500)
    
    # GET request - render upload page
    return render(request, 'soysmart-ai.html', {'active_page': 'soysmart-ai'})
