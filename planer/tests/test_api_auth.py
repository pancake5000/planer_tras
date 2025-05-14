from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from planer.models import Route, Point, BackgroundImage

class ApiAuthTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.bg = BackgroundImage.objects.create(name='bg', image='test.jpg')
        self.route1 = Route.objects.create(user=self.user1, background=self.bg, name='Route1')
        self.route2 = Route.objects.create(user=self.user2, background=self.bg, name='Route2')
        self.point1 = Point.objects.create(route=self.route1, x=1, y=2)
        self.point2 = Point.objects.create(route=self.route2, x=3, y=4)

    def get_token(self, username, password):
        response = self.client.post('/planer/api/token/', {'username': username, 'password': password}, format='json')
        return response.data['access']

    def test_auth_required(self):
        # Unauthenticated access should be denied
        resp = self.client.get('/planer/api/trasy/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_only_see_own_routes(self):
        token = self.get_token('user1', 'pass1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.get('/planer/api/trasy/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['name'], 'Route1')

    def test_user_cannot_access_others_route(self):
        token = self.get_token('user1', 'pass1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        # Try to get user2's route
        resp = self.client.get(f'/planer/api/trasy/{self.route2.id}/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_only_modify_own_routes(self):
        token = self.get_token('user1', 'pass1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        # Try to delete own route
        resp = self.client.delete(f'/planer/api/trasy/{self.route1.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # Try to delete other's route
        resp = self.client.delete(f'/planer/api/trasy/{self.route2.id}/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_only_see_own_points(self):
        token = self.get_token('user1', 'pass1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        resp = self.client.get(f'/planer/api/trasy/{self.route1.id}/points/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['x'], self.point1.x)
        # Try to access other's points
        resp = self.client.get(f'/planer/api/trasy/{self.route2.id}/points/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_only_add_points_to_own_route(self):
        token = self.get_token('user1', 'pass1')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        # Add point to own route
        resp = self.client.post(f'/planer/api/trasy/{self.route1.id}/points/', {'x': 10, 'y': 20}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Try to add point to other's route
        resp = self.client.post(f'/planer/api/trasy/{self.route2.id}/points/', {'x': 10, 'y': 20}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
