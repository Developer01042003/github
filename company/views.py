from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from .models import Company
from .serializers import (CompanySerializer, CompanySignupSerializer,
                        CompanyLoginSerializer)
from users.models import userUniquness

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @action(detail=False, methods=['post'])
    def signup(self, request):
        serializer = CompanySignupSerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()
            return Response({
                'message': 'Company registered successfully. Please wait for admin verification.',
                'company': CompanySerializer(company).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = CompanyLoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                company = Company.objects.get(email=serializer.validated_data['email'])
                if check_password(serializer.validated_data['password'], company.password):
                    refresh = RefreshToken.for_user(company)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'company': CompanySerializer(company).data
                    })
                return Response({'error': 'Invalid credentials'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            except Company.DoesNotExist:
                return Response({'error': 'Company not found'}, 
                              status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

    @action(detail=False, methods=['post'])
    def add_user(self, request):
        # Get API credentials from request
        api_key = request.data.get('api_key')
        api_id = request.data.get('api_id')
        

        # Validate API credentials
        
        company = Company.objects.get(api_key=api_key, api_id=api_id)
            
            # Check if company is verified
        if not company.is_verified:
                return Response({
                    'error': 'Company is not verified'
                }, status=status.HTTP_401_UNAUTHORIZED)

        # Check if user exists and is verified
        id = request.data.get('id')
        try:
            userUniquness = userUniquness.objects.get(id=id)
            userUniquness.is_verified = True
            userUniquness.save()
            return Response({
                
                'status': True
            }, status=status.HTTP_201_CREATED)
       
        except Exception as e:
            return Response({
                'status': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])    
    def get_kyc_certificate(self,request):
        kyc_key = request.data.get('kyc_key')
        pass
