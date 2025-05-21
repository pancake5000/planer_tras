from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm  # Add this import
from .models import BackgroundImage, Route, Point, Pair, GameBoard, Dot, UserPath
from .forms import RouteForm, PointForm, UserRegistrationForm, PairForm, GameBoardForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse

@login_required
def route_list(request):
    routes = Route.objects.filter(user=request.user)
    boards = GameBoard.objects.filter(user=request.user)
    user_paths = UserPath.objects.filter(user=request.user).select_related('board')
    other_boards = GameBoard.objects.exclude(user=request.user).select_related('user')
    return render(request, 'planer/route_list.html', {
        'routes': routes,
        'boards': boards,
        'user_paths': user_paths,
        'other_boards': other_boards,
    })

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
    points = route.points.order_by('id')
    pairs = route.pairs.order_by('id')
    grid_size = request.session.get(f'grid_size_{route_id}', 20)
    form = PointForm()
    pair_form = PairForm()

    if request.method == 'POST':
        if 'grid_size' in request.POST:
            try:
                grid_size = int(request.POST.get('grid_size', 20))
                if grid_size < 5: grid_size = 5
                if grid_size > 100: grid_size = 100
            except ValueError:
                grid_size = 20
            request.session[f'grid_size_{route_id}'] = grid_size
        elif 'add_pair' in request.POST:
            pair_form = PairForm(request.POST)
            if pair_form.is_valid():
                pair = pair_form.save(commit=False)
                pair.route = route
                pair.save()
                return redirect('edit_and_view_route', route_id=route.id)
        elif 'add_point' in request.POST or ('x' in request.POST and 'y' in request.POST):
            form = PointForm(request.POST)
            if form.is_valid():
                point = form.save(commit=False)
                point.route = route
                point.save()
                return redirect('edit_and_view_route', route_id=route.id)
        elif 'delete_point' in request.POST:
            point_id = request.POST.get('point_id')
            Point.objects.filter(id=point_id, route=route).delete()
            return redirect('edit_and_view_route', route_id=route.id)
        elif 'delete_pair' in request.POST:
            pair_id = request.POST.get('pair_id')
            Pair.objects.filter(id=pair_id, route=route).delete()
            return redirect('edit_and_view_route', route_id=route.id)

    return render(request, 'planer/edit_and_view_route.html', {
        'route': route,
        'points': points,
        'pairs': pairs,
        'form': form,
        'pair_form': pair_form,
        'grid_size': grid_size,
    })

@login_required
def create_or_edit_board(request, board_id=None):
    if board_id:
        board = get_object_or_404(GameBoard, id=board_id, user=request.user)
        dots = list(board.dots.values('row', 'col', 'color'))
        from collections import defaultdict
        color_map = defaultdict(list)
        for dot in dots:
            color_map[dot['color']].append(dot)
        pairs = [
            (color, color_map[color])
            for color in color_map
            if len(color_map[color]) == 2
        ]
    else:
        board = None
        dots = []
        pairs = []

    form = None  # Always define form

    if request.method == 'POST':
        # Handle pair deletion
        if 'delete_pair_color' in request.POST and board:
            color_to_delete = request.POST.get('delete_pair_color')
            board.dots.filter(color=color_to_delete).delete()
            # Refresh dots and pairs after deletion
            dots = list(board.dots.values('row', 'col', 'color'))
            from collections import defaultdict
            color_map = defaultdict(list)
            for dot in dots:
                color_map[dot['color']].append(dot)
            pairs = [
                (color, color_map[color])
                for color in color_map
                if len(color_map[color]) == 2
            ]
            form = GameBoardForm(instance=board)
        else:
            form = GameBoardForm(request.POST, instance=board)
            if form.is_valid():
                board = form.save(commit=False)
                board.user = request.user
                board.save()
                board.dots.all().delete()
                dots_json = request.POST.get('dots_json')
                if dots_json:
                    dots_data = json.loads(dots_json)
                    for dot in dots_data:
                        Dot.objects.create(board=board, row=dot['row'], col=dot['col'], color=dot['color'])
                return redirect('route_list')
    else:
        form = GameBoardForm(instance=board)

    return render(request, 'planer/edit_board.html', {
        'form': form,
        'board': board,
        'dots': json.dumps(dots),
        'pairs': pairs,
    })

@login_required
def delete_board(request, board_id):
    board = get_object_or_404(GameBoard, id=board_id, user=request.user)
    if request.method == 'POST':
        board.delete()
        return redirect('board_list')
    return render(request, 'planer/delete_board.html', {'board': board})

@login_required
def create_board(request):
    return redirect('create_or_edit_board')

@login_required
def draw_path(request, board_id):
    board = get_object_or_404(GameBoard, id=board_id)
    dots = list(board.dots.values('row', 'col', 'color'))

    path_id = request.GET.get('path_id')
    path = []
    path_name = ''
    user_path = None

    if path_id:
        user_path = get_object_or_404(UserPath, id=path_id, user=request.user, board=board)
        path = user_path.path
        path_name = user_path.name

    if request.method == 'POST':
        path_json = request.POST.get('path_json')
        path_name = request.POST.get('path_name', '').strip()
        if path_json and path_name:
            if user_path:
                user_path.path = json.loads(path_json)
                user_path.name = path_name
                user_path.save()
            else:
                UserPath.objects.create(
                    board=board,
                    user=request.user,
                    path=json.loads(path_json),
                    name=path_name
                )
            return redirect('route_list')

    return render(request, 'planer/draw_path.html', {
        'board': board,
        'dots': json.dumps(dots),
        'path': json.dumps(path),
        'path_name': path_name,
    })

@login_required
def create_user_route_on_board(request, board_id):
    board = get_object_or_404(GameBoard, id=board_id)
    dots = list(board.dots.values('row', 'col', 'color'))

    if request.method == 'POST':
        # Save a new route for this user on this board
        route_json = request.POST.get('route_json')
        route_name = request.POST.get('route_name', '').strip()
        if route_json and route_name:
            # Create a new Route instance (not UserPath)
            route = Route.objects.create(
                user=request.user,
                background=None,  # or set to a default BackgroundImage if required
                name=route_name
            )
            # Save points for the route
            route_points = json.loads(route_json)
            for pt in route_points:
                Point.objects.create(route=route, x=pt['col'], y=pt['row'])
            return redirect('route_list')
    else:
        route_name = ''

    return render(request, 'planer/create_route_on_board.html', {
        'board': board,
        'dots': json.dumps(dots),
        'route_name': route_name,
    })

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