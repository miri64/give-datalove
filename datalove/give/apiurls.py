from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('datalove.give.views.api',
    url(r'^$', 'api_doc'),
    url(r'^history$', 'get_history', name='api__get_history'),
    url(r'^(?P<format>(json|xml))/history$', 'get_history'),
    url(r'^users/(?P<username>[^?$/\\#%\s]+)$', 'profile', name='api__profile'),
    url(r'^(?P<format>[a-z]+)/users/(?P<username>[^?$/\\#%\s]+)$', 'profile'),
    url(
        r'^users/(?P<username>[^?$/\\#%\s]+)/give_datalove$', 
        'give_datalove', 
        name='api__give_datalove'
    ),
    url(
        r'^(?P<format>[a-z]+)/users/(?P<username>[^?$/\\#%\s]+)/give_datalove$', 
        'give_datalove'
    ),
)
