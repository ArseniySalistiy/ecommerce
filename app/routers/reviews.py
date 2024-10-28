from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update

from app.backend.db_depends import get_db
from app.routers.auth import get_current_user
from app.models.review import Review
from app.models.rating import Rating
from app.models.products import Product
from app.schemas import CreateReview, CreateRating

router = APIRouter(prefix='/reviews', tags=['reviews'])

@router.get('/get/reviews')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))

    if reviews is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='This product doesnt have any reviews yet')

    return reviews.all()

@router.get('/get/{product_id}')
async def product_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_id: int):
    reviews = await db.scalars(select(Review).where(Review.product_id == product_id))
    ratings = await db.scalars(select(Rating).where(Rating.product_id == product_id))

    if reviews is None or ratings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='There are no reviews on this product')

    return {'Ratings': ratings.all(),
            'Reviews': reviews.all()}

@router.post('/create/review')
async def create_review(db: Annotated[AsyncSession, Depends(get_db)], get_user: Annotated[dict, Depends(get_current_user)], rating: CreateRating, review: CreateReview, product_id: int):
    if get_user.get('is_customer'):
        product = await db.scalar(select(Product).where(Product.id == product_id))

        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='There is no such product')

        user_rating = await db.scalar(select(Rating).where(Rating.user_id == get_user.get('id'), Rating.product_id == product_id))
        user_review = await db.scalar(select(Review).where(Review.user_id == get_user.get('id'), Review.product_id == product_id))


        if (user_review is None and user_rating is None) or (user_review.is_active == False and user_rating.is_active == False): #проверка на уже добавленный отзыв пользователем

            await db.execute(insert(Rating).values(grade=rating.rating, user_id=get_user.get('id'), product_id=product_id))

            await db.commit()

            recent_rating = await db.scalar(select(Rating).where(Rating.user_id == get_user.get('id'), Rating.product_id == product_id))

            await db.execute(insert(Review).values(user_id=get_user.get('id'), product_id=product_id, comment=review.comment, rating_id=recent_rating.id))

            await db.commit()

            ratings = await db.scalars(select(Rating).where(Review.product_id == product_id))

            all_ratings = [rating.grade for rating in ratings.all()]
            average_rating = sum(all_ratings) / len(all_ratings)

            await db.execute(update(Product).where(Product.id == product_id).values(rating=average_rating))

            await db.commit()

            return {'status_code': status.HTTP_200_OK,
                    'detail': 'your review has been sent'}
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='You already reviewed this product')

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only customer can add a review')


@router.delete('/delete/{product_id}') #удаление пользователем своего собственного отзыва
async def delete_review_customer(db: Annotated[AsyncSession, Depends(get_db)], product_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_customer'):
        review = await db.scalar(select(Review).where(Review.product_id == product_id, Review.user_id == get_user.get('id')))
        rating = await db.scalar(select(Rating).where(Rating.product_id == product_id, Rating.user_id == get_user.get('id')))

        if review.is_active == False and rating.is_active == False:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Review and rating already deleted')

        else:
            await db.execute(update(Review).where(Review.user_id == get_user.get('id'), Review.product_id == product_id).values(is_active=False))
            await db.execute(update(Rating).where(Rating.user_id == get_user.get('id'), Rating.product_id == product_id).values(is_active=False))

            await db.commit()

        return {'status_code': status.HTTP_200_OK,
                'detail': 'Your review has been deleted'}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You cant delete this review')

@router.delete('/admin/delete/{review_id}') #удаление любого отзыва админом
async def delete_review_admin(db: Annotated[AsyncSession, Depends(get_db)], rating_id: int, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        rating = await db.scalar(select(Rating).where(Rating.id == rating_id))
        review = await db.scalar(select(Review).where(Review.rating_id == rating_id))

        if review.is_active == False and rating.is_active == False:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='Review and rating already deleted')

        else:
            await db.execute(update(Review).where(Review.rating_id == rating_id).values(is_active=False))
            await db.execute(update(Rating).where(Rating.id == rating_id).values(is_active=False))

            await db.commit()

        return {'status_code': status.HTTP_200_OK,
                'detail': 'Review has been deleted'}

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You cant delete this review')