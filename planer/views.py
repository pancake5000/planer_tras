from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BackgroundImage, Route, Point
from .forms import RouteForm, PointForm

@login_required
def route_list(request):
    routes = Route.objects.filter(user=request.user)
    return render(request, 'planer/route_list.html', {'routes': routes})

@login_required
def create_route(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.user = request.user
            route.save()
            return redirect('route_list')
    else:
        form = RouteForm()
    return render(request, 'planer/create_route.html', {'form': form})

@login_required
def edit_route(request, route_id):
    route = get_object_or_404(Route, id=route_id, user=request.user)
    points = route.points.all()
    if request.method == 'POST':
        form = PointForm(request.POST)
        if form.is_valid():
            point = form.save(commit=False)
            point.route = route
            point.save()
            return redirect('edit_route', route_id=route.id)
    else:
        form = PointForm()
    return render(request, 'planer/edit_route.html', {'route': route, 'points': points, 'form': form})