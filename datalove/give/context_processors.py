from django.core.urlresolvers import reverse
from give.forms import DataloveAuthenticationForm
from give.models import DataloveProfile

def total_loverz(request):
    return {'total_loverz': DataloveProfile.get_total_loverz()}

def login_information(request):
    logged_in = request.user.is_authenticated()
    result = {'logged_in': logged_in}
    login_form_needed = reverse('login') != request.path and \
           reverse('register') != request.path
    print reverse('register'), request.path
    result['login_form_needed'] = login_form_needed
    if not logged_in and login_form_needed:
        if request.method == 'POST' and 'login' in request.POST:
            result.update({'form': DataloveAuthenticationForm(request.POST)})
        else:
            result.update({'form': DataloveAuthenticationForm()})
    return result

def path(request):
    return {'path': request.path}
