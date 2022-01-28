from logging import getLogger

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token

logger = getLogger('chat')


@database_sync_to_async
def get_user(token_key):
    try:
        token = Token.objects.get(key=token_key)
        print(f"obj {token = }")
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        logger.info("from middleware")
        try:

            # token_key = None
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
            print(f"{token_key = }")
            print(f"{token_key = }")
        except ValueError:
            token_key = None
        scope['user'] = AnonymousUser()  # if token_key is None else await get_user(token_key)
        return await super().__call__(scope, receive, send)
