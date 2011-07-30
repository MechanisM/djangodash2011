
from django.conf import settings

from redis import Redis

redis = Redis(**getattr(settings, 'STASTE_REDIS_CONNECTION', {}))

if not getattr(settings, 'STASTE_METRICS_PREFIX', None):
    settings.STASTE_METRICS_PREFIX = 'staste'
