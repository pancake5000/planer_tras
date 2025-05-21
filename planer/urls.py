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
    path('logout/', views.logout_view, name='logout'),    
    path('login/', views.login_view, name='login'),    
    path('register/', views.register, name='register'),
    path('board/create/', views.create_or_edit_board, name='create_board'),
    path('board/<int:board_id>/edit/', views.create_or_edit_board, name='edit_board'),
    path('board/<int:board_id>/delete/', views.delete_board, name='delete_board'),
    path('board/<int:board_id>/draw/', views.draw_path, name='draw_path'),
    path('board/<int:board_id>/create_route/', views.create_user_route_on_board, name='create_route_on_board'),
]