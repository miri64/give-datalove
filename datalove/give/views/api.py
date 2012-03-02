from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, get_list_or_404
from give.models import *

import simplejson as json

import _common as common

API_LOGIN_URL=settings.LOGIN_URL

_resp_encode = json.dumps
_resp_mimetype = 'application/json'
_req_decode = json.loads

def _set_format(format):
    if format not in ('json'):
        raise Http404
    pass

def respond(
        ResponseObjectType=HttpResponse, 
        content=None, 
        mimetype=None,
        content_type=settings.DEFAULT_CONTENT_TYPE
    ):
    return ResponseObjectType(
            content=content,
            mimetype=mimetype,
            content_type=content_type
        )

@login_required(login_url=API_LOGIN_URL)
def get_history(request, format='json'):
    _set_format(format)
    history = {}
    profile = get_object_or_404(DataloveProfile, pk=request.user.id)
    history['send'] = common.get_history(sender=profile)
    history['received'] = common.get_history(recipient=profile)
    return respond(
            content=_resp_encode(history)
        )

def profile(request, user_id, format='json'):
    _set_format(format)
    profile = get_object_or_404(DataloveProfile,pk=user_id)
    selection = ['username','received_love','websites']
    if request.user.is_authenticated() and request.user == profile.user:
        selection += ['available_love']
    return respond(
                content=_resp_encode(
                        profile.get_profile_dict(selection)
                    )
        )
