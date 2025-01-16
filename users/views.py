# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from .models import User, kycShareKey, nft_uniquekey, userUniquness
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, UserLoginSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def signup(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Changed to match frontend's expected token format
            token = RefreshToken.for_user(user)
            return Response({
                'token': str(token.access_token),  # Changed from 'access' to 'token'
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({
                    'error': 'Invalid credentials'  # Generic error message for security
                }, status=status.HTTP_401_UNAUTHORIZED)

            user = authenticate(username=user.username, password=password)
            if user:
                # Changed to match frontend's expected token format
                token = RefreshToken.for_user(user)
                return Response({
                    'token': str(token.access_token),  # Changed from 'access' to 'token'
                    'user': UserSerializer(user).data
                })
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes = [IsAuthenticated])
    def nft_create(self, request):
        user = request.user
        user = User.objects.get(email=user)
        
        if user.is_nft == True and user.is_verified == True and user.is_banned == False:
            try:
                
                    nft_unique = nft_uniquekey.objects.create()
                    nft_unique.is_verified = True
                    nft_unique.save()
                    return Response({
                        'status': True
                        
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], permission_classes = [IsAuthenticated])
    def getUniqueKey(self, request):
        user = request.user
        company_id = request.data.get('company_id')    
        if user & company_id:
            try:
                if user.is_banned == False & user.is_verified == True:
                    user_unique = userUniquness.objects.filter(company_id=company_id,user=user)
                    if user_unique:
                        return Response({
                            'error': 'User already exists'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        user_unique = userUniquness.objects.create(user=user,company_id=company_id)
                        id = user_unique.id
                        return Response({
                            'id': id,
                            
                        }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=False, methods=['post'], permission_classes = [IsAuthenticated])
    def kycShareKey(self, request):
        user = request.user
        company_id = request.data.get('company_id')
        if user & company_id:
            try:
                if user.is_banned == False & user.is_verified == True:
                    kyc_key = kycShareKey.objects.filter(company=company_id,user=user)
                    if kyc_key:
                        return Response({
                            'error': 'User already exists'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        kyc_key = kycShareKey.objects.create(user=user,company=company_id)
                        id = kyc_key.id
                        return Response({
                            'id': id,
                            
                        }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=False, methods=['post'], permission_classes = [IsAuthenticated])
    def dashboard(self, request):
        user = request.user
        if user:
            return Response({
                'user': UserSerializer(user).data
            })
        return Response({
            'error': 'User is not verified'
        }, status=status.HTTP_400_BAD_REQUEST)
    

                    

                




