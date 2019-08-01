# Overrides
#from .settings import *  # noqa: F401


DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

SECRET_KEY = ""

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
TEMPLATED_EMAIL_BACKEND = 'templated_email.backends.vanilla_django'

EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.example.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'username@example.com'
EMAIL_HOST_PASSWORD = 'mysecretpassword'
DEFAULT_FROM_EMAIL = 'username@example.com'
#"""