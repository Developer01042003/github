# views.py
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import KYC
from rest_framework.permissions import IsAuthenticated
from .serializers import UserKYCSerializer
from .aws_helper import AWSRekognition
from django.conf import settings
from django.core.exceptions import ValidationError

class CreateSessionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Print request details
            print("Request User:", request.user)
            print("Request Data:", request.data)
            print("Request Headers:", request.headers)

            user_id = request.user.id
            print(f"Processing request for user_id: {user_id}")

            # Verify AWS credentials are loaded
            

            aws_rekognition = AWSRekognition()
            
            # Add more detailed error handling for session creation
            try:
                session_id = aws_rekognition.create_face_liveness_session()
                print(f"Created session ID: {session_id}")
            except Exception as session_error:
                print(f"Session creation error: {str(session_error)}")
                return Response({
                    'error': 'Session creation failed',
                    'detail': str(session_error)
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'session_id': session_id,
                'message': 'Session created successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"General error in CreateSessionView: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return Response({
                'error': 'Request failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class SessionResultView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Processing session result for user: {user.id}, session_id: {session_id}")
        try:
            aws_rekognition = AWSRekognition()

            # Step 1: Get session results
            session_results = aws_rekognition.get_session_results(session_id)['response']
            

            # Extract confidence level
            confidence = session_results.get('Confidence', 0)
            if confidence < 75:
                print(f"Liveness check failed with confidence: {confidence}")
                return Response({
                    'message': 'Liveness check failed',
                    'confidence': confidence
                }, status=status.HTTP_400_BAD_REQUEST)

            # Step 2: Retrieve reference image S3 information
            reference_image_info = session_results.get('ReferenceImage', {}).get('S3Object')
            if not reference_image_info:
                return Response({'error': 'Reference image not found'}, status=status.HTTP_400_BAD_REQUEST)

            bucket_name = reference_image_info['Bucket']
            object_key = reference_image_info['Name']
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"

            # Step 3: Download image as bytes from S3
            reference_image_bytes = aws_rekognition.download_image_as_bytes(bucket_name, object_key)

            # Step 4: Check for duplicate faces
            face_matches = aws_rekognition.search_faces(reference_image_bytes)
            if face_matches:
                print("duplicate found")
                print(f"Duplicate face found: {face_matches[0]['Face']['FaceId']}")
                return Response({
                    'message': 'Duplicate face found',
                    'match_confidence': face_matches[0]['Similarity']
                }, status=status.HTTP_400_BAD_REQUEST)

            # Step 5: Index the face using the downloaded bytes
            face_id = aws_rekognition.index_face(reference_image_bytes)
            print(f"Indexed face ID: {face_id}")
            # Step 6: Create KYC record using the existing S3 image URL
            kyc = KYC(
                user=request.user,
                face_id=face_id,
                s3_image_url=s3_url,
                is_verified=True
            )
            kyc.full_clean()
            kyc.save()

            return Response({
                'message': 'KYC completed successfully',
                'confidence': confidence
            }, status=status.HTTP_200_OK)

        except Exception as e:
           
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
