from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import *
from sqlalchemy import insert, select, update
from app.schemas import CreateProduct
from app.routers.auth import get_current_user

from slugify import slugify

router = APIRouter(prefix='/products', tags=['products'])

@router.get('/')
async def get_all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    product = await db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0))

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Product not found')

    return product.all()

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], product: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        category = await db.scalar(select(Category).where(Category.id == product.category))

        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Category not found')

        await db.execute(insert(Product).values(name=product.name, slug=slugify(product.name),
                                      rating=0.0, category_id=product.category,
                                      description=product.description,
                                      price=product.price, stock=product.stock,
                                      image_url=product.image_url, supplier_id=get_user.get('id')))
        await db.commit()

        return {'status_code': status.HTTP_201_CREATED,
                'transaction': 'successful'}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Customers arent allowed to use this method')

@router.get('{/category_slug}')
async def products_by_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db.scalar(select(Category).where(Category.slug == category_slug))

    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Product not found')

    subcategories = await db.scalars(select(Category).where(Category.parent_id == category.id))

    categories_and_subcategories = [category.id] + [i.id for i in subcategories.all()]
    products_category = await db.scalars(select(Product).where(Product.category_id.in_(categories_and_subcategories),
                                                         Product.is_active == True, Product.stock > 0))
    return products_category.all()

@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug, Product.is_active == True, Product.stock > 0))

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Product not found')
    return product

@router.put('/detail/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str, product: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        product1 = await db.scalar(select(Product).where(Product.slug == product_slug))

        if product1 is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='Product not found')

        category = await db.scalar(select(Category).where(Category.id == product.category))

        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='No such category')
        if product1.supplier_id == get_user.get('is_supplier'):

            await db.execute(update(Product).where(Product.slug == product_slug).values(name=product.name, slug=slugify(product.name),
                                      rating=0.0, category_id=product.category,
                                      description=product.description,
                                      price=product.price, stock=product.stock,
                                      image_url=product.image_url))
            await db.commit()
            return {'status_code': status.HTTP_200_OK,
                    'transaction': 'successful'}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Its not your product')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Customers arent allowed to use this method')

@router.delete('/delete')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        product = await db.scalar(select(Product).where(Product.id == product_id))

        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='can not find appropriate product')
        if product.supplier_id == get_user.get('is_supplier'):

            await db.execute(update(Product).where(Product.id == product_id).values(is_active = False))

            await db.commit()

            return {'status_code': status.HTTP_200_OK,
                    'transaction': 'Product delete is successful'}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='Its not your product')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Customers arent allowed to use this method')