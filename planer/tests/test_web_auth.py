from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from planer.models import BackgroundImage

class WebAuthTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.bg = BackgroundImage.objects.create(name='bg', image='test.jpg')

    def test_route_list_requires_login(self):
        resp = self.client.get(reverse('route_list'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_create_route_requires_login(self):
        resp = self.client.get(reverse('create_route'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_edit_and_view_route_requires_login(self):
        self.client.login(username='user', password='pass')
        self.client.post(reverse('create_route'), {'name': 'Test', 'background': self.bg.id})
        route_id = self.user.route_set.first().id
        self.client.logout()
        resp = self.client.get(reverse('edit_and_view_route', args=[route_id]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_logged_in_user_can_access_protected_views(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('route_list'))
        self.assertEqual(resp.status_code, 200)
