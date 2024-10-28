from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.user import User
from .auth import get_current_user
router = APIRouter(prefix='/permission', tags=['permission'])

@router.patch('/')
async def supplier_permission(db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)], id: int):
    if get_user.get('is_admin'):
        user = await db.scalar(select(User).where(User.id == id))

        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='User doesnt exist')

        if user.is_supplier:
            await db.execute(update(User).where(User.id == id).values(is_supplier=False, is_customer=True))
            await db.commit()
            return {'status_code': status.HTTP_200_OK,
                    'detail': 'user isnt supplier anymore'}

        if not user.is_supplier:
            await db.execute(update(User).where(User.id == id).values(is_supplier=True, is_customer=False))
            await db.commit()
            return {'status_code': status.HTTP_200_OK,
                    'detail': 'user is supplier now'}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You are not admin')

@router.delete('/delete/user')
async def deletion_of_user(db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)], id: int):
    if get_user.get('is_admin'):
        user = await db.scalar(select(User).where(User.id == id))

        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Such user doesnt exist')
        if user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You cant delete admin')
        if user.is_active:
            await db.execute(update(User).where(User.id == id).values(is_active=False))
            await db.commit()
            return {'status_code': status.HTTP_200_OK,
                    'detail': 'User has been deleted'}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not admin, you cant delete users')