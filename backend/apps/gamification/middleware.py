"""
JWT WebSocket middleware — query string ?token=<access_token> orqali autentifikatsiya.
"""
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_str: str):
    """JWT access tokenni tekshirib foydalanuvchini qaytaradi."""
    try:
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
        from rest_framework_simplejwt.authentication import JWTAuthentication

        # Tokenni tekshirish
        UntypedToken(token_str)

        # Foydalanuvchini aniqlash
        jwt_auth = JWTAuthentication()
        validated = jwt_auth.get_validated_token(token_str)
        user = jwt_auth.get_user(validated)
        return user
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    WebSocket uchun JWT autentifikatsiya middleware.
    Token query string yoki Header orqali uzatiladi:
      ws://host/ws/duel/123/?token=<jwt_access_token>
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Query string dan token olish
        qs = parse_qs(scope.get('query_string', b'').decode())
        token = qs.get('token', [None])[0]

        if token:
            scope['user'] = await get_user_from_token(token)
        elif 'user' not in scope:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """AuthMiddlewareStack o'rniga ishlatiladi — JWT + session fallback."""
    from channels.auth import AuthMiddlewareStack
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))
