from pwdlib import PasswordHash
from jwt import encode, decode
from jwt.exceptions import PyJWTError
from datetime import datetime, timedelta
import pytz
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_session
from fastapi import Depends, HTTPException
from http import HTTPStatus
from models import User


pwd_context = PasswordHash.recommended()
oauth2_schema = OAuth2PasswordBearer(tokenUrl='token')


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


SECRET_KEY = 'your-secret-key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(pytz.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_schema),
):
    '''
    Pega o usuario atual a partir do token gerado no login
    '''
    credential_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload['sub']
        if not email:
            raise credential_exception
    except PyJWTError:
        raise credential_exception

    db_user = session.scalar(select(User).where(User.email == email))
    if not db_user:
        raise credential_exception

    return db_user
