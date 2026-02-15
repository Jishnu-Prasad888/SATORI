from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Node

class NodeAPIAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-Node-API-Key')
        if not api_key:
            return None
        
        try:
            node = Node.objects.get(api_key=api_key)
            return (node, node)  # Return node as both user and auth
        except Node.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')