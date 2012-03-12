from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import give.views._common as common

@login_required
def oauth_callback(request,token):
    return common.render_to_response2(
            request,
            'oauth/verifier.html',
            {'token': token}
        )
