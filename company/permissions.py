from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import CustomAuthToken

class IsValidAuthToken(BasePermission):
    """
    Permission class to validate auth_token and ip_address.
    """

    def has_permission(self, request, view):
        # Get auth token from headers
        auth_token = request.headers.get('Authorization')  # Token is expected in Authorization header
        
        # Get the IP address considering potential reverse proxies
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        if ip_address and ',' in ip_address:  # In case multiple IPs are forwarded, take the first one
            ip_address = ip_address.split(',')[0].strip()
        
        # Log the extracted data for debugging
        print(f"Authorization Token: {auth_token}")
        print(f"Client IP Address: {ip_address}")

        if not auth_token:
            raise PermissionDenied("Auth token is missing in the Authorization header.")

        try:
            # Validate the token
            token_obj = CustomAuthToken.objects.get(token=auth_token)
            print(f"Token Found: {token_obj.token}")

            # Validate the IP address
            if token_obj.ip_address != ip_address:
                print(f"IP mismatch: Expected {token_obj.ip_address}, Got {ip_address}")
                raise PermissionDenied("IP address does not match the token.")
        except CustomAuthToken.DoesNotExist:
            print(f"Invalid Token: {auth_token}")
            raise PermissionDenied("Invalid auth token.")

        # Attach the company object to the request for further use
        request.company = token_obj.company
        return True
