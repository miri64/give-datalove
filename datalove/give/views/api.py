from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, get_list_or_404
import django.utils.simplejson as json
from give.models import *

from collections import namedtuple

import _common as common

API_LOGIN_URL=settings.LOGIN_URL

_FORMAT_LIST = ['json']

class HttpResponseUnauthorized(HttpResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponseUnauthorized,self).__init__(*args,**kwargs)
        self.status_code = 401

class _apicall(object):
    def __init__(self):
        self.apiview = None

    def set_format(self, *args, **kwargs):
        Format = namedtuple('Format', 'resp_encode resp_mimetype req_decode')
        if 'format' != self.apiview.func_code.co_varnames[0]:
            raise ValueError("'%s' is no apicall. Needs argument 'format' as first argument." % \
                    self.abiview.__name__)
        if 'format' in kwargs:
            format = kwargs.pop('format')
        else:
            format = 'json'
        if format not in _FORMAT_LIST:
            raise Http404
        if format == 'json':
            form = Format(json.dumps, 'application/json', json.loads)
        args = tuple([form] + list(args))
        return self.apiview(*args,**kwargs)

    def __call__(self, apiview):
        self.apiview = apiview
        return self.set_format

def _respond(
        ResponseObjectType=HttpResponse, 
        content='', 
        mimetype=settings.DEFAULT_CONTENT_TYPE,
    ):
    return ResponseObjectType(
            content=content,
            mimetype=mimetype,
            content_type=mimetype
        )

def _not_logged_in_response():
    return _respond(
            HttpResponseUnauthorized,
            content=format.resp_encode({'error': 'You are not logged in.'}),
            mimetype=format.resp_mimetype
        )

def api_doc(request):
    return common.render_to_response2(request, 'give/api.html')

def get_history_dicts(selection=None, *args, **kwargs):
    return [m.get_history_dict(selection) for m in \
            DataloveHistory.objects.filter(*args,**kwargs)
        ][:30]

@_apicall()
def get_history(format, request):
    if not request.user.is_authenticated():
        return _not_logged_in_response()
    history = {}
    profile = get_object_or_404(DataloveProfile, pk=request.user.id)
    history['send'] = get_history_dicts(sender=profile)
    history['received'] = get_history_dicts(recipient=profile)
    return _respond(
            content=format.resp_encode(history),
            mimetype=format.resp_mimetype
        )

@_apicall()
def profile(format, request, username):
    profile = get_object_or_404(DataloveProfile,user__username=username)
    selection = ['username','received_love','websites']
    if request.user.is_authenticated() and request.user == profile.user:
        selection += ['available_love']
    return _respond(
            content=format.resp_encode(profile.get_profile_dict(selection)),
            mimetype=format.resp_mimetype
        )
