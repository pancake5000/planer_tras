from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from planer.models import Route, BackgroundImage

class ApiInvalidInputTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.bg = BackgroundImage.objects.create(name='bg', image='test.jpg')
        self.route = Route.objects.create(user=self.user, background=self.bg, name='Route1')

    def get_token(self, username, password):
        response = self.client.post('/planer/api/token/', {'username': username, 'password': password}, format='json')
        return response.data['access']

    def test_add_point_missing_fields(self):
        token = self.get_token('user', 'pass')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.post(f'/planer/api/trasy/{self.route.id}/points/', {'x': 10}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('y', resp.data)

    def test_add_point_invalid_type(self):
        token = self.get_token('user', 'pass')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.post(f'/planer/api/trasy/{self.route.id}/points/', {'x': 'not_a_number', 'y': 20}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('x', resp.data)

    def test_create_route_missing_fields(self):
        token = self.get_token('user', 'pass')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.post('/planer/api/trasy/', {'name': 'IncompleteRoute'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('background_id', resp.data)

    def test_create_route_invalid_type(self):
        token = self.get_token('user', 'pass')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.post('/planer/api/trasy/', {'name': 'Route', 'background_id': 'not_an_int'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('background_id', resp.data)

    def test_get_points_invalid_route(self):
        token = self.get_token('user', 'pass')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.get('/planer/api/trasy/99999/points/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
