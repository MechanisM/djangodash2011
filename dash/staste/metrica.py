import datetime
import itertools

from django.conf import settings

from staste import redis
from staste.dateaxis import DATE_AXIS

class Metrica(object):
    """Metrica is some class of events you want to count, like "site visits".

    Metrica is actually a space of all such countable events.

    It consists of Axes, which represent some parameters of an event: for example, a page URL, or whether the visitor was logged in. Please take a look at staste.axes.Axis.

    Every time the event happens, you call Metrica.kick() function with all the parameters for all axes specified.
    """

    def __init__(self, name, axes):
        """Constructor of a Metrica

        name - should be a unique (among your metrics) string, it will be used in Redis identifiers (lots of them)
        axes - a list/iterable of tuples: (keyword, staste.axes.Axis object). can be empty"""
        self.name = str(name)
        self.axes = list(axes)
        self.date_axis = DATE_AXIS
        

    def kick(self, date=None, **kwargs):
        """Registers an event with parameters (for each of axis)"""
        date = date or datetime.datetime.now()
        
        hash_key_prefix = self.key_prefix()

        hash_field_id_parts = []

        for axis_kw, axis in self.axes:
            hash_field_id_parts.append(
                list(axis.get_field_id_parts(kwargs.pop(axis_kw, None)))
                )

        if kwargs:
            raise TypeError("Invalid kwargs left: %s" % kwargs)
            
        # Here we go: bumping all counters out there
        pipe = redis.pipeline(transaction=False)

        for date_scale in self.date_axis.scales(date):
            hash_key = '%s:%s' % (hash_key_prefix, date_scale.id)
            
            for parts in itertools.product(*hash_field_id_parts):
                hash_field_id = ':'.join(parts)

                pipe.hincrby(hash_key, hash_field_id, 1)
            
            if date_scale.expiration:
                pipe.expire(hash_key, date_scale.expiration)

            if date_scale.store:
                set_key = '%s:%s' % (hash_key_prefix, date_scale.store)
                pipe.sadd(set_key, date_scale.value)

        pipe.execute()

    # STATISTICS

    def values(self):
        """Returns a MetricaValues object for all the data out there"""
        return MetricaValues(self)

    def timespan(self, **kwargs):
        """Returns a MetricaValues object limited to the spefic period in time

        Please keep in mind that the timespan can't be arbitraty, it can be only a specific year, month, day, hour or minute

        Example: mymetric.timespan(year=2011, month=3, day=2)"""
        return self.values().timespan(**kwargs)

    def filter(self, **kwargs):
        """Returns a MetricaValues object filtered by one or several axes"""
        return self.values().filter(**kwargs)

    def total(self, **kwargs):
        """Total count of events"""
        return self.values().total()

    # UTILS

    def key_prefix(self):
        metrics_prefix = settings.STASTE_METRICS_PREFIX
        
        return '%s:%s' % (metrics_prefix, self.name)

    def hash_field_id(self, **kwargs):
        hash_field_id_parts = []
        
        for axis_kw, axis in self.axes:
            hash_field_id_parts.append(
                axis.get_field_main_id(kwargs.pop(axis_kw, None))
                )

        if kwargs:
            raise TypeError("Invalid kwargs left: %s" % kwargs)

        return ':'.join(hash_field_id_parts)





class MetricaValues(object):
    """A representation of a subset of Metrica statistical values

    Used for filtering"""
    
    def __init__(self, metrica, timespan=None, filter=None):
        """Constructor. You probably don't want to call it directly"""
        self.metrica = metrica
        self._timespan = timespan or {}
        self._filter = filter or {}

        # we should do it now to raise an error eagerly
        tp_id = self.metrica.date_axis.timespan_to_id(**self._timespan)
        self._hash_key = '%s:%s' % (self.metrica.key_prefix(),
                                    tp_id)
        self._hash_field_id = self.metrica.hash_field_id(**self._filter)


    # FILTERING
        
    def timespan(self, **kwargs):
        """Filter by timespan. Returns a new MetricaValues object"""
        
        tp = dict(self._timespan, **kwargs)
        return MetricaValues(self.metrica, timespan=tp, filter=self._filter)

    def filter(self, **kwargs):
        fl = dict(self._filter, **kwargs)
        return MetricaValues(self.metrica, timespan=self._timespan, filter=fl)

    # GETTING VALUES

    def total(self):
        """Total events count in the subset"""
        return int(redis.hget(self._hash_key, self._hash_field_id) or 0)

    def iterate(self):
        """Iterates on a MetricaValues set. Returns a list of (key, value) tuples.

        If axis is not specified, iterates on the next scale of a date axis. I.e. mymetric.timespan(year=2011).iterate() will iterate months."""
        
        prefix = self.metrica.key_prefix()
        keys = []

        pipe = redis.pipeline(transaction=False)
        
        for key, tp_id in self.metrica.date_axis.iterate(self):
            keys.append(key)
            
            hash_key = '%s:%s' % (prefix, tp_id)
            
            pipe.hget(hash_key, self._hash_field_id)

        values = pipe.execute()

        return zip(keys, [int(v or 0) for v in values])
            
            
        