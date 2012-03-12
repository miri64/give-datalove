from django.core.urlresolvers import reverse, NoReverseMatch
from give.forms import DataloveAuthenticationForm
from give.models import DataloveProfile

def path_is_in(request_path, view_list):
    for view in view_list:
        try:
            if reverse(view) == request_path:
                return True
        except NoReverseMatch:
            if view in request_path:
                return True
    return False

def total_loverz(request):
    return {'total_loverz': DataloveProfile.get_total_loverz()}

def login_information(request):
    logged_in = request.user.is_authenticated()
    result = {'logged_in': logged_in}
    login_form_needed = not path_is_in(
            request.path, 
            ['register','password_reset_confirm','reset_password']
        )
    result['login_form_needed'] = login_form_needed
    if not logged_in and login_form_needed:
        if request.method == 'POST' and 'login' in request.POST:
            result.update({'form': DataloveAuthenticationForm(request.POST)})
        else:
            result.update({'form': DataloveAuthenticationForm()})
    if logged_in:
        result.update({'userprofile': request.user.get_profile()})
    return result

def path(request):
    return {'path': request.path}
