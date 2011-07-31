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
    """
    Shows the current metric's chosen axis in the context of the specified time period (from somewhen back untill now).
    Defining view's class parameters:
        TimeserieChart.metrica                            - an instance of staste.metrica.Metrica class - 
                                             specifies the metric the view is dealing with;
        TimeserieChart.template_name                      - specifies the template the output would be rendered with.
    Context:
       {{ axis.name }}                         - the name of presented axis (described below);
       {{ axis.data }}                         - a dict, where keys are current axis' possible choices and values are lists of tuples
                                             of time-marked results
                                             (e.g. {
                                                    'male':   [
                                                                (datetime.datetime(2007, 1, 2, 3, 4, 5), 12),
                                                                (datetime.datetime(2007, 1, 2, 4, 4, 5), 7),
                                                              ],
                                                    'female': [
                                                                (datetime.datetime(2007, 1, 2, 3, 4, 5), 9),
                                                                (datetime.datetime(2007, 1, 2, 4, 4, 5), 21),
                                                              ],
                                                    }
                                             );
    Accepts GET-parameters:
        'show_axis'                        - specifies the metric's axis to present (e.g. '?show_axis=gender'.);
                                             default = current metric's first axis;
        a set of '{timescale}__ago' params - where {timescale} in ['year', 'month', 'day', 'hour', 'minute'] - 
                                             defines a period of time 'ago' for which the results would be aggregated
                                            (e.g. '?year__ago=2' would provide you with data regarding the past two years);
                                            default is 5 minutes;
        'timescale'                        - a timescale parameter, defines the discreteness of aggregated data
                                            (e.g. '?timescale=minute' will provide you with 'per-minute' statistic);
                                            default = 'minute'.
                                            
        A full example:
            http://mysite.com/path_to_this_view/?show_axis=age&day_ago=3&hour_ago=1&timescale=hour
            will show you frequency of inclision of all visitors' ages over the past 73 hours.
        
        Note, that you don't want to use some highly distributed value as 'show_axis' parameter, due to all of those cases would be drawn in your chart and would
        certainly flood it over.      
    """
    template_name = 'staste/charts/timeserie.html'

    def get_context_data(self):
        time_until = datetime.datetime.now()
        
        time_scale = self.request.GET.get('timescale')
        time_scale = time_scale if time_scale in [i[0] for i in DATE_SCALES_AND_EXPIRATIONS] else 'minute'
        
        axis_displayed = self.request.GET.get('show_axis')
        axis_displayed = axis_displayed if axis_displayed in [i[0] for i in self.metrica.axes] else self.metrica.axes[0][0]
        
        time_since_kwargs = {'minutes': 5,}
        for scale, _ in DATE_SCALES_AND_EXPIRATIONS:
            try:      
                time_since_for_scale = int(self.request.GET.get('%s__ago' % scale))
                time_since_kwargs.update({'%ss' % scale: time_since_for_scale})
            except (TypeError, ValueError):
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

    scales = [#'year', 'month', 'day',
        'hour', 'minute']

    scale_deltas = {'year': datetime.timedelta(days=365*5),
                    'month': datetime.timedelta(days=730),
                    'day': datetime.timedelta(days=31),
                    'hour': datetime.timedelta(days=2),
                    'minute': datetime.timedelta(minutes=30)}

    def get_context_data(self):

        scale = self.request.GET.get('scale')
        if scale not in self.scales:
            scale = 'minute'
        
        vs = self.metrica.values()

        since = datetime.datetime.now() - self.scale_deltas[scale]

        data = list(vs.timeserie_counts_and_averages(since,
                                                     datetime.datetime.now(),
                                                     scale=scale))

        return {'title': self.title,
                'axis': {'data': data},
                'scales': self.scales,
                'current_scale': scale
                }
