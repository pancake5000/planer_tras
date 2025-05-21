from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Route, Point, Pair, GameBoard, Dot

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['background', 'name']  # Exclude the 'user' field

class PointForm(forms.ModelForm):
    class Meta:
        model = Point
        fields = ['x', 'y']

class PairForm(forms.ModelForm):
    class Meta:
        model = Pair
        fields = ['x1', 'y1', 'x2', 'y2']

class GameBoardForm(forms.ModelForm):
    class Meta:
        model = GameBoard
        fields = ['name', 'rows', 'cols']

class DotForm(forms.ModelForm):
    class Meta:
        model = Dot
        fields = ['row', 'col', 'color']