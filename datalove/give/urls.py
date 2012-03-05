from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout, password_reset, \
        password_reset_done, password_reset_confirm, password_reset_complete
from give.forms import DataloveAuthenticationForm

urlpatterns = patterns('datalove.give.views.html',
    url(r'^$','index'),
    url(r'^history$','history'),
    url(    
            r'^login$',
            login,
            {
                'template_name': 'give/welcome.html',
                'authentication_form': DataloveAuthenticationForm
            },
            name='login'
        ),
    url(r'^logout$',logout,{'next_page': '/'}),
    url(r'^manage_account$','manage_account',name='manage_account'),
    url(
            r'^reset_password$',
            password_reset,
            {
                'template_name': 'give/reset_password.html',
                'email_template_name': 'give/reset_password_email.html',
                'from_email': 'password-reset@give.datalove.me'
            },
            name='password_reset'
        ),
    url(
            '^reset_password/done$',
            password_reset_done,
            {'template_name': 'give/reset_password_done.html'}
        ),
    url(
            r'^reset_password/confirm/(?P<uidb36>[0-9]+)/(?P<token>[-0-9a-f]+)$',
            password_reset_confirm,
            {'template_name': 'give/reset_password_confirm.html'},
            name='password_reset_confirm',
        ),
    url(
            '^reset_password/complete$',
            password_reset_complete,
            {'template_name': 'give/reset_password_complete.html'}
        ),
    url(r'^register$','register',name='register'),
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
