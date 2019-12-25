from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField(max_length=15, unique=True)

    class Meta:
        db_table = 'users_tb'
