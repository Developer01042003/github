from django.contrib import admin
from .models import KYC




admin.site.register(KYC)

from django.contrib import admin
from .models import AWSRekognitionDummy
from .admin_actions import clear_face_collection  # Adjust the import path if needed


@admin.register(AWSRekognitionDummy)
class AWSRekognitionAdmin(admin.ModelAdmin):
    actions = [clear_face_collection]
    list_display = ('name',)

