from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
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
            form = AuthenticationForm()
            next = None
            if 'next' in request.GET:
                next = request.GET['next']
            return render_to_response2(
                    request,
                    'give/welcome.html',
                    {'form': form,'next': next}
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
