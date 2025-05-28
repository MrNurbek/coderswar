from django.db import models

# Create your models here.
from django.db import models
from apps.userapp.models import User
from apps.mainquest.models import Assignment

class Duel(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_duels')
    opponent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='joined_duels')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_duels')
    started_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Duel #{self.id} by {self.creator.email}"


class DuelAssignment(models.Model):
    duel = models.ForeignKey(Duel, on_delete=models.CASCADE, related_name='duel_assignments')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
