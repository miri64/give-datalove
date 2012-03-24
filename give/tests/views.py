"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, NoReverseMatch, resolve
from django.utils import unittest

import random
from urlparse import urlparse,parse_qs
try:
    import lxml.html
    from lxml.etree import XMLSyntaxError
    lxml_html_installed = True
except ImportError:
    lxml_html_installed = False

import give.views, give.models

from models import create_user,randstr

class TestURLs(TestCase):
    class URLTester(object):
        def __init__(self, testcase):
            self.tested_urls = {
                    'get': [],
                    'post': []
                }
            views_attr = give.views.__dict__.keys()
            self.views_to_see = []
            for attr_str in views_attr:
                attr = give.views.__getattribute__(attr_str)
                if type(attr).__name__ == 'function' and \
                        attr.__module__ == 'give.views' and \
                        not attr_str.startswith('_'):
                    self.views_to_see.append(attr_str)
            self.client = Client()
            self.username = randstr(30,True)
            self.create_user()
            self.testcase = testcase
        
        def __del__(self):
            self.user.delete()
        
        def create_user(self):
            self.user_password = randstr(30,True)
            self.user = create_user(
                    username=self.username,
                    password=self.user_password
                )
            give.models.UserWebsite.objects.create(
                    user=self.user.get_profile(), 
                    url='http://example.com'
                )
            

        def test_site(self, url, login=False, method="get", out_prefix=""):
            if len(User.objects.filter(username=self.username)) == 0:
                self.create_user()
            if login:
                self.client.login(username=self.user.username,password=self.user_password)
            if method.lower() == "get":
                response = self.client.get(url, follow=True)
            elif method.lower() == "post":
                response = self.client.post(url, follow=True)
            else:
                raise NotImplemented()
            self.testcase.assertNotEqual(0, len(response.content), "Content of %s %s is empty" % (method.upper(), url))
            dom = lxml.html.fromstring(response.content)
            self.testcase.assertEqual(200, response.status_code, 'Status-Code of %s %s is not 200, but %d.' % (method.upper(), url, response.status_code))
            url_path = urlparse(url).path
            view_func = resolve(url_path).func
            if view_func.__name__ in self.views_to_see: 
                self.views_to_see.remove(view_func.__name__)
            self.tested_urls[method].append(url)
            for link in dom.iterlinks():
                if link[0].tag.lower() == 'form':
                    next_method = link[0].get("method").lower()
                else:
                    next_method = "get"
                link = list(link)
                if link[2] not in self.tested_urls[next_method] and \
                        link[2].startswith('/') and \
                        not link[2].startswith('/static'):
                    self.test_site(link[2],login,next_method,out_prefix+" ")
            if login:
                self.client.logout()

    def setUp(self):
        self.url_tester = TestURLs.URLTester(self)
        for _ in range(random.randint(1,20)):
            create_user()
    
    def tearDown(self):
        for user in User.objects.all():
            user.delete()
    
    @unittest.skipUnless(lxml_html_installed, "lxml.html not found => Skip")
    def test_urls(self):
        self.url_tester.test_site(reverse('index'))
        for key in self.url_tester.tested_urls:
            self.url_tester.tested_urls[key] = []
        self.url_tester.test_site(reverse('index'), login=True)
        self.assertEqual(0,len(self.url_tester.views_to_see))

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.username, self.user = create_user()

    def test_index_get_without_login(self):
        response = self.client.get(reverse(give.views.index))
        self.assertEqual(200,response.status_code)
        self.assertIn('next',  response.context)
        self.assertIn('form',  response.context)
        self.assertTemplateUsed(response,'give/welcome.html')

    def test_index_get_login(self):
        self.assertTrue(
                self.client.login(
                        username=self.username, 
                        password=self.username
                    )
            )
        response = self.client.get(reverse(views.index))
        self.assertEqual(200,response.status_code)
        if 'next' in response.context:
            self.assertIsNone(response.context['next'])
        self.assertTemplateUsed(response,'give/userpage.html')
    
    def test_index_post_no_data(self):
        response = self.client.post(reverse(views.index))
        self.assertEqual(200,response.status_code)
        self.assertTemplateUsed(response,'give/welcome.html')
        self.assertIn('next',  response.context)
        self.assertIn('form',  response.context)
        form = response.context['form']
        self.assertContains(response,'This field is required.')

    def tearDown(self):
        self.user.delete()
