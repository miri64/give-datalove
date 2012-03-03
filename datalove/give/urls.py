from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login,logout

urlpatterns = patterns('datalove.give.views.html',
    url('^$','index'),
    url(    
            '^login$',
            login,
            {   
                'template_name': 'give/welcome.html'
            },
            name='login'
        ),
    url('^logout$',logout,{'next_page': '/'}),
    url('^manage_account$','manage_account',name='manage_account'),
    url('^register$','register'),
    url('^users$', 'users', name='users'),
    url(
            '^users/give_(?P<username>[^?$/\\#%\s]+)_datalove$',
            'give_datalove',
            {'from_users': True},
        ),
    url('^users/(?P<username>[^?$/\\#%\s]+)$','profile',name='profile'),
    url('^users/(?P<username>[^?$/\\#%\s]+)/give_datalove$','give_datalove'),
    url('^api/',include('datalove.give.apiurls')),
)
