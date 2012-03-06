from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('datalove.give.views.api',
    url('^$', 'api_doc'),
    url('^history$', 'get_history', name='api__get_history'),
    url('^(?P<format>(json|xml))/history$', 'get_history'),
    url('^users/(?P<username>[^?$/\\#%\s]+)$', 'profile', name='api__profile'),
    url('^(?P<format>[a-z]+)/users/(?P<username>[^?$/\\#%\s]+)$', 'profile'),
)
