from django.db import models
from django.conf import settings

class KYC(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kyc_records')
    selfie_url = models.URLField()
    face_id = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"KYC for {self.user}"

    class Meta:
        verbose_name = "KYC"
        verbose_name_plural = "KYCs"