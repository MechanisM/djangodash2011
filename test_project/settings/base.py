from defaults import *

INSTALLED_APPS += ('staste',
                   'test_app')

STASTE_METRICS_PREFIX = 'staste'

try:
    from local_settings import *
    
    STASTE_REDIS_CONNECTION = {'host': GONDOR_REDIS_HOST,
                               'port': GONDOR_REDIS_PORT,
                               'password': GONDOR_REDIS_PASSWORD}


except ImportError:
    pass


DEBUG = True
TEMPLATE_DEBUG = True


MIDDLEWARE_CLASSES = (
    'staste.middleware.ResponseTimeMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',)
