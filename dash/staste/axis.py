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

