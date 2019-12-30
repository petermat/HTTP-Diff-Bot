# Overrides
#from .settings import *  # noqa: F401


DEBUG = False

SITE_URL = 'http://localhost:8000/'
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

SECRET_KEY = ""

CHROME_PATH = '/usr/bin/chromium-browser'
CHROMEDRIVER_PATH = '/snap/bin/chromium.chromedriver'

# Trun these ON when running on https
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False


# Email Settings

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.example.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'username@example.com'
EMAIL_HOST_PASSWORD = 'mysecretpassword'
DEFAULT_FROM_EMAIL = 'username@example.com'
