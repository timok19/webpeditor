from datetime import datetime, timedelta
from webpeditor.settings import SECRET_KEY
from jose import jwt


def create_jwt_token(user_id: str) -> str:
    secret_jwt_key = SECRET_KEY
    expires_in_minutes = 30

    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    }

    return jwt.encode(payload, key=secret_jwt_key, algorithm='HS256')


def decode_jwt_token(encoded_jwt: str) -> dict[str, datetime | str]:
    secret_jwt_key = SECRET_KEY

    return jwt.decode(encoded_jwt, secret_jwt_key, algorithms=["HS256"])
