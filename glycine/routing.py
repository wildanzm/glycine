# glycine/routing.py
from django.urls import re_path
from core import consumers

websocket_urlpatterns = [
    # WebSocket for IoT devices
    re_path(r'ws/device/(?P<device_uuid>[\w:-]+)/$', consumers.DeviceConsumer.as_asgi()),
    
    # WebSocket for the browser dashboard
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
]
