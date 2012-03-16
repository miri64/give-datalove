from django.http import HttpResponse
from djangopiston.piston import authentication

class OAuthAuthentication(authentication.OAuthAuthentication):
    def __init__(self, *args, **kwargs):
        super(OAuthAuthentication,self).__init__(*args, **kwargs)

    def challenge(self):
        response = HttpResponse()
        response.status_code = 401
        return response
