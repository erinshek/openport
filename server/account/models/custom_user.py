import secrets
import string

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    subdomain = models.CharField(max_length=50, unique=True)
    api_key = models.CharField(max_length=32, unique=True)
    max_tunnels = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = self.generate_api_key()
        if not self.subdomain:
            self.subdomain = self.username.lower()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_api_key():
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

    def regenerate_api_key(self):
        self.api_key = self.generate_api_key()
        self.save()
        return self.api_key

    def __str__(self):
        return self.username
