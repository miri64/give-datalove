from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout, password_reset, \
        password_reset_done, password_reset_confirm, password_reset_complete
from give.forms import DataloveAuthenticationForm

urlpatterns = patterns('give.views',
    url(r'^/?$','index',name='index'),
    url(r'^logout/?$',logout,{'next_page': '/'},name='logout'),
    url(r'^manage_account/?$','manage_account',name='manage_account'),
    url(
            r'^manage_account/delete_website/(?P<id>[0-9]+)/?$',
            'manage_account_delete_website',
            name='manage_account_delete_website'
        ),
    url(
            r'^reset_password/?$',
            password_reset,
            {
                'template_name': 'give/reset_password.html',
                'email_template_name': 'give/reset_password_email.html',
                'from_email': 'password-reset@give.datalove.me'
            },
            name='password_reset'
        ),
    url(
            '^reset_password/done/?$',
            password_reset_done,
            {'template_name': 'give/reset_password_done.html'}
        ),
    url(
            r'^reset_password/confirm/(?P<uidb36>[0-9]+)/(?P<token>[0-9a-z]+-[0-9a-f]+)/?$',
            password_reset_confirm,
            {'template_name': 'give/reset_password_confirm.html'},
            name='password_reset_confirm',
        ),
    url(
            '^reset_password/complete/?$',
            password_reset_complete,
            {'template_name': 'give/reset_password_complete.html'}
        ),
    url(r'^register/?$','register',name='register'),
    url(r'^unregister/?$','unregister',name='unregister'),
    url(r'^users/?$', 'users', name='users'),
    url(
            r'^users/give_(?P<username>[^?$/\\#%\s]+)_datalove/?$',
            'give_datalove',
            {'from_users': True},
            name='give_user_datalove'
        ),
    url(r'^users/(?P<username>[^?$/\\#%\s]+)/?$','profile',name='profile'),
    url(
            r'^users/(?P<username>[^?$/\\#%\s]+)/give_datalove/?$',
            'give_datalove',
            name='give_datalove'
        ),
    url(
            r'^users/(?P<username>[^?$/\\#%\s]+)/history/?$',
            'history',
            name='history'
        ),
    url(r'^widget/?$','widget',name='widget'),
    url(r'^widget/doc/?$','widget_doc',name='widget_doc'),
    url(
            r'^widget/give_(?P<username>[^?$/\\#%\s]+)_datalove/?$',
            'widget_give_datalove',
            name='widget_give_datalove'
        ),
    url(r'^api/?$','api_doc',name='api__doc'),
    url(r'^ajax/', include('give.ajaxurls'))
)
