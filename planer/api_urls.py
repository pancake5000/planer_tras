from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import RouteViewSet

router = DefaultRouter()
router.register(r'trasy', RouteViewSet, basename='route')

urlpatterns = [
    path('', include(router.urls)),
]
