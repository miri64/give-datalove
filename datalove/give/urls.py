from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login,logout

urlpatterns = patterns('datalove.give.views.html',
    url(r'^$','index'),
    url(    
            r'^login$',
            login,
            {'template_name': 'give/welcome.html'},
            name='login'
        ),
    url(r'^logout$',logout,{'next_page': '/'}),
    url(r'^manage_account$','manage_account',name='manage_account'),
    url(r'^register$','register'),
    url(r'^unregister$','unregister'),
    url(r'^users$', 'users', name='users'),
    url(
            r'^users/give_(?P<username>[^?$/\\#%\s]+)_datalove$',
            'give_datalove',
            {'from_users': True},
        ),
    url(r'^users/(?P<username>[^?$/\\#%\s]+)$','profile',name='profile'),
    url(r'^users/(?P<username>[^?$/\\#%\s]+)/give_datalove$','give_datalove'),
    url(r'^widget$','widget',name='widget'),
    url(
            r'^widget/give_(?P<username>[^?$/\\#%\s]+)_datalove$',
            'widget_give_datalove',
        ),
    url(r'^api/',include('datalove.give.apiurls')),
)
