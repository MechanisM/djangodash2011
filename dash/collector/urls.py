from django.conf.urls.defaults import *

from staste.charts.views import PieChart, TimeserieChart
from staste.middleware import response_time_metrica

from .views import EmotionView
from .metrics import gender_age_metrica


urlpatterns = patterns('',
                       url(r'^$', EmotionView.as_view(), name="index"),

                       url(r'^pie/$',
                           PieChart.as_view(metrica=gender_age_metrica,
                                            axis_keyword='gender'),
                           name='gender_pie'),

                       url(r'^timeline/$',
                           TimeserieChart.as_view(metrica=gender_age_metrica),
                           name='gender_timeline'),

                       url(r'^requests/pie/$',
                           PieChart.as_view(metrica=response_time_metrica,
                                            axis_keyword='view'),
                          name='requests_pie'),

                       url(r'^requests/$',
                           TimeserieChart.as_view(metrica=response_time_metrica),
                           name='requests_timeserie')
                      )
