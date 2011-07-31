from django.http import HttpResponseRedirect
from django.views.generic import FormView

from staste import redis

from .forms import ParticipantForm, GENDERS
from .metrics import gender_age_metrica


class IndexView(FormView):
    form_class = ParticipantForm
    template_name = 'test_app/index.html'

    def get_context_data(self, *args, **kwargs):
        data = super(IndexView, self).get_context_data(*args, **kwargs)
        data['redis_memory'] = redis.info()['used_memory_human']
        return data
      
    def form_valid(self, form):
        gender_age_metrica.kick(
                            gender=form.cleaned_data['gender'],
                            age=form.cleaned_data['age']
                         )
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', '/')) 
