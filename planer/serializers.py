from rest_framework import serializers
from .models import Route, Point, BackgroundImage

class BackgroundImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackgroundImage
        fields = ['id', 'name', 'image']

class PointSerializer(serializers.ModelSerializer):
    x = serializers.FloatField()
    y = serializers.FloatField()

    class Meta:
        model = Point
        fields = ['id', 'x', 'y']

class RouteSerializer(serializers.ModelSerializer):
    points = PointSerializer(many=True, read_only=True)
    background = BackgroundImageSerializer(read_only=True)
    background_id = serializers.PrimaryKeyRelatedField(
        queryset=BackgroundImage.objects.all(), source='background', write_only=True
    )

    class Meta:
        model = Route
        fields = ['id', 'name', 'background', 'background_id', 'points']
