"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from django.core.urlresolvers import reverse

import views
from models import create_user

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.username, self.user = create_user()

    def test_index_get_without_login(self):
        response = self.client.get(reverse(views.index))
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
