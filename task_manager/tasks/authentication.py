import jwt
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

def generate_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token