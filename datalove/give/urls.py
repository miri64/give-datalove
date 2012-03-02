from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login,logout

urlpatterns = patterns('datalove.give.views.html',
    url('^$','index'),
    url(    
            '^login$',
            login,
            {   
                'template_name': 'give/welcome.html',
                'redirect_field_name': '/'
            },
            name='login'
        ),
    url('^logout$',logout,{'next_page': '/'}),
    url('^api/',include('datalove.give.apiurls')),
)
