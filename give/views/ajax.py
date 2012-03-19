from django.contrib.auth import login as auth_login
from django.http import HttpResponseBadRequest as DjangoResponseBadRequest, \
        HttpResponse as DjangoResponse
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_protect

from give.forms import DataloveAuthenticationForm

def _find_content_and_convert(args,kwargs):
    if (len(args) > 0):
        content = args[0]
        args = args[1:]
    else:
        content = kwargs.pop('content',{})
    return json.dumps(content)

class HttpResponse(DjangoResponse):
    def __init__(self, *args, **kwargs):
        content = _find_content_and_convert(args,kwargs)
        super(HttpResponse, self).__init__(content, *args, **kwargs)
        self['Content-Type'] = 'application/json'

class HttpResponseBadRequest(DjangoResponseBadRequest):
    def __init__(self, *args, **kwargs):
        content = _find_content_and_convert(args,kwargs)
        super(HttpResponseBadRequest, self).__init__(content, *args, **kwargs)
        self['Content-Type'] = 'application/json'

def login(request):
    if request.method != 'POST':
        return HttpResponseBadRequest({}) 
    form = DataloveAuthenticationForm(data=request.POST)
    if form.is_valid():
        auth_login(request,form.get_user())
        return HttpResponse()
    else:
        data = dict()
        data['errors'] = dict()
        for field,error in form.errors.items():
            data['errors'][field.strip('_')] = error.as_ul()
        return HttpResponse(errors)
