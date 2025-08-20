import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import glycine.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glycine.settings.development')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        glycine.routing.websocket_urlpatterns
    ),
})