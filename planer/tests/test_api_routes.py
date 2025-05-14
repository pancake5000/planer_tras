from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from planer.models import Route, BackgroundImage

class ApiRoutesTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.bg = BackgroundImage.objects.create(name='bg', image='test.jpg')
        self.route1 = Route.objects.create(user=self.user1, background=self.bg, name='Route1')
        self.route2 = Route.objects.create(user=self.user2, background=self.bg, name='Route2')

    def get_token(self, username, password):
        response = self.client.post('/planer/api/token/', {'username': username, 'password': password}, format='json')
        return response.data['access']

    def test_create_route(self):
        token = self.get_token('user1', 'pass1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        data = {
            "name": "NewRoute",
            "background_id": self.bg.id
        }
        resp = self.client.post('/planer/api/trasy/', data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['name'], "NewRoute")
        self.assertEqual(resp.data['background']['id'], self.bg.id)

    def test_list_routes_only_user(self):
        token = self.get_token('user2', 'pass2')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.get('/planer/api/trasy/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['name'], 'Route2')
        self.assertEqual(resp.data[0]['id'], self.route2.id)

    def test_get_route_detail(self):
        token = self.get_token('user1', 'pass1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.get(f'/planer/api/trasy/{self.route1.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], 'Route1')
        self.assertEqual(resp.data['background']['id'], self.bg.id)
        self.assertIn('points', resp.data)
