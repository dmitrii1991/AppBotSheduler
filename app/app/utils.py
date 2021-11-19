import secrets
import string
import bcrypt
from typing import Optional
from datetime import timedelta, datetime

from jose import JWTError, jwt

from settings import ADMIN_TOKEN, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


class Secret:

    @staticmethod
    def get_new_password(difficult=10) -> bytes:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for i in range(difficult))
        return password.encode()

    @staticmethod
    def hashpw(password: bytes) -> bytes:
        return bcrypt.hashpw(password, ADMIN_TOKEN)

    @staticmethod
    def checkpw(password: bytes, hash_password: str) -> bool:
        return hash_password == bcrypt.hashpw(password, ADMIN_TOKEN).decode()


class JWT:

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, ADMIN_TOKEN.decode(), algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode(token):
        return jwt.decode(token, ADMIN_TOKEN.decode(), algorithms=[ALGORITHM])
