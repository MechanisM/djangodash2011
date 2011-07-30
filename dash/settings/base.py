from .defaults import *

INSTALLED_APPS += ('dash.staste',)

from local_settings import *

STASTE_REDIS_CONNECTION = {'host': GONDOR_REDIS_HOST,
                           'port': GONDOR_REDIS_PORT,
                           'password': GONDOR_REDIS_PASSWORD}
