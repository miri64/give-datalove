from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('give.views.ajax',
    url('^login/?', 'login', name='ajax__login'),
)
