from django.db import models
import uuid
from django.contrib.auth.hashers import make_password
from django.conf import settings

class Company(models.Model):
    company_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    address = models.TextField()
    country = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    is_kyc_need = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False)
    api_id = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True, unique=True)
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"




class KycSharedData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, unique=True, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_shared = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'company')
