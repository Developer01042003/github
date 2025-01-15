from django.contrib import admin
from .models import KYC

from django.contrib import admin
from django.contrib import messages
from .aws_helper import AWSRekognition


@admin.action(description="Clear AWS Rekognition Face Collection")
def clear_face_collection(modeladmin, request, queryset):
    """Admin action to clear the Rekognition face collection."""
    rekognition = AWSRekognition()
    try:
        rekognition.clear_collection()
        messages.success(request, "Successfully cleared the Rekognition face collection.")
    except Exception as e:
        messages.error(request, f"Error clearing the face collection: {str(e)}")


admin.site.register(KYC)
