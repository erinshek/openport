from django.db import models
from rest_framework.exceptions import ValidationError

from account.models import CustomUser


class Tunnel(models.Model):
    PROTOCOL_CHOICES = [
        ('tcp', 'TCP'),
        ('http', 'HTTP'),
        ('https', 'HTTPS'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('connecting', 'Connecting'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tunnels')
    name = models.CharField(max_length=100)
    protocol = models.CharField(max_length=10, choices=PROTOCOL_CHOICES, default='tcp')
    local_port = models.IntegerField()
    remote_port = models.IntegerField(unique=True)
    public_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    bytes_in = models.BigIntegerField(default=0)
    bytes_out = models.BigIntegerField(default=0)
    connections_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'name']

    def clean(self):
        if self.user.tunnels.filter(status='active').count() >= self.user.max_tunnels:
            raise ValidationError(f'Maximum {self.user.max_tunnels} tunnels allowed')

        if not (1024 <= self.local_port <= 65535):
            raise ValidationError('Local port must be between 1024 and 65535')

        if not (8000 <= self.remote_port <= 9999):
            raise ValidationError('Remote port must be between 8000 and 9999')

    def generate_public_url(self):
        if self.protocol in ['http', 'https']:
            return f"{self.protocol}://{self.user.subdomain}.openport.com"
        else:
            return f"tcp://{self.user.subdomain}.openport.com:{self.remote_port}"

    def save(self, *args, **kwargs):
        if not self.public_url:
            self.public_url = self.generate_public_url()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.protocol}:{self.local_port})"
