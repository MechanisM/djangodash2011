import datetime

from collections import namedtuple

def days_to_seconds(days):
    """Converts days to seconds. No ".total_seconds()" in 2.6"""

    return days * 24 * 60 * 60

DATE_SCALES_AND_EXPIRATIONS = [('year', 0),
                               ('month', days_to_seconds(3*365)),
                               ('day', days_to_seconds(185)),
                               ('hour', days_to_seconds(14))]

DATE_SCALES_DICT = dict(DATE_SCALES_AND_EXPIRATIONS)

DateScale = namedtuple('DateScale', ['id', 'expiration'])

class DateAxis(object):
    def scales(self, date):
        yield DateScale('__all__', 0)

        id_parts = []
        for scale, scale_expiration in DATE_SCALES_AND_EXPIRATIONS:
            value = getattr(date, scale)
            
            id_parts += [scale, str(value)]
            yield DateScale(':'.join(id_parts), scale_expiration)

    def timespan_to_id(self, timespan):
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

        return ':'.join(id_parts)

DATE_AXIS = DateAxis()
                
