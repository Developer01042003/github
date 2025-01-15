import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import KYC
from rest_framework.permissions import IsAuthenticated
from .aws_helper import AWSRekognition
from django.conf import settings

logger = logging.getLogger(__name__)

class CreateSessionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Print request details
            logger.info(f"Request User: {request.user}")
            logger.info(f"Request Data: {request.data}")
            logger.info(f"Request Headers: {request.headers}")

            user_id = request.user.id
            logger.info(f"Processing request for user_id: {user_id}")

            # Initialize AWS Rekognition
            aws_rekognition = AWSRekognition()
            
            # Create session
            try:
                session_id = aws_rekognition.create_face_liveness_session()
                logger.info(f"Created session ID: {session_id}")
            except Exception as session_error:
                logger.error(f"Session creation error: {str(session_error)}")
                return Response({
                    'error': 'Session creation failed',
                    'detail': str(session_error)
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'session_id': session_id,
                'message': 'Session created successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"General error in CreateSessionView: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
            logger.warning("Session ID is missing in request.")
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Processing session result for user: {user.id}, session_id: {session_id}")
        try:
            aws_rekognition = AWSRekognition()

            # Step 1: Get session results
            try:
                session_results = aws_rekognition.get_session_results(session_id)['response']
                logger.info(f"Session results: {session_results}")  # Log the full response to check its structure
            except Exception as session_error:
                logger.error(f"Error retrieving session results: {session_error}")
                return Response({'error': 'Failed to retrieve session results', 'detail': str(session_error)}, status=status.HTTP_400_BAD_REQUEST)

            # Check if session_results is a dictionary or list and log accordingly
            if isinstance(session_results, list):
                logger.error(f"Unexpected structure: session_results is a list, not a dictionary. Contents: {session_results}")
                return Response({'error': 'Unexpected structure in session results'}, status=status.HTTP_400_BAD_REQUEST)

            # Step 2: Extract confidence level
            confidence = session_results.get('Confidence', 0)
            if confidence < 75:
                logger.warning(f"Liveness check failed with confidence: {confidence}")
                return Response({
                    'message': 'Liveness check failed',
                    'confidence': confidence
                }, status=status.HTTP_400_BAD_REQUEST)

            # Step 3: Retrieve reference image S3 information
            reference_image_info = session_results.get('ReferenceImage', {}).get('S3Object')
            if not reference_image_info:
                logger.error("Reference image not found in session results.")
                return Response({'error': 'Reference image not found'}, status=status.HTTP_400_BAD_REQUEST)

            bucket_name = reference_image_info['Bucket']
            object_key = reference_image_info['Name']
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"

            # Step 4: Download image as bytes from S3
            reference_image_bytes = aws_rekognition.download_image_as_bytes(bucket_name, object_key)

            # Step 5: Check for duplicate faces using your `search_faces` helper function
            face_matches = aws_rekognition.search_faces(reference_image_bytes)

            if face_matches:
                # Duplicate face found
                face_id = face_matches[0]['Face']['FaceId']
                total_faces = len(face_matches)
                logger.info(f"Duplicate face found using past Face ID: {face_id} in collection {aws_rekognition.collection_id}, Total faces in collection: {total_faces}")

                # Check if the face_id already exists in the KYC records for this user
                existing_kyc = KYC.objects.filter(user=user, face_id=face_id).first()

                if existing_kyc:
                    logger.info(f"Duplicate face detected for user {user.id} using Face ID {face_id}.")
                    # Return a response indicating that the KYC record already exists
                    return Response({
                        'message': 'Duplicate face detected, KYC already exists',
                        'confidence': confidence,
                        'face_id': face_id,
                        'total_faces_in_collection': total_faces
                    }, status=status.HTTP_200_OK)

                # If no existing KYC found, create a new KYC record
                kyc = KYC.objects.create(
                    user=request.user,
                    face_id=face_id,
                    selfie_url=s3_url,
                    is_verified=True
                )
                return Response({
                    'message': 'KYC completed successfully using duplicate face',
                    'confidence': confidence,
                    'face_id': face_id,
                    'total_faces_in_collection': total_faces
                }, status=status.HTTP_200_OK)

            # Step 6: If no duplicate, index the face using your `index_face` helper function
            face_id = aws_rekognition.index_face(reference_image_bytes)

            # Step 7: Create KYC record with new face
            if face_id:
                kyc = KYC.objects.create(
                    user=request.user,
                    face_id=face_id,
                    selfie_url=s3_url,
                    is_verified=True
                )
                logger.info(f"KYC record created for user {request.user.id} with new Face ID {face_id}")

                return Response({
                    'message': 'KYC completed successfully',
                    'confidence': confidence,
                    'face_id': face_id
                }, status=status.HTTP_200_OK)
            else:
                logger.error("No face was indexed.")
                return Response({'error': 'Face could not be indexed.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error processing session result for user {user.id}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

