from datetime import datetime

from django.http import HttpResponsePermanentRedirect
from django.views.generic import FormView

from .forms import ParticipantForm, GENDERS
from .metrics import gender_age_metrica


class IndexView(FormView):
    form_class = ParticipantForm
    template_name = 'test_app/index.html'
      
    def form_valid(self, form):
        gender_age_metrica.kick(
                            date=datetime.now(), 
                            gender=form.cleaned_data['gender'],
                            age=form.cleaned_data['age']
                         )
        return HttpResponsePermanentRedirect('') 
