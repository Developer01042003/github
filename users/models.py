from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    full_name = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])
    address = models.TextField()
    country = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_banned = models.BooleanField(default=False)
    is_kyc = models.BooleanField(default=False)
    is_nft = models.BooleanField(default=False)

    def __str__(self):
        return self.email

class userUniquness(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    id = models.UUIDField(default=uuid.uuid4,primary_key=True, unique=True, editable=False)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)

class kycShareKey(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    company_id = models.CharField(max_length=255)
    id = models.UUIDField(primary_key=True, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_shared = models.BooleanField(default=False)


class nft_uniquekey(models.Model):
    nft_unique = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
