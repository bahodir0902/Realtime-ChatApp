from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from accounts.models import User


@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token.payload.get('user_id')

        user = User.objects.get(id=user_id)
        return user
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()

class JwtAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_sting = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_sting)

        token = query_params.get('token', [None])[0]

        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith("Bearer "):
                token = auth_header.split(' ')[1]

        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)