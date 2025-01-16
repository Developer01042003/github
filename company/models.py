from datetime import timezone
from django.db import models
import uuid
from django.contrib.auth.hashers import make_password
from django.conf import settings

class Company(models.Model):
    company_id = models.CharField(primary_key=True,max_length=255, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    address = models.TextField()
    country = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    is_kyc_need = models.BooleanField(default=False)
    is_api = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=10, decimal_places=4, default=0.000)
    
    # New field to link to the User model
    

    def get_api_id(self):
        api_key_obj = apiKeys.objects.filter(company=self).first()
        return api_key_obj.api_id if api_key_obj else None

    def get_api_key(self):
        api_key_obj = apiKeys.objects.filter(company=self).first()
        return api_key_obj.api_key if api_key_obj else None

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"

class CustomAuthToken(models.Model):
    company = models.ForeignKey(Company, related_name='auth_tokens', on_delete=models.CASCADE)
    token = models.CharField(max_length=256, unique=True)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"Token: {self.token} for Company: {self.company.name}, IP: {self.ip_address}"


class apiKeys(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    api_id = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True, unique=True)
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True, unique=True)

    def __str__(self):
        return self.company.name

class nft_data(models.Model):
    Company = models.ForeignKey(Company, on_delete=models.CASCADE)
    nft_unique = models.CharField(max_length=255, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class KycSharedData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, unique=True, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_kyc_certificate = models.BooleanField(default=False)
    is_full_kyc = models.BooleanField(default=False)
    is_half_kyc = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_shared = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'company')
