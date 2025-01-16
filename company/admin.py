from django.contrib import admin
from .models import Company,KycSharedData
import uuid

from django.contrib import admin
from .models import Company, apiKeys

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    # Use the methods from the Company model to display api_id and api_key
    list_display = ('name', 'email', 'balance', 'display_api_id', 'display_api_key', 'is_verified')
    readonly_fields = ('display_api_id', 'display_api_key')  # Use methods to access API data

    def display_api_id(self, obj):
        # Safely fetch the related api_id
        api_key_obj = apiKeys.objects.filter(company=obj).first()
        return api_key_obj.api_id if api_key_obj else "N/A"
    display_api_id.short_description = 'API ID'

    def display_api_key(self, obj):
        # Safely fetch the related api_key
        api_key_obj = apiKeys.objects.filter(company=obj).first()
        return api_key_obj.api_key if api_key_obj else "N/A"
    display_api_key.short_description = 'API Key'


@admin.register(KycSharedData)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ('company', 'user', 'created_at')
    list_filter = ('company', 'created_at')
    
