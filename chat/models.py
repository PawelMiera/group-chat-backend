from django.db import models
from django.contrib.auth.models import User
import uuid


class ChatGroup(models.Model):
    uuid = models.CharField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    avatar = models.CharField(max_length=1000000)
    members = models.ManyToManyField(User, through="Membership")

    def __str__(self):
        return f'{self.name}: {self.uuid}'


class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name="chat_messages", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    msg = models.CharField(max_length=5000, unique=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}: {self.msg}'

    class Meta:
        ordering = ['-created']


class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    admin = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)
