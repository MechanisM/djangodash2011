import datetime

class Metrica(object):
    """Metrica is some class of events you want to count, like "site visits".

    Metrica is actually a space of all such countable events.

    It consists of Axes, which represent some parameters of an event: for example, a page URL, or whether the visitor was logged in. Please take a look at staste.axes.Axis.

    Every time the event happens, you call Metrica.kick() function with all the parameters for all axes specified.
    """

    def __init__(self, name, axes):
        """Constructor of a Metrica

        name - should be a unique (among your metrics) string, it will be used in Redis identifiers (lots of them)
        axes - a list of staste.axes.Axis objects. can be empty"""
        self.name = str(name)
        self.axes = list(axes)

    def kick(self, date=None, **kwargs):
        date = date or datetime.datetime.now()

    def timespan(self, **kwargs):
        """Returns an MetricaValues object limited to the spefic period in time

        Please keep in mind that the timespan can't be arbitraty and is limited to years, months, days and hours"""
        mv = MetricaValues(self)
        return mv.timespan(**kwargs)


class MetricaValues(object):
    """A representation of Metrica statistical values"""
    def __init__(self, metrica, timespan=None):
        self.metrica = metrica
        self._timespan = timespan or {}

    def timespan(self, **kwargs):
        tp = dict(self._timespan, **kwargs)
        return MetricaValues(self.metrica, timespan=tp)

    @property
    def value(self):
        return 0

        
