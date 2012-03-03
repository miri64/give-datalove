from django.contrib.auth.forms import AuthenticationForm
from give.models import DataloveProfile

def total_loverz(request):
    return {'total_loverz': DataloveProfile.get_total_loverz()}

def login_information(request):
    logged_in = request.user.is_authenticated()
    result = {'logged_in': logged_in}
    if not logged_in:
        result.update({'login_form': AuthenticationForm()})
    return result
