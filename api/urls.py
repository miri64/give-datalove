from django.conf.urls.defaults import patterns, include, url
from djangopiston.piston.resource import Resource
from djangopiston.piston.authentication import oauth_request_token, oauth_user_auth, \
        oauth_access_token
from authentication import OAuthAuthentication
from handlers import *

auth = OAuthAuthentication(realm="give.datalove.me")

profile_handler = Resource(ProfileHandler, authentication=[auth])
history_handler = Resource(HistoryHandler, authentication=[auth])
give_datalove_handler = Resource(GiveDataloveHandler, authentication=[auth])

urlpatterns = patterns('',
    url(
        r'^users/?$', 
        profile_handler,
        {'emitter_format': 'json'},
        name='api__users'
    ),
    url(
        r'^users/(?P<username>[^?$/\\#%\s]+)/?$', 
        profile_handler,
        {'emitter_format': 'json'},
        name='api__profile'
    ),
    url(
        r'^users/(?P<username>[^?$/\\#%\s]+)/history/?$', 
        history_handler,
        {'emitter_format': 'json'},
        name='api__history'
    ),
    url(
        r'^give_datalove/(?P<id>[0-9]+)/?$', 
        give_datalove_handler,
        {'emitter_format': 'json'},
        name='api__give_datalove'
    ),
    url(
        r'^(?P<emitter_format>[a-z]+)/users/?$', 
        profile_handler,
    ),
    url(
        r'^(?P<emitter_format>[a-z]+)/users/(?P<username>[^?$/\\#%\s]+)/?$', 
        profile_handler,
    ),
    url(
        r'^(?P<emitter_format>[a-z]+)/users/(?P<username>[^?$/\\#%\s]+)/history/?$', 
        history_handler,
    ),
    url(
        r'^(?P<emitter_format>[a-z]+)/give_datalove/(?P<id>[0-9]+)/?$', 
        give_datalove_handler,
    ),
    url(
        r'^oauth/authorize/?$',
        oauth_user_auth,
        {'template_name': 'oauth/authorize.html'},
        name='api__oauth_authorize'
    ),
    url(
        r'^oauth/access_token/?$',
        oauth_access_token,
        name='api__oauth_access_token'
    ),
    url(
        r'^oauth/request_token/?$',
        oauth_request_token,
        name='api__oauth_request_token'
    ),
)
    
