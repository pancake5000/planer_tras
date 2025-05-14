from django import forms
from .models import Route, Point

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'background']

class PointForm(forms.ModelForm):
    class Meta:
        model = Point
        fields = ['x', 'y']