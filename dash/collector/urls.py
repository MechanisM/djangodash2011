from django.conf.urls.defaults import *

from .views import EmotionView



urlpatterns = patterns('',
                        url(r'^$', EmotionView.as_view(), name="index"),                                                                 
                      )
