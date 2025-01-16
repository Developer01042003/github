from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password

from company.permissions import IsValidAuthToken
from .models import Company, CustomAuthToken, KycSharedData, apiKeys, nft_data
from django.utils.crypto import get_random_string
from .serializers import (CompanySerializer, CompanySignupSerializer,
                        CompanyLoginSerializer)
from users.models import userUniquness
from rest_framework.permissions import AllowAny


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def signup(self, request):
        serializer = CompanySignupSerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()
            return Response({
                'status': True,
                'message': 'Company registered successfully. Please wait for admin verification.',
                
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = CompanyLoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Fetch the company by email
            company = Company.objects.filter(email=email).first()

            if not company:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if the company is verified
            if not company.is_verified:
                return Response({'error': 'Company not verified. Please contact admin.'}, status=status.HTTP_401_UNAUTHORIZED)

            # Verify the password
            if not check_password(password, company.password):
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

            # Generate a new token (company_id + random string)
            random_string = get_random_string(length=32)  # Generate a random string
            token = f"{company.company_id}_{random_string}"

            # Get the IP address from the request
            ip_address = request.META.get('REMOTE_ADDR')

            # Delete any existing token for this company
            CustomAuthToken.objects.filter(company=company).delete()

            # Create a new token and save it with the IP address
            CustomAuthToken.objects.create(
                company=company,
                token=token,
                ip_address=ip_address
            )

            # Fetch API keys (if they exist)
            api_keys = apiKeys.objects.filter(company=company).first()

            # Serialize company data
            company_data = CompanySerializer(company).data

            # Prepare response data
            response_data = {
                'token': token,
                'message': "Login successful, new token generated.",
                'company': company_data  # Include company data here
            }

            if api_keys:
                response_data.update({
                    'api_id': api_keys.api_id,
                    'api_key': api_keys.api_key,
                })

            # Return success response
            return Response(response_data, status=status.HTTP_200_OK)

        # If serializer validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    #update dashboard company
    @action(detail=False, methods=['post'], permission_classes=[IsValidAuthToken])
    def refresh_dashboard(self, request):
        # Fetch the company from the request (attached by the permission class)
        company = request.company

        # Get the company's balance
        balance = company.balance

        try:
            # Try fetching API keys for the company
            api = apiKeys.objects.get(company=company)
            return Response({
                'company': CompanySerializer(company).data,  # Include serialized company data
                'balance': balance,
                'api_id': api.api_id,
                'api_key': api.api_key
            }, status=status.HTTP_200_OK)
        except apiKeys.DoesNotExist:
            # If API keys do not exist, return the response without them
            return Response({
                'company': CompanySerializer(company).data,  # Include serialized company data
                'balance': balance
            }, status=status.HTTP_200_OK)

      

    
    
    
    @action(detail=False, methods=['post'], permission_classes=[IsValidAuthToken])
    def get_api(self, request):
        # Fetch the company from the request (attached by the permission class)
        company = request.company

        # Check if the company has API access and is verified
        if company.is_api and company.is_verified:
            return Response({
                'api_id': company.get_api_id(),
                'api_key': company.get_api_key()
            }, status=status.HTTP_200_OK)

        # If API access is not enabled but the company is verified, create API keys
        if not company.is_api and company.is_verified:
            api = apiKeys.objects.create(company=company)
            company.is_api = True
            company.save()
            return Response({
                'api_id': api.api_id,
                'api_key': api.api_key
            }, status=status.HTTP_201_CREATED)

        # If the company is not verified
        return Response({
            'error': 'Company not verified.'
        }, status=status.HTTP_401_UNAUTHORIZED) 
    
            

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
        if company.balance < 0.0001:
            return Response({
                'error': 'Insufficient balance'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        id = request.data.get('id')
        try:
            balance = company.balance - 0.09
            company.balance = balance
            company.save()
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
        api_key = request.data.get('api_key')
        api_id = request.data.get('api_id')

        apiKeys = apiKeys.objects.get(api_key=api_key, api_id=api_id)
        if apiKeys:
            company = apiKeys.company
        if company.balance < 10:
            return Response({
                'error': 'Insufficient balance'
            }, status=status.HTTP_400_BAD_REQUEST)
        if company.is_verified == True and company.is_kyc_need == True:
            if company:
                kyc_check = KycSharedData.objects.filter(id=kyc_key, company=company)
                if kyc_check:
                    return Response({
                        'error': 'KYC already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
            kyc = KycSharedData.objects.create(id=kyc_key, company=company, is_kyc_certificate=True)
            company.balance = company.balance - 0.90
            company.save()
            return Response({
                'status': True
            }, status=status.HTTP_200_OK)
        


        
    
    @action(detail=False, methods=['post'])
    def nft_verification(self,request):
        api_key = request.data.get('api_key')
        api_id = request.data.get('api_id')
        nft_unique = request.data.get('nft_unique')
        
        apiKeys = apiKeys.objects.get(api_key=api_key, api_id=api_id)

        if apiKeys:
            company = apiKeys.company
        
        if company.balance < 5:
            return Response({
                'error': 'Insufficient balance'
            }, status=status.HTTP_400_BAD_REQUEST)
        if company.is_verified == True:
            if company:
                nft_check = nft_data.objects.filter(nft_unique=nft_unique, Company=company)
                if nft_check:
                    return Response({
                        'error': 'NFT already exists'
                    }, status=status.HTTP_400_BAD_REQUEST)
            nft = nft_data.objects.create(nft_unique=nft_unique, Company=company, is_verified=True)
            company.balance = company.balance - 0.09
            company.save()
            return Response({
                'status': True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Company not verified'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        
        


