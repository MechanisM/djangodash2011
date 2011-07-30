from django.views.generic import TemplateView

import datetime

from staste.dateaxis import DATE_SCALES_AND_EXPIRATIONS

class Chart(TemplateView):
    metrica = None

    def timespan(self, vs):
        for scale, _ in DATE_SCALES_AND_EXPIRATIONS:
            try:
                timespan_val = int(self.request.GET.get('timespan__%s' % scale))
            except TypeError:
                break

            vs = vs.timespan(**{scale: timespan_val})

        return vs
    
    def get_metrica_values(self):
        vs = self.metrica.values()

        vs = self.timespan(vs)        
        
        return vs

    
class PieChart(Chart):
    template_name = 'staste/charts/pie.html'

    axis_keyword = None

    def get_context_data(self):
        values = self.get_metrica_values().iterate(self.axis_keyword)

        axis_data = {'name': self.axis_keyword,
                     'values': list(values)}
        
        return {'axis': axis_data}

class TimelineChart(Chart):
    template_name = 'staste/charts/timeline.html'

    def get_context_data(self):
        values = self.get_metrica_values().iterate()

        axis_data = {'name': 'Timeline',
                     'values': list(values)}
        
        return {'axis': axis_data}

    
class TimeserieChart(Chart):
    template_name = 'staste/charts/timeserie.html'

    def get_context_data(self):
        since = datetime.datetime.now() - datetime.timedelta(hours=4)
        
        values = self.get_metrica_values().timeserie_averages(since,
                                                     datetime.datetime.now(),
                                                     scale='minute')

        axis_data = {'name': 'Timeline',
                     'values': list(values)}
        
        return {'axis': axis_data}
    
