from django.core.urlresolvers import reverse, NoReverseMatch
from give.forms import DataloveAuthenticationForm
from give.models import DataloveProfile

from urllib import urlencode

def _path_is_in(request_path, view_list):
    for view in view_list:
        try:
            if reverse(view) == request_path || \
                    reverse('ajax__'+view) == request_path:
                return True
        except NoReverseMatch:
            if view in request_path:
                return True
    return False

def total_loverz(request):
    return {'total_loverz': DataloveProfile.get_total_loverz()}

def menu(request, result = {}):
    menu = []
    if request.user.is_authenticated():
        menu += [
                {'url': reverse('logout')+'?'+urlencode(
                        {'next': request.path.replace('/ajax','')}
                    ), 'name': 'Logout'},
                {'url': reverse('manage_account'), 'name': 'Manage account'},
                {'url': reverse(
                        'history', 
                        kwargs={'username': request.user.username}
                    ), 'name': 'History'},
            ]
    menu += [
            {'url': reverse('widget_doc'), 'name': 'Widget for website'},
            {
                    'url': 'http://datalove.me/give/about.html', 
                    'name': 'About give.datalove.me'
                },
            {'url': reverse('users'), 'name': 'Loverz'},
            {'url': 'http://datalove.me/give/faq.html', 'name': 'FAQ'},
            {'url': reverse('api__doc'), 'name': 'API Documentation'},
        ]
    return {'menu': menu}

def login_information(request, result = {}):
    logged_in = request.user.is_authenticated()
    result['logged_in'] = logged_in
    login_form_needed = not logged_in and not _path_is_in(
            request.path, 
            ['register','password_reset_confirm','reset_password']
        )
    result['login_form_needed'] = login_form_needed
    if not logged_in and login_form_needed:
        if request.method == 'POST' and 'login' in request.POST:
            result['form'] = DataloveAuthenticationForm(request.POST)
        else:
            result['form'] = DataloveAuthenticationForm()
    if logged_in:
        result['userprofile'] = request.user.get_profile()
    return result

def path(request):
    return {'path': request.path}
