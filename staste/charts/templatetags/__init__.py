
from django.conf import settings

from redis import Redis

redis = Redis(**getattr(settings, 'STASTE_REDIS_CONNECTION', {}))

if not settings.STASTE_METRICS_PREFIX:
    settings.STASTE_METRICS_PREFIX = 'staste'
