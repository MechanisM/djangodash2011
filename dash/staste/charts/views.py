from django.views.generic import TemplateView

from staste.dateaxis import DATE_SCALES_AND_EXPIRATIONS

class PieChart(TemplateView):
    template_name = 'staste/charts/pie.html'
    metrica = None
    axis_keyword = None

    def get_metrica_values(self):
        vs = self.metrica.values()

        for scale, _ in DATE_SCALES_AND_EXPIRATIONS:
            try:
                timespan_val = int(self.request.GET.get('timespan__%s' % scale))
            except TypeError:
                break

            vs = vs.timespan(**{scale: timespan_val})
        
        return vs

    def get_context_data(self):
        values = self.get_metrica_values().iterate(self.axis_keyword)

        axis_data = {'name': self.axis_keyword,
                     'values': list(values)}
        
        return {'axis': axis_data}
