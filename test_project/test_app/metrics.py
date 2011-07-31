from staste.metrica import Metrica
from staste.axis import Axis, StoredChoiceAxis

from .forms import GENDERS



gender_axis = Axis(choices=GENDERS.keys())

age_axis = StoredChoiceAxis()

gender_age_metrica = Metrica(name='visitors_gender_and_age',
                             axes=[('gender', gender_axis),
                                   ('age', age_axis),])
