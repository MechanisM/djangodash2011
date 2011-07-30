from django.conf.urls.defaults import *

from staste.charts.views import PieChart

from .views import EmotionView
from .metrics import gender_age_metrica


urlpatterns = patterns('',
                        url(r'^$', EmotionView.as_view(), name="index"),

                       url(r'^pie/', PieChart.as_view(metrica=gender_age_metrica,
                                                      axis_keyword='gender')),
                      )
