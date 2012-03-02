from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('datalove.give.views.api',
    url('^user/(?P<user_id>\d+)$', 'profile', name='api__profile'),
    url('^(?P<format>(json|xml))/user/(?P<user_id>\d+)$', 'profile'),
)
