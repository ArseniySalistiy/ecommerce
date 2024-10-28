from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, insert
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from jwt import PyJWTError

from app.models.user import User
from app.schemas import CreateUser
from app.backend.db_depends import get_db
from app.models.config import settings

router = APIRouter(prefix='/auth', tags=['auth'])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')

@router.post('/')
async def auth(db: Annotated[AsyncSession, Depends(get_db)], user: CreateUser):
    await db.execute(insert(User).values(first_name=user.first_name,
                                         last_name=user.last_name,
                                         username=user.username,
                                         email=user.email,
                                         hashed_password=bcrypt_context.hash(user.password)))

    await db.commit()
    return {'status_code': status.HTTP_201_CREATED,
            'detail': 'User created!'}

async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str):
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='such user doesnt exist',
                            headers={"WWW-Authenticate": "Bearer"})
    return user

async def create_access_token(username: str, user_id: int, is_admin: bool, is_supplier: bool, is_customer: bool):
    iat = datetime.now(timezone.utc)
    exp = datetime.now(timezone.utc) + timedelta(minutes=10)
    payload = {'sub': username, 'id': user_id, 'is_admin': is_admin,
               'is_supplier': is_supplier, 'is_customer': is_customer, 'iat': iat, 'exp': exp}
    return jwt.encode(payload, settings.secret_key, settings.algorithm)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        is_admin: bool = payload.get('is_admin')
        is_supplier: bool = payload.get('is_supplier')
        is_customer: bool = payload.get('is_customer')
        exp_time = payload.get('exp')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='couldnt validate user')

        if exp_time is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='No access token provided')

        return {'username': username,
                'id': user_id,
                'is_admin': is_admin,
                'is_supplier': is_supplier,
                'is_customer': is_customer}

    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='couldnt validate user')

@router.post('/token')
async def login(db: Annotated[AsyncSession, Depends(get_db)], form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(db, form.username, form.password)
    token = await create_access_token(user.username, user.id, user.is_admin, user.is_supplier, user.is_customer)

    return {'access_token': token,
            'token_type': 'bearer'}

@router.get('/current_user')
async def current_user(user: dict = Depends(get_current_user)):
    return user