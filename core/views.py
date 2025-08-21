from django.shortcuts import render

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