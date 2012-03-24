from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from urllib import urlencode
from give.models import DataloveProfile
from give.forms import DataloveAuthenticationForm
import _common

## Helper functions
def _query_redirect(to, query = {}, *args, **kwargs):
    response = redirect(to, *args, **kwargs)
    if len(query) > 0:
        response['Location'] += "?%s" % urlencode(query)
    return response

## Views
@csrf_protect
def index(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return _common.render_to_response2(
                    request,
                    'give/userpage.html',
                ) 
        else:
            context = {'next': request.GET.get('next', None)}
            return _common.render_to_response2(
                    request,
                    'give/welcome.html',
                    context
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
    context = _common.get_history_context(request)
    return _common.render_to_response2(request,'give/history.html',context)

@login_required
@csrf_protect
def manage_account(request):
    context = _common.get_manage_account_context(request)
    if request.method == 'POST':
        form_valid = False
        if "user" in request.POST:
            context, form_valid = _common.check_user_form(request, context) 
        elif "password" in request.POST:
            context, form_valid = _common.check_password_form(request, context) 
        elif "profile" in request.POST:
            context, form_valid = _common.check_profile_form(request, context) 
        if form_valid:
            return redirect(manage_account)
    return _common.render_to_response2(
            request,
            'give/manage_account.html',
            context
        )

@login_required
@csrf_protect
def manage_account_delete_website(request,id):
    _common.manage_account_delete_website(request,id)
    return redirect(manage_account)


@csrf_protect
def users(request):
    context = _common.get_users_context(request)
    return _common.render_to_response2(request,'give/users.html',context)

@csrf_protect
def register(request):
    context = _common.get_register_context(request)
    if request.method == 'POST':
        context, form_valid = _common.check_register_form(request,context)
        if form_valid:
            return redirect(index)
    return _common.render_to_response2(request,'give/register.html',context)    

@login_required
def unregister(request):
    request.user.delete()
    return redirect(index)

@login_required
def unregister_confirm(request):
    return _common.render_to_response2(request,'give/unregister_confirm.html')

@csrf_protect
def profile(request, username):
    context = _common.get_profile_context(request,username)
    return _common.render_to_response2(request,'give/profile.html',context)

@login_required
def give_datalove(request, username, from_users=False):
    query = _common.give_datalove(request,username) 
    if from_users:
        return _query_redirect(users, query)
    else:
        return _query_redirect(profile, query, username)

def widget(request):
    context = {'error': request.GET['error']} if 'error' in request.GET else {}
    if 'random' in request.GET and 'user' not in request.GET:
        context['profile'] = DataloveProfile.get_random_profile()
    elif 'user' in request.GET and 'random' not in request.GET:
        try:
            context['profile'] = DataloveProfile.objects.get(
                    user__username=request.GET['user']
                )
        except DataloveProfile.DoesNotExist:
            context['error'] = "User '%s' does not exist" % request.GET['user']
    else:
        return HttpResponseBadRequest(
                "GET request must have eather query parameter 'user' or "
                "'random'."
            )
    return _common.render_to_response2(request, 'give/widget.html', context)

@csrf_protect
def widget_doc(request):
    context = _common.get_widget_doc_context(request)
    return _common.render_to_response2(request, 'give/widget_doc.html', context)

def widget_give_datalove(request, username):
    if not request.user.is_authenticated():
        return redirect(index)
    query = _common.give_datalove(request, username, query={'user': username})
    return _query_redirect(widget, query)

@csrf_protect
def api_doc(request):
    pass
