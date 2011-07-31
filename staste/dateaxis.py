"""DateTime axis is special-cased because it's simpler to build everything around date

For example, using separate hash keys for dates allows to set different expiration datees for keys."""
import datetime
import calendar

from dateutil import rrule

from collections import namedtuple

from staste import redis


def days_to_seconds(days):
    """Converts days to seconds. No ".total_seconds()" in 2.6"""
    return days * 24 * 60 * 60


# Please keep in mind that years are special-cased (I got to think about it)
# cause their range is not hard specified, but stored in Redis instead.

DATE_SCALES_AND_EXPIRATIONS = [('year', 0),
                               ('month', days_to_seconds(3*365)),
                               ('day', days_to_seconds(185)),
                               ('hour', days_to_seconds(14)),
                               ('minute', days_to_seconds(1))]

DATE_SCALES_DICT = dict(DATE_SCALES_AND_EXPIRATIONS)

DATE_SCALES_RANGES = {'month': lambda **t: (1, 12),
                      'day': lambda year, month, **t: (1, calendar.monthrange(year, month)[1]),
                      'hour': lambda **t: (0, 23),
                      'minute': lambda **t: (0, 59)}

DATE_SCALES_RRULE_KWARGS = {'year': {'freq': rrule.YEARLY,
                                     'bymonthday': 1},
                           'month': {'freq': rrule.MONTHLY,
                                     'bymonthday': 1},
                           'day': {'freq': rrule.DAILY},
                           'hour': {'freq': rrule.HOURLY},
                           'minute': {'freq': rrule.MINUTELY}}


# can be average
DATE_SCALES_DELTAS = {'year': datetime.timedelta(days=365),
                      'month': datetime.timedelta(days=30),
                      'day': datetime.timedelta(days=1),
                      'hour': datetime.timedelta(hours=1),
                      'minute': datetime.timedelta(minutes=1)}

DATE_SCALES_SCALE = {'year': lambda dt: datetime.datetime(dt.year, 1, 1),
                     'month': lambda dt: datetime.datetime(dt.year,
                                                           dt.month, 1),
                     'day': lambda dt: datetime.datetime(year=dt.year,
                                                         month=dt.month,
                                                         day=dt.day),
                     'hour': lambda dt: datetime.datetime(year=dt.year,
                                                          month=dt.month,
                                                          day=dt.day,
                                                          hour=dt.hour),
                     'minute': lambda dt: datetime.datetime(year=dt.year,
                                                          month=dt.month,
                                                          day=dt.day,
                                                          hour=dt.hour,
                                                          minute=dt.minute)}

# This is a tuple which is used by Metric.kick()
# to understand that it should be doing with a scale
DateScale = namedtuple('DateScale', ['id', 'expiration', 'value', 'store'])


class DateAxis(object):
    """This is a special-cased axis of DateTime"""
    
    def scales(self, date):
        """Yields DateScale objects for all scales on which the event should be stored"""
        yield DateScale('__all__', 0, '', False)

        id_parts = []
        for scale, scale_expiration in DATE_SCALES_AND_EXPIRATIONS:
            value = getattr(date, scale)
            
            id_parts += [scale, str(value)]
            yield DateScale(':'.join(id_parts),
                            scale_expiration,
                            value,
                            'years' if scale == 'year' else False)
            

    def timespan_to_id(self, **timespan):
        """Returns an string part of the hash key for a timespan

        A timespan is a dict of date scales"""

        if not timespan:
            return '__all__'
        
        id_parts = self._timespan_to_id_parts(**timespan)

        return ':'.join(id_parts)
    

    def iterate(self, mv):
        """Iterates on all date values for scale of MetricaValues. Yields a number and an id (string part of the hash key)

        For example, if MetricaValues is filtered by month (like .timespan(month=2)), this will iterate by month days."""
        
        id_parts = self._timespan_to_id_parts(**mv._timespan)

        scale_n = len(id_parts) / 2        
        try:
            scale_ = DATE_SCALES_AND_EXPIRATIONS[scale_n]
        except IndexError:
            raise ValueError("Can't iterate further than %s"
                             % DATE_SCALES_AND_EXPIRATIONS[-1][0])
        scale = scale_[0]

        for i in self.get_scale_range(scale, mv):
            yield int(i), ':'.join(id_parts + [scale, str(i)])
            

    def get_scale_range(self, scale, mv):
        """Returns a range of values for a scale, within some space of statistical values"""
        
        # okay, it's not very configurable, but I tried
        if scale == 'year':
            set_key = '%s:years' % mv.metrica.key_prefix()
            return redis.smembers(set_key)
        
        return xrange(*DATE_SCALES_RANGES[scale](**mv._timespan))


    def timeserie(self, since, until, max_scale=None):
        """Returns a list of time points and scales we can have information about"""

        now = datetime.datetime.now()

        points = []
        
        for scale, expiration in reversed(DATE_SCALES_AND_EXPIRATIONS):
            if max_scale:
                if scale == max_scale:
                    max_scale = None
                else:
                    continue
                
            if expiration:
                scale_since = now - datetime.timedelta(seconds=expiration)

                if scale_since >= until:
                    continue

                if scale_since < since:
                    scale_since = since

            else:
                scale_since = since

            points = list(self.scale_timeserie(scale, scale_since, until)) + points

            until = scale_since

            if until <= since:
                break

        for scale, point in points:
            yield point, ':'.join(self._datetime_to_id_parts(scale, point))
            

    def scale_timeserie(self, scale, since, until):
        rr = rrule.rrule(dtstart=since,
                         until=until,
                         **DATE_SCALES_RRULE_KWARGS[scale])

        for point in rr:
            yield scale, self.scale_point(scale, point)

    def scale_point(self, scale, point):
        return DATE_SCALES_SCALE[scale](point) + DATE_SCALES_DELTAS[scale]/2
    

    def _datetime_to_id_parts(self, max_scale, dt):
        id_parts = []
        
        for scale, scale_expiration in DATE_SCALES_AND_EXPIRATIONS:
            val = getattr(dt, scale)
            id_parts += [scale, str(val)]

            if scale == max_scale:
                return id_parts

        raise ValueError('Invalid scale: %s' % scale)

    
    def _timespan_to_id_parts(self, **timespan):
        """Converts timespan (a dict of date scales) to a joinable list of id parts.

        {'year': 2011, 'month': 10} => ['year', '2011', 'month': 10]"""
        
        for k in timespan:
            if k not in DATE_SCALES_DICT:
                raise TypeError('Invalid date argument: "%s"' % k)

        id_parts = []
        for scale, scale_expiration in DATE_SCALES_AND_EXPIRATIONS:
            try:
                val = timespan.pop(scale)
            except KeyError:
                if timespan:
                    raise TypeError("You should have specified %s" % scale)

                # all kwargs are gone!
                break
                
            id_parts += [scale, str(val)]

        return id_parts


# We need only one such Axis object, and it's completely thread-safe
DATE_AXIS = DateAxis()
                
