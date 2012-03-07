from django.shortcuts import get_object_or_404, get_list_or_404, render_to_response
from django.template import RequestContext
from give.models import DataloveHistory, DataloveProfile

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

def get_history(**args):
    send_history = [m.__dict__ for m in get_list_or_404(
            DataloveHistory, 
            **args
        )]
    for h in send_history:
        del h['_state']
        del h['id']
        h['timestamp'] = str(h['timestamp'])
    return send_history 

def give_datalove(request, username, love=1, query={}):
    recipient = get_object_or_404(DataloveProfile, user__username=username)
    datalove = 1
    if love in request.GET:
        datalove = int(request.GET['love'])
    try:
        request.user.get_profile().send_datalove(recipient,datalove) 
    except IntegrityError, e:
        query['error'] = "Don't be narcistic. :("
    except NotEnoughDataloveException:
        query['error'] = "You've got not enough datalove. :("
    return query
