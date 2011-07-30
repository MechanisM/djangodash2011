import datetime

from django.test import TestCase
from django.conf import settings

import staste
from staste.metrics import Metrica

class TestStatsApi(TestCase):
    def removeAllKeys(self):        
        for k in staste.redis.keys(settings.STASTE_METRICS_PREFIX + '*'):
            staste.redis.delete(k)

    def setUp(self):
        self.old_prefix = getattr(settings, 'STASTE_METRICS_PREFIX', 'metrica')
        settings.STASTE_METRICS_PREFIX = self.old_prefix + '_test'
        
        self.removeAllKeys()

    def tearDown(self):
        self.removeAllKeys()
        
        settings.STASTE_METRICS_PREFIX = self.old_prefix

            
    def testTheSimplestCase(self):
        # so we want to count my guests
        # and they all alike to me, I'm a sociopath
        # so we want only to count them in time

        metrica = Metrica(name='guest_visits', axes=[])

        my_birthday = datetime.datetime(2006, 2, 7) # my 14th birthday. sorry for that
        day = datetime.timedelta(days=1)
        month = datetime.timedelta(days=31)

        yesterday = my_birthday - day
        before_yesterday = yesterday - day

        prev_month = my_birthday - month
        prev_month_and_a_day_back = prev_month - day

        metrica.kick(date=prev_month_and_a_day_back)
        for i in xrange(2):
            metrica.kick(date=prev_month)

            
        for i in xrange(5):
            metrica.kick(date=before_yesterday)

        for i in xrange(8):
            metrica.kick(date=yesterday)

        for i in xrange(20): # all my friends have come
            metrica.kick(date=my_birthday)


        # so, how many of them have visited me?

        self.assertEquals(metrica.timespan(year=2006, month=1).value, 3)
        self.assertEquals(metrica.timespan(year=2006, month=2).value, 33)
        self.assertEquals(metrica.timespan(year=2006, month=3).value, 0)
        self.assertEquals(metrica.timespan(year=2006, month=2, day=7).value, 20)
        self.assertEquals(metrica.timespan(year=2006).value, 36)

        # looks like that

            
