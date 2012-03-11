from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from give.models import DataloveProfile, NotEnoughDataloveException, DataNarcismException, LovableObject

import re

def render_to_response2(request, *args, **kwargs):
    if 'context_instance' in kwargs:
        raise AttributeError(
                "'context_instance' not allowed for render_to_response2"
            )
    return render_to_response(
            *args, 
            context_instance=RequestContext(request),
            **kwargs
        )

def give_datalove(request, id, love=1, query={}):
    if re.match(r"[0-9]+",id):
        recipient = get_object_or_404(LovableObject, id=id)
    elif re.match(r"[^?$/\\#%\s]+"):
        recipient = get_object_or_404(DataloveProfile, user__username=id)
    else:
        recipient = id
    datalove = 1
    if love in request.GET:
        datalove = int(request.GET['love'])
    try:
        request.user.get_profile().send_datalove(recipient,datalove) 
    except DataNarcismException, e:
        query['error'] = "Don't be narcistic. :("
    except NotEnoughDataloveException:
        query['error'] = "You've got not enough datalove. :("
    return query

