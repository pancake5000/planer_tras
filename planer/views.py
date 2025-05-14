from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm  # Add this import
from .models import BackgroundImage, Route, Point
from .forms import RouteForm, PointForm, UserRegistrationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.views import LogoutView

@login_required
def route_list(request):
    routes = Route.objects.filter(user=request.user)  # Filter by logged-in user
    return render(request, 'planer/route_list.html', {'routes': routes})

@login_required
def create_route(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.user = request.user  # Automatically assign the logged-in user
            route.save()
            return redirect('route_list')
    else:
        form = RouteForm()
    return render(request, 'planer/create_route.html', {'form': form})

@login_required
def edit_and_view_route(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    points = route.points.order_by('id')  # Ensure points are ordered

    if request.method == 'POST':
        if 'add_point' in request.POST:  # Fixed the unterminated string literal
            form = PointForm(request.POST)
            if form.is_valid():
                point = form.save(commit=False)
                point.route = route
                point.save()
                return redirect('edit_and_view_route', route_id=route.id)
        elif 'delete_point' in request.POST:  # Fixed the unterminated string literal
            point_id = request.POST.get('point_id')
            Point.objects.filter(id=point_id, route=route).delete()
            return redirect('edit_and_view_route', route_id=route.id)
    else:
        form = PointForm()

    return render(request, 'planer/edit_and_view_route.html', {'route': route, 'points': points, 'form': form})

def register(request):
    if request.user.is_authenticated:  # Redirect authenticated users
        return redirect('route_list')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('route_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'planer/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:  # Redirect authenticated users
        return redirect('route_list')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('route_list')
    else:
        form = AuthenticationForm()
    return render(request, 'planer/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

class CustomLogoutView(LogoutView):
    next_page = 'login'  # Redirect to the login page after logout