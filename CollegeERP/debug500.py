import sys
import traceback


def debug500(request):
    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_value is None:
        return __import__('django.http', fromlist=['HttpResponseServerError']).HttpResponseServerError('NO EXCEPTION INFO')
    detail = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    return __import__('django.http', fromlist=['HttpResponseServerError']).HttpResponseServerError(
        '<pre>%s</pre>' % detail
    )
