from .base import *

# Production-specific settings
DEBUG = False

ALLOWED_HOSTS = ['154.19.37.54', 'soysmart360.cloud', 'www.soysmart360.cloud']

CSRF_TRUSTED_ORIGINS = ['https://soysmart360.cloud', 'https://www.soysmart360.cloud']

# Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 3600
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_ROOT = BASE_DIR / 'staticfiles'