import random
import datetime

from .metrics import gender_age_metrica, GENDERS

def lots_of_dummy_stats():
    for i in xrange(2000):
        minutes_ago = random.randint(1, 1600)

        dt = datetime.datetime.now() - datetime.timedelta(minutes=minutes_ago)

        gender_age_metrica.kick(date=dt,
                                gender=random.choice(GENDERS.keys()),
                                age=random.randint(1, 100))
