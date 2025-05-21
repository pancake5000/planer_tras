from django.db import models
from django.contrib.auth.models import User

class BackgroundImage(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='backgrounds/')

    def __str__(self):
        return self.name

class Route(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    background = models.ForeignKey(BackgroundImage, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Point(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='points')
    x = models.FloatField()
    y = models.FloatField()

    def __str__(self):
        return f"Point ({self.x}, {self.y})"

class Pair(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='pairs')
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()

    def __str__(self):
        return f"Pair (({self.x1}, {self.y1}), ({self.x2}, {self.y2}))"

class GameBoard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    cols = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Dot(models.Model):
    board = models.ForeignKey(GameBoard, on_delete=models.CASCADE, related_name='dots')
    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()
    color = models.CharField(max_length=7)  # hex color, e.g. #FF0000

    def __str__(self):
        return f"Dot ({self.row}, {self.col}) {self.color}"

class UserPath(models.Model):
    board = models.ForeignKey(GameBoard, on_delete=models.CASCADE, related_name='paths')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.JSONField()  # List of {"row": int, "col": int}
    name = models.CharField(max_length=100, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Remove unique_together so user can have many paths per board
        pass

    def __str__(self):
        return f"Path '{self.name}' for {self.user.username} on {self.board.name}"