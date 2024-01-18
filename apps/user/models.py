from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    symbol = models.CharField(max_length=1, default="O")
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id}-{self.username}"
