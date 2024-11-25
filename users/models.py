from django.db import models
from django.contrib.auth.models import User


class ExtendedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    anonymous = models.BooleanField(default=False)
    avatar = models.CharField(max_length=1000000)
