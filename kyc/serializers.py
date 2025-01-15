# serializers.py
from rest_framework import serializers
from .models import KYC


class SessionResultSerializer(serializers.Serializer):
    session_id = serializers.CharField()
    user_id = serializers.CharField()

class UserKYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = '__all__'