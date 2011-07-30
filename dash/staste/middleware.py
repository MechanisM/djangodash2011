import time

from staste.metrica import AveragedMetrica
from staste.axis import StoredChoiceAxis

response_time_metrica = AveragedMetrica('response_time_metrica',
                                        [('view', StoredChoiceAxis()),
                                         ('exception', StoredChoiceAxis())],
                                        multiplier=10000)

class ResponseTimeMiddleware(object):
    def process_request(self, request):
        request._staste_kicked = False
        request._staste_time_start = time.time()
        request._staste_params = {'view': None,
                                  'exception': None} 
        

    def process_view(self, request, view_func, view_args, view_kwargs):
        module = view_func.__module__
        func = view_func.__name__
        request._staste_params['view'] = '%s.%s' % (module, func)

    def process_response(self, request, response):
        self._kick(request)

        return response

    def process_exception(self, request, exception):
        request._staste_params['exception'] = exception.__class__.__name__

        self._kick(request)
        

    def _kick(self, request):
        """In my experience, both process_exception and process_response can be called, or only process_exception"""

        if request._staste_kicked:
            return
        request._staste_kicked = True
        
        total_time = time.time() - request._staste_time_start

        response_time_metrica.kick(value=total_time,
                                   **request._staste_params)
        
