from django import forms
from django.utils.translation import ugettext_lazy as _



GENDERS = {
            'male': _(u'Male'),
            'female': _(u'Female'),
            'unknown': _(u'Not your business!'),
          }
          
          
class ParticipantForm(forms.Form):
    """
    """
    #email = forms.EmailField(label=_(u'email'))
    #name = forms.CharField(label=_(u'name'), max_length=64)
    gender = forms.ChoiceField(label=_(u'gender'), choices=GENDERS.items())
    age = forms.IntegerField(label=_(u'age'), max_value=100, min_value=1)
    #emotion = forms.CharField(label=_('feeling (succinctly)'), max_length=32)
    
    #def __init__(self, *args, **kwargs):
    #    super(ParticipantForm, self).__init__(*args, **kwargs)
    #    self.fields['emotion'].widget = forms.Textarea()
        