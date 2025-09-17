from .base import *

# Production-specific settings
DEBUG = False

ALLOWED_HOSTS = ['154.19.37.54', 'soysmart360.cloud', 'www.soysmart360.cloud']

CSRF_TRUSTED_ORIGINS = ['https://soysmart360.cloud', 'https://www.soysmart360.cloud']