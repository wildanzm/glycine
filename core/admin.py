from django.contrib import admin
from .models import Device, SensorReading

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_uuid', 'status', 'battery_level', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'device_uuid')

@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('device', 'timestamp', 'air_temperature', 'soil_moisture', 'soil_ph')
    list_filter = ('device',)
    date_hierarchy = 'timestamp'