from django.contrib.auth.forms import AuthenticationForm
from give.models import DataloveProfile

def total_loverz(request):
    return {'total_loverz': DataloveProfile.get_total_loverz()}

