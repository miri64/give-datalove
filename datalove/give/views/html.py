from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import login
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from urllib import urlencode
from give.forms import *
from give.models import *
import _common as common

## Helper functions
def get_more_information(request, vars={}):
    if request.user.is_authenticated():
        vars.update({'user': request.user})
    if 'error' in request.GET:
        vars.update({'error': request.GET['error']})
    return vars

def query_redirect(to, query = {}, *args, **kwargs):
    response = redirect(to, *args, **kwargs)
    if len(query) > 0:
        response['Location'] += "?%s" % urlencode(query)
    return response

## Views
@csrf_exempt
def index(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return common.render_to_response2(
                    request,
                    'give/userpage.html',
                ) 
        else:
            next = None
            if 'next' in request.GET:
                next = request.GET['next']
            return common.render_to_response2(
                    request,
                    'give/welcome.html',
                    {'next': next}
                )
    else:
        return login(
                request, 
                template_name='give/welcome.html',
                authentication_form=DataloveAuthenticationForm
            )


@login_required
def history(request,username):
    if request.user.username != username:
        return redirect('profile', username)
    profile = request.user.get_profile()
    vars = {}
    vars['received'] = profile.receive_history.all()[:30]
    vars['sent'] = profile.send_history.all()[:30]
    return common.render_to_response2(request,'give/history.html',vars)


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
                return redirect(manage_account)
        if "password" in request.POST:
            password_form = PasswordChangeForm(
                    request.user,
                    request.POST,
                    prefix="password"
                )
            if password_form.is_valid():
                password_form.save()
                return redirect(manage_account)
        if "profile" in request.POST:
            profile_form = UserWebsiteFormSet(
                    request.user,
                    request.POST,
                    prefix="profile"
                )
            if profile_form.is_valid():
                profile_form.save()
                return redirect(manage_account)
    return common.render_to_response2(
            request,
            'give/manage_account.html',
            {
                'user_form': user_form,
                'password_form': password_form,
                'profile_form': profile_form
            }
        )

def users(request):
    profiles = DataloveProfile.objects.order_by('?')
    vars = get_more_information(request, {'profiles': profiles})
    return common.render_to_response2(request,'give/users.html',vars)

@csrf_exempt
def register(request):
    form = DataloveUserCreationForm()
    if request.method == 'POST':
        form = DataloveUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(index)
    return common.render_to_response2(request,'give/register.html',{'form':form})    

@login_required
def unregister(request):
    request.user.delete()
    return redirect(index)

def profile(request, username):
    profile = get_object_or_404(DataloveProfile, user__username=username)
    vars = get_more_information(request, {'profile': profile})
    return common.render_to_response2(request,'give/profile.html',vars)

@login_required
def give_datalove(request, username, from_users=False):
    query = common.give_datalove(request,username) 
    if from_users:
        return query_redirect(users, query)
    else:
        return query_redirect(profile, query, username)

def widget(request):
    vars = {'error': request.GET['error']} if 'error' in request.GET else {}
    if 'random' in request.GET:
        vars['profile'] = DataloveProfile.get_random_profile()
    elif 'user' in request.GET:
        try:
            vars['profile'] = DataloveProfile.objects.get(
                    user__username=request.GET['user']
                )
        except DataloveProfile.DoesNotExist:
            vars['error'] = "User '%s' does not exist" % request.GET['user']
    else:
        if request.user.is_authenticated():
            vars['profile'] = request.user.get_profile()
        return common.render_to_response2(request, 'give/widgetpage.html', vars)
    return common.render_to_response2(request, 'give/widget.html', vars)

def widget_give_datalove(request, username):
    query = common.give_datalove(request, username, query={'user': username})
    return query_redirect(widget, query)

def api_doc(request):
    pass
