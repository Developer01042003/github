from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import CustomAuthToken

class IsValidAuthToken(BasePermission):
    """
    Permission class to validate auth_token and ip_address.
    """
    def has_permission(self, request, view):
        auth_token = request.headers.get('Authorization')  # Assuming token is sent in Authorization header
        ip_address = request.META.get('REMOTE_ADDR')       # Get the user's IP address

        if not auth_token:
            raise PermissionDenied("Auth token is missing.")

        # Check if token exists and matches the IP address
        try:
            token_obj = CustomAuthToken.objects.get(token=auth_token)
            if token_obj.ip_address != ip_address:
                raise PermissionDenied("IP address does not match the token.")
        except CustomAuthToken.DoesNotExist:
            raise PermissionDenied("Invalid auth token.")

        # Attach the company to the request for further use
        request.company = token_obj.company
        return True
