from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        AUTHOR = 'author', 'Автор'
        REVIEWER = 'reviewer', 'Рецензент'
        ADMIN = 'admin', 'Администратор'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.AUTHOR)
    full_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.user.username
