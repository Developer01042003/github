import logging
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)

class AWSRekognition:
    def __init__(self):
        # Initialize Rekognition and S3 clients
        self.client = boto3.client(
            'rekognition',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.collection_id = 'user_faces'
        self.ensure_collection_exists()

    def ensure_collection_exists(self):
        """Ensure Rekognition collection exists."""
        try:
            self.client.describe_collection(CollectionId=self.collection_id)
            logger.info(f"Collection {self.collection_id} exists.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                self.client.create_collection(CollectionId=self.collection_id)
                logger.info(f"Collection {self.collection_id} created.")
            else:
                raise Exception(f"Error checking collection: {str(e)}")

    def create_face_liveness_session(self):
        """Create a face liveness session."""
        try:
            response = self.client.create_face_liveness_session(
                Settings={
                    'OutputConfig': {
                        'S3Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    }
                }
            )
            logger.info(f"Face liveness session created with ID: {response['SessionId']}")
            return response['SessionId']
        except Exception as e:
            raise Exception(f"Error creating face liveness session: {str(e)}")

    def clear_collection(self):
        """Clear all faces in the Rekognition collection."""
        try:
            # List all faces in the collection
            response = self.client.list_faces(CollectionId=self.collection_id)
            face_ids = [face['FaceId'] for face in response.get('Faces', [])]
            
            # Delete faces if any are found
            if face_ids:
                self.client.delete_faces(CollectionId=self.collection_id, FaceIds=face_ids)
                logger.info(f"Deleted {len(face_ids)} faces from collection {self.collection_id}.")
            else:
                logger.info("No faces found in the collection to delete.")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise Exception(f"Error clearing collection: {str(e)}")

    def get_session_results(self, session_id):
        """Retrieve session results from AWS Rekognition."""
        try:
            response = self.client.get_face_liveness_session_results(SessionId=session_id)
            return {'response': response}
        except Exception as e:
            raise Exception(f"Error getting session results: {str(e)}")

    def search_faces(self, image_bytes):
        """Search for duplicate faces in the Rekognition collection."""
        try:
            response = self.client.search_faces_by_image(
                CollectionId=self.collection_id,
                Image={'Bytes': image_bytes},
                MaxFaces=1,
                FaceMatchThreshold=95
            )
            if 'FaceMatches' in response and response['FaceMatches']:
                logger.info(f"Found duplicate face matches with confidence: {response['FaceMatches'][0]['Similarity']}")
            else:
                logger.info("No duplicate faces found.")
            return response.get('FaceMatches', [])
        except Exception as e:
            logger.error(f"Error searching faces: {str(e)}")
            raise Exception(f"Error searching faces: {str(e)}")

    def index_face(self, image_bytes):
        """Index a face into the Rekognition collection."""
        try:
            response = self.client.index_faces(
                CollectionId=self.collection_id,
                Image={'Bytes': image_bytes},
                MaxFaces=1,
                QualityFilter="AUTO"
            )
            if response['FaceRecords']:
                face_id = response['FaceRecords'][0]['Face']['FaceId']
                logger.info(f"Indexed face with Face ID: {face_id}")
                return face_id
            else:
                logger.warning("No faces were indexed.")
                return None
        except Exception as e:
            logger.error(f"Error indexing face: {str(e)}")
            raise Exception(f"Error indexing face: {str(e)}")

    def download_image_as_bytes(self, bucket_name, object_key):
        """Download an image from S3 and return its bytes."""
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)
            logger.info(f"Downloaded image from S3: {object_key}")
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Error downloading image from S3: {e}")
            raise Exception(f"Error downloading image from S3: {e}")

