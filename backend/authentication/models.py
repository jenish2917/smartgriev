from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    language = models.CharField(max_length=10, default='en')
    is_officer = models.BooleanField(default=False)

    def __str__(self):
        return self.username
