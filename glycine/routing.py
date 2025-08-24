# glycine/routing.py
from django.urls import re_path
from core import consumers

websocket_urlpatterns = [
    # WebSocket untuk perangkat IoT
    re_path(r'ws/device/(?P<device_uuid>[\w:-]+)/$', consumers.DeviceConsumer.as_asgi()),
    
    # WebSocket untuk dashboard browser
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
]
