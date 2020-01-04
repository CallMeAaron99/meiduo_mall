from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField(max_length=15, unique=True)
    email_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'tb_users'
