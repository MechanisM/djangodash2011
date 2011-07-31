from django import forms
from django.utils.translation import ugettext_lazy as _



GENDERS = {
            'male': _(u'Male'),
            'female': _(u'Female'),
            'unknown': _(u'None of your business!'),
          }
          
          
class ParticipantForm(forms.Form):
    """
    A simple form to get some simple data.
    """
    gender = forms.ChoiceField(label=_(u'gender'), choices=GENDERS.items())
    age = forms.IntegerField(label=_(u'age'), max_value=100, min_value=1, required=False)
