from django.http import JsonResponse
from .models import UserToken

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get('auth_token')
        if token:
            try:
                user_token = UserToken.objects.get(token=token)
                request.user = user_token.user
            except UserToken.DoesNotExist:
                pass
        return self.get_response(request)