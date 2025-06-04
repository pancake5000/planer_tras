import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GameBoard, UserPath
from .views import subscribers

@receiver(post_save, sender=GameBoard)
def gameboard_created(sender, instance, created, **kwargs):
    if created:
        data = {
            "board_id": instance.id,
            "board_name": instance.name,
            "creator_username": instance.user.username,
        }
        msg = f"event: newBoard\ndata: {json.dumps(data)}\n\n"
        # Wyślij do wszystkich subskrybentów
        for queue in list(subscribers):
            queue.append(msg)

@receiver(post_save, sender=UserPath)
def userpath_created(sender, instance, created, **kwargs):
    if created:
        data = {
            "path_id": instance.id,
            "board_id": instance.board.id,
            "board_name": instance.board.name,
            "user_username": instance.user.username,
            "path_name": instance.name,
        }
        msg = f"event: newPath\ndata: {json.dumps(data)}\n\n"
        for queue in list(subscribers):
            queue.append(msg)

# The userpath_created function is not called directly in your code.
# It is automatically called by Django's signals framework whenever a UserPath object is saved.
# This happens because of the @receiver(post_save, sender=UserPath) decorator above the function.
# When you create or save a UserPath instance (e.g., UserPath.objects.create(...) or user_path.save()),
# Django emits the post_save signal, which triggers userpath_created.
