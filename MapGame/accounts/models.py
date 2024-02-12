from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Create your models here.


class User(AbstractUser):
    pass
    # add additional fields in here

    def __str__(self):
        return self.username
    


class UserToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    player_uuid = models.CharField(max_length=64, unique=True, null=True, blank=True)
