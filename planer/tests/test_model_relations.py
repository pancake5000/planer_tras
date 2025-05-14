from django.contrib.auth.models import User
from django.test import TestCase
from planer.models import BackgroundImage, Route, Point

class ModelRelationsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.bg = BackgroundImage.objects.create(name='bg', image='test.jpg')
        self.route = Route.objects.create(user=self.user, background=self.bg, name='MyRoute')
        self.point = Point.objects.create(route=self.route, x=1.5, y=2.5)

    def test_route_user_relation(self):
        self.assertEqual(self.route.user, self.user)

    def test_route_background_relation(self):
        self.assertEqual(self.route.background, self.bg)

    def test_point_route_relation(self):
        self.assertEqual(self.point.route, self.route)

    def test_point_reverse_relation(self):
        self.assertIn(self.point, self.route.points.all())
