from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', views.route_list, name='route_list'),
    path('create/', views.create_route, name='create_route'),
    path('route/<int:route_id>/', views.edit_and_view_route, name='edit_and_view_route'),   
    path('api/', include('planer.api_urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),    
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),    
    path('login/', views.login_view, name='login'),    
    path('register/', views.register, name='register'),
]