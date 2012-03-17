from django.contrib.auth import login as auth_login
from django.http import HttpResponseBadRequest as DjangoResponseBadRequest, \
        HttpResponse as DjangoResponse
from django.utils import simplejson as json
from django.views.decorators.csrf import csrf_protect

from give.forms import DataloveAuthenticationForm

class HttpResponse(DjangoResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponse, self).__init__(*args, **kwargs)
        self['Content-Type'] = 'application/json'

class HttpResponseBadRequest(DjangoResponseBadRequest):
    def __init__(self, *args, **kwargs):
        super(HttpResponseBadRequest, self).__init__(*args, **kwargs)
        self['Content-Type'] = 'application/json'

from django.shortcuts import get_object_or_404, render_to_response
def login(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('{}') 
    form = DataloveAuthenticationForm(data=request.POST)
    if form.is_valid():
        auth_login(request,form.get_user())
        return HttpResponse()
    else:
        errors = dict()
        for field,error in form.errors.items():
            errors[field.strip('_')] = error.as_ul()
        return HttpResponse(json.dumps(errors))
