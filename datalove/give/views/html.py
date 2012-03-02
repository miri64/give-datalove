from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from give.models import *
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def index(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            try:
                profile = request.user.get_profile()
            except DataloveProfile.DoesNotExist:
                # if there is no datalove profile make it
                profile = DataloveProfile(user=request.user)
                profile.save()
            return render_to_response2(
                    request,
                    'give/userpage.html',
                    {'profile': profile}
                ) 
        else:
            form = AuthenticationForm()
            return render_to_response2(
                    request,
                    'give/welcome.html',
                    {'form': form}
                )
