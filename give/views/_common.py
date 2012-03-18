import re

from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from give.models import *
from give.forms import *

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
    if not request.user.is_authenticated():
        raise UserException("You are not logged in.")
    if re.match(r"[0-9]+",id):
        recipient = get_object_or_404(LovableObject, id=id)
    elif re.match(r"[^?$/\\#%\s]+",id):
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

def get_more_information(request, vars={}):
    if request.user.is_authenticated():
        vars.update({'user': request.user})
    if 'error' in request.GET:
        vars.update({'error': request.GET['error']})
    return vars

def check_form(form):
    if form.is_valid():
        form.save()
        return True
    return False

def get_history_context(request):
    profile = request.user.get_profile()
    context = {}
    context['received'] = profile.receive_history.all()[:30]
    context['sent'] = profile.send_history.all()[:30]
    return context 

def get_manage_account_context(request):
    context = {}
    context['user_form'] = DataloveUserChangeForm(
            instance=request.user,
            prefix="user"
        )
    context['password_form'] = PasswordChangeForm(
            request.user,
            prefix="password"
        )
    context['profile_form'] = UserWebsiteFormSet(
            request.user,
            prefix="profile"
        )
    return context

def check_user_form(request, context):
    context['user_form'] = DataloveUserChangeForm(
            request.POST,
            instance=request.user,
            prefix="user"
        )
    return context, check_form(context['user_form'])

def check_password_form(request, context):
    context['password_form'] = PasswordChangeForm(
            request.user,
            request.POST,
            prefix="user"
        )
    return context, check_form(context['password_form'])

def check_profile_form(request, context):
    context['profile_form'] = UserWebsiteFormSet(
            request.user,
            request.POST,
            prefix="profile"
        )
    return context, check_form(context['profile_form'])

def manage_account_delete_website(request,id):
    website = get_object_or_404(UserWebsite, pk=id)
    if website.user == request.user.get_profile():
        website.delete()
        return website
    return None

def get_register_context(request):
    context = {}
    context['form'] = DataloveUserCreationForm()
    return context

def check_register_form(request, context):
    context['form'] = DataloveUserCreationForm(request.POST)
    return context, check_form(context['form'])

def get_users_context(request):
    profiles = DataloveProfile.objects.order_by('?')
    context = get_more_information(request, {'profiles': profiles})
    return context

def get_profile_context(request, username):
    profile = get_object_or_404(DataloveProfile, user__username=username)
    context = get_more_information(request, {'profile': profile})
    return context

def get_widget_doc_context(request):
    context = {}
    if request.user.is_authenticated():
        context['profile'] = request.user.get_profile()
    return context
    
