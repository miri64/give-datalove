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
    url('^user/(?P<username>[^?$/\\#%\s]+)/$','profile',name='profile'),
    url('^api/',include('datalove.give.apiurls')),
)
