from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import get_object_or_404
from give.models import *

import simplejson as json

format = 'json'
mimetype = 'application/json'

def profile(request, user_id):
    profile = get_object_or_404(DataloveProfile,pk=user_id)
    selection = ['username','received_love','websites']
    if request.user.is_authenticated() and request.user == profile.user:
        selection += ['available_love']
    return HttpResponse(
                json.dumps(
                        profile.get_profile_dict(selection)
                    ),
                content_type = mimetype,
                mimetype = mimetype
        )
