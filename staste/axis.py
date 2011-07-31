from staste import redis

class Axis(object):
    def __init__(self, choices):
        self.choices = choices

    def get_field_id_parts(self, value):
        if not value in self.choices:
            raise ValueError('Invalid value: %s, choices are: %s'
                             % (value, self.choices))
        
        return ['__all__', str(value)]
    

    def get_field_main_id(self, value):
        if not value:
            return '__all__'

        return str(value)

    def get_choices(self, key):
        return self.choices



class StoredChoiceAxis(Axis):
    """An Axis for which you don't know values in advance

    Stores all values in a set at some key in Redis"""

    store_choice = True

    def __init__(self):
        pass

    def get_field_id_parts(self, value):
        return ['__all__', str(value)]

    def get_choices(self, key):
        return redis.smembers(key)
