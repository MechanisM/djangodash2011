import datetime

from django.test import TestCase
from django.conf import settings

from staste import redis
from staste.metrica import Metrica
from staste.axis import Axis

class TestStatsApi(TestCase):
    def removeAllKeys(self):
        # be careful.

        assert settings.STASTE_METRICS_PREFIX.endswith('_test')
        
        for k in redis.keys(settings.STASTE_METRICS_PREFIX + '*'):
            redis.delete(k)

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

        self.assertEquals(metrica.timespan(year=2006, month=1).total(), 3)
        self.assertEquals(metrica.timespan(year=2006, month=2).total(), 33)
        self.assertEquals(metrica.timespan(year=2006).timespan(month=2).total(), 33)
        self.assertEquals(metrica.timespan(year=2006, month=3).total(), 0)
        self.assertEquals(metrica.timespan(year=2006, month=2, day=7).total(), 20)
        self.assertEquals(metrica.timespan(year=2006).total(), 36)
        self.assertEquals(metrica.total(), 36)
                

        # looks like that


        # and also an iterator

        months = list(metrica.timespan(year=2006).iterate())[:3]
        self.assertEquals(months, [(1, 3), (2, 33), (3, 0)])
            

        years = list(metrica.timespan().iterate())
        self.assertEquals(years, [(2006, 36)])

    def testSimpleAxis(self):
        # so I grew older, and I had learned
        # how to tell if it's a boy or a girl

        gender_axis = Axis(choices=['boy', 'girl'])
        metrica = Metrica(name='guest_visits', axes=[('gender', gender_axis)])

        my_birthday = datetime.datetime(2007, 2, 7)
        # my 15th birthday.
        # you know what? I hated that year

        
        day = datetime.timedelta(days=1)
        month = datetime.timedelta(days=31)

        yesterday = my_birthday - day
        before_yesterday = yesterday - day

        prev_month = my_birthday - month
        prev_month_and_a_day_back = prev_month - day

        # my best friend came, we were playing video games
        metrica.kick(date=prev_month_and_a_day_back, gender='boy')
        
        metrica.kick(date=prev_month, gender='girl')
        metrica.kick(date=prev_month, gender='girl') # I got lucky
            
        for i in xrange(5):
            metrica.kick(date=before_yesterday, gender='boy')
            # we got really drunk

        for i in xrange(4):
            metrica.kick(date=yesterday, gender='girl')
            metrica.kick(date=yesterday, gender='boy')
            # they came in pairs. I was FOREVER ALONE
            
        for i in xrange(18): # all my friends have come
            metrica.kick(date=my_birthday, gender='boy')
        for i in xrange(2): # and two girls
            metrica.kick(date=my_birthday, gender='girl')

        # let's count them!
        
        self.assertEquals(metrica.timespan(year=2007).total(), 36)
        self.assertEquals(metrica.filter(gender='girl').total(), 8)
        self.assertEquals(metrica.timespan(year=2007, month=2).filter(gender='boy').total(), 27)

