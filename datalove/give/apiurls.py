from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('datalove.give.views.api',
    url(r'^$', 'doc', name='api__doc'),
    url(r'^history$', 'history', name='api__history'),
    url(r'^users$', 'users', name='api__users'), 
    url(r'^users/(?P<username>[^?$/\\#%\s]+)$', 'profile', name='api__profile'),
    url(
        r'^users/(?P<username>[^?$/\\#%\s]+)/give_datalove$', 
        'give_datalove', 
        name='api__give_datalove'
    ),
    url(r'^(?P<format>[a-z]+)/users$', 'users'), 
    url(r'^(?P<format>[a-z]+)/history$', 'history'),
    url(r'^(?P<format>[a-z]+)/users/(?P<username>[^?$/\\#%\s]+)$', 'profile'),
    url(
        r'^(?P<format>[a-z]+)/users/(?P<username>[^?$/\\#%\s]+)/give_datalove$', 
        'give_datalove'
    ),
)
