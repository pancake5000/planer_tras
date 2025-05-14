from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from planer.models import BackgroundImage, Route, Point

class WebRoutesPointsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.bg = BackgroundImage.objects.create(name='bg', image='test.jpg')

    def login(self):
        self.client.login(username='user', password='pass')

    def test_create_empty_route(self):
        self.login()
        resp = self.client.post(reverse('create_route'), {'name': 'MyRoute', 'background': self.bg.id})
        self.assertEqual(resp.status_code, 302)
        route = Route.objects.get(name='MyRoute', user=self.user)
        self.assertEqual(route.background, self.bg)
        self.assertEqual(route.points.count(), 0)

    def test_add_point_to_route(self):
        self.login()
        route = Route.objects.create(user=self.user, background=self.bg, name='RouteWithPoints')
        resp = self.client.post(reverse('edit_and_view_route', args=[route.id]), {
            'x': 10, 'y': 20, 'add_point': 'Add Point'
        })
        self.assertEqual(resp.status_code, 302)
        route.refresh_from_db()
        self.assertEqual(route.points.count(), 1)
        point = route.points.first()
        self.assertEqual(point.x, 10)
        self.assertEqual(point.y, 20)
        # Check if point is visible in the view
        resp = self.client.get(reverse('edit_and_view_route', args=[route.id]))
        self.assertContains(resp, "Point (10.0, 20.0)")

    def test_delete_point_from_route(self):
        self.login()
        route = Route.objects.create(user=self.user, background=self.bg, name='RouteWithPoints')
        point = Point.objects.create(route=route, x=5, y=15)
        # Delete the point
        resp = self.client.post(reverse('edit_and_view_route', args=[route.id]), {
            'point_id': point.id, 'delete_point': 'Delete'
        })
        self.assertEqual(resp.status_code, 302)
        route.refresh_from_db()
        self.assertEqual(route.points.count(), 0)
        # Check if point is not visible in the view
        resp = self.client.get(reverse('edit_and_view_route', args=[route.id]))
        self.assertNotContains(resp, "Point (5.0, 15.0)")
