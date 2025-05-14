from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from planer.models import Route, Point, BackgroundImage

class ApiPointsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.bg = BackgroundImage.objects.create(name='bg', image='test.jpg')
        self.route = Route.objects.create(user=self.user, background=self.bg, name='Route1')
        self.point = Point.objects.create(route=self.route, x=1, y=2)

    def get_token(self, username, password):
        response = self.client.post('/planer/api/token/', {'username': username, 'password': password}, format='json')
        return response.data['access']

    def test_add_point_to_route(self):
        token = self.get_token('user', 'pass')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        data = {"x": 10, "y": 20}
        resp = self.client.post(f'/planer/api/trasy/{self.route.id}/points/', data, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['x'], 10)
        self.assertEqual(resp.data['y'], 20)

    def test_list_points_for_route(self):
        token = self.get_token('user', 'pass')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.get(f'/planer/api/trasy/{self.route.id}/points/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(resp.data, list))
        self.assertGreaterEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['x'], self.point.x)
        self.assertEqual(resp.data[0]['y'], self.point.y)
