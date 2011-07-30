import datetime
import calendar

from collections import namedtuple

from staste import redis

def days_to_seconds(days):
    """Converts days to seconds. No ".total_seconds()" in 2.6"""

    return days * 24 * 60 * 60

DATE_SCALES_AND_EXPIRATIONS = [('year', 0),
                               ('month', days_to_seconds(3*365)),
                               ('day', days_to_seconds(185)),
                               ('hour', days_to_seconds(14))]

DATE_SCALES_DICT = dict(DATE_SCALES_AND_EXPIRATIONS)

DATE_SCALES_RANGES = {'month': lambda **t: (1, 12),
                      'day': lambda year, month, **t: (1, calendar.monthrange(year, month)[1]),
                      'hour': lambda **t: (0, 23)}

DateScale = namedtuple('DateScale', ['id', 'expiration', 'value', 'store'])

class DateAxis(object):
    def scales(self, date):
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
        id_parts = self._timespan_to_id_parts(**timespan)

        return ':'.join(id_parts)
    

    def iterate(self, mv):
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
        # okay, it's not very configurable, but I tried
        if scale == 'year':
            set_key = '%s:years' % mv.metrica.key_prefix()
            return redis.smembers(set_key)
        
        return xrange(*DATE_SCALES_RANGES[scale](**mv._timespan))

        

    def _timespan_to_id_parts(self, **timespan):
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


DATE_AXIS = DateAxis()
                
