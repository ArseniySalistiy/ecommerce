from fastapi import APIRouter, Depends, status, HTTPException
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import *
from sqlalchemy import insert, select, update
from app.schemas import CreateCategory
from app.routers.auth import get_current_user

from slugify import slugify

router = APIRouter(prefix='/category', tags=['category'])

@router.get('/all_categories')
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    categories = await db.scalars(select(Category).where(Category.is_active == True)) # select for getting data from sql table. where is being used to filter data and all() returns data in the list
    return categories.all()

@router.post('/create')
async def create_category(db: Annotated[AsyncSession, Depends(get_db)], create_category: CreateCategory, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        await db.execute(insert(Category).values(name = create_category.name, parent_id=create_category.parent_id, slug=slugify(create_category.name))) # slugify function formats text
        await db.commit()
        return {'status_code': status.HTTP_201_CREATED,
                'transaction': 'Successful'}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not admin')

@router.put('/update_category')
async def update_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: int, category: CreateCategory, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        category1 = await db.scalar(select(Category).where(Category.id == category_id))
        if category1 is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='category not found')
        await db.execute(update(Category).where(Category.id == category_id).values(name=category.name,
                                                                         slug=slugify(category.name),
                                                                         parent_id=category.parent_id))
        await db.commit()
        return {'status_code': status.HTTP_200_OK,
            'transaction': 'Category successfully updated!'}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not admin')

@router.delete('/delete')
async def delete_category(db: Annotated[AsyncSession, Depends(get_db)], category_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        category = await db.scalar(select(Category).where(Category.id == category_id))
        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='There is no such category')
        await db.execute(update(Category).where(Category.id == category_id).values(is_active=False)) # делаем запрос на изменение is_active на False у категории с переданным id
        await db.commit()
        return {'status_code': status.HTTP_200_OK,
                'transaction': 'Category deletion is successful'}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not admin')
