from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from urllib import urlencode
from give.forms import *
from give.models import *

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
            profile = request.user.get_profile()
            return render_to_response2(
                    request,
                    'give/userpage.html',
                    {'profile': profile}
                ) 
        else:
            next = None
            if 'next' in request.GET:
                next = request.GET['next']
            return render_to_response2(
                    request,
                    'give/welcome.html',
                    {'next': next}
                )

@csrf_exempt
@login_required
def manage_account(request):
    user_form = DataloveUserChangeForm(instance=request.user,prefix="user")
    password_form = PasswordChangeForm(
            request.user,
            prefix="password"
        )
    profile_form = UserWebsiteFormSet(
            request.user,
            prefix="profile"
        )
    if request.method == 'POST':
        if "user" in request.POST:
            user_form = DataloveUserChangeForm(
                    request.POST,
                    instance=request.user,
                    prefix="user"
                )
            if user_form.is_valid():
                user_form.save()
                return redirect('manage_account')
        if "password" in request.POST:
            password_form = PasswordChangeForm(
                    request.user,
                    request.POST,
                    prefix="password"
                )
            if password_form.is_valid():
                password_form.save()
                return redirect('manage_account')
        if "profile" in request.POST:
            profile_form = UserWebsiteFormSet(
                    request.user,
                    request.POST,
                    prefix="profile"
                )
            if profile_form.is_valid():
                profile_form.save()
                return redirect('manage_account')
    return render_to_response2(
            request,
            'give/manage_account.html',
            {
                'profile': request.user.get_profile(),
                'user_form': user_form,
                'password_form': password_form,
                'profile_form': profile_form
            }
        )

def get_more_information(request, vars={}):
    if request.user.is_authenticated():
        vars.update({'user': request.user})
    if 'error' in request.GET:
        vars.update({'error': request.GET['error']})
    return vars

def users(request):
    profiles = DataloveProfile.objects.order_by('?')
    vars = get_more_information(request, {'profiles': profiles})
    return render_to_response2(request,'give/users.html',vars)

@csrf_exempt
def register(request):
    form = DataloveUserCreationForm()
    if request.method == 'POST':
        form = DataloveUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    return render_to_response2(request,'give/register.html',{'form':form})    

def profile(request, username):
    profile = get_object_or_404(DataloveProfile, user__username=username)
    vars = get_more_information(request, {'profile': profile})
    return render_to_response2(request,'give/profile.html',vars)

def query_redirect(to, query = {}, *args, **kwargs):
    response = redirect(to, *args, **kwargs)
    if len(query) > 0:
        response['Location'] += "?%s" % urlencode(query)
    return response

@login_required
def give_datalove(request, username, from_users=False):
    recipient = get_object_or_404(DataloveProfile, user__username=username)
    query = {}
    try:
        request.user.get_profile().send_datalove(recipient) 
    except IntegrityError, e:
        query['error'] = str(e)
    except NotEnoughDataloveException:
        query['error'] = "You do not have enough datalove :(."
    if from_users:
        return query_redirect('users', query)
    else:
        return query_redirect(recipient, query)
