from datetime import datetime, timedelta

from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.views.generic import FormView
from django.utils import simplejson

from staste import redis
from staste.metrica import Metrica
from staste.axis import Axis, StoredChoiceAxis

from .forms import ParticipantForm, GENDERS



class EmotionView(FormView):
    form_class = ParticipantForm
    template_name = 'collector/index.html'
    
    def dispatch(self, *args, **kwargs):
        self.metrica = self._get_metrica()
        return super(EmotionView, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        self.metrica.kick(
                            date=datetime.now(), 
                            gender=form.cleaned_data['gender'],
                            age=form.cleaned_data['age']
                         )
        return HttpResponsePermanentRedirect('')
        
    def _get_metrica(self):
        gender_axis = Axis(choices=GENDERS.keys())
        age_axis = StoredChoiceAxis()
        return Metrica(name='visitors_gender_and_age', axes=[('gender', gender_axis), ('age', age_axis),])
        
    def get_context_data(self, **kwargs):
        context = super(EmotionView, self).get_context_data(**kwargs)
        context.update({'genders': self._get_genders()})
       # context.update({'ages': self._get_ages()})
        return context
        
    def _get_genders(self, time_interval=5):   
        data = []       
        now = datetime.now()       
        for i in xrange(time_interval):
            time_point = (now-timedelta(minutes=i))
            time_point_data = ['%i' % time_point.minute,]
            for gender in GENDERS.keys():                
                time_point_data.append(self.metrica.timespan(year=time_point.year, month=time_point.month, day=time_point.day, hour=time_point.hour, minute=time_point.minute).filter(gender=gender).total())
            data.append(time_point_data)
        data.reverse()
        return data
        
    #def _get_ages(self):
        #return self.metrica.filter().iterate('age')
    