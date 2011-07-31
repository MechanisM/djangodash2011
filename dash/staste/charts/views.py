import datetime

from django.views.generic import TemplateView

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
        time_until = datetime.datetime.now()
        
        time_scale = self.request.GET.get('timescale')
        time_scale = time_scale if time_scale in [i[0] for i in DATE_SCALES_AND_EXPIRATIONS] else 'hour'
        
        axis_displayed = self.request.GET.get('show_axis')
        axis_displayed = axis_displayed if axis_displayed in [i[0] for i in self.metrica.axes] else self.metrica.axes[0][0]
        
        time_since_kwargs = {}
        for scale, _ in DATE_SCALES_AND_EXPIRATIONS:
            try:      
                time_since_for_scale = int(self.request.GET.get('%s__ago' % scale))
                time_since_kwargs.update({'%ss' % scale: time_since_for_scale})
            except TypeError:
                pass
        time_since = time_until - datetime.timedelta(**time_since_kwargs)
     
        values = {}
        for item in self.get_metrica_values().iterate(axis=axis_displayed):
            values.update({item[0]: self.get_metrica_values().filter(**{axis_displayed: item[0]}).timeserie(time_since, time_until, scale=time_scale)})
        
        axis_data = {'name': 'Timeline: %s statistic.' % axis_displayed,
                     'data': values,}

        return {'axis': axis_data}
        
        
    

class LatestCountAndAverageChart(Chart):
    template_name = 'staste/charts/latest_count_and_average.html'

    title = 'Counts and Averages'

    def get_context_data(self):
        vs = self.metrica.values()

        since = datetime.datetime.now() - datetime.timedelta(hours=1)

        data = list(vs.timeserie_counts_and_averages(since,
                                                     datetime.datetime.now()))

        return {'title': self.title,
                'axis': {'data': data}}
