from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path
from sqlalchemy.orm import Session

from app.database.connect_db import get_db
from app.schemas import RatingModel
from app.repository import ratings as repository_ratings
from app.services.auth import auth_service
from app.services.roles import RoleChecker
from app.database.models import User, UserRoleEnum
from app.conf.messages import NOT_FOUND, NO_POST_ID, COMM_NOT_FOUND, NO_RATING

router = APIRouter(prefix='/ratings', tags=["ratings"])

# Ролі для доступу
allowed_get_all_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
allowed_create_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_edit_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_remove_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
allowed_user_post_rate = RoleChecker([UserRoleEnum.admin])
allowed_commented_by_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])


# --------------------------------------------
# CREATE RATING
# --------------------------------------------
@router.post(
    "/posts/{post_id}/{rate}",
    response_model=RatingModel,
    dependencies=[Depends(allowed_create_ratings)]
)
async def create_rate(
    post_id: int,
    rate: int = Path(..., description="Rating from 1 to 5 stars.", ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Створює новий рейтинг для поста.

    - **post_id**: ID поста
    - **rate**: Значення рейтингу від 1 до 5
    """
    new_rate = await repository_ratings.create_rate(post_id, rate, db, current_user)
    if new_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_POST_ID)
    return new_rate


# --------------------------------------------
# EDIT RATING
# --------------------------------------------
@router.put(
    "/edit/{rate_id}/{new_rate}",
    response_model=RatingModel,
    dependencies=[Depends(allowed_edit_ratings)]
)
async def edit_rate(
    rate_id: int,
    new_rate: int = Path(..., description="New rating value from 1 to 5", ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Редагує існуючий рейтинг.

    - **rate_id**: ID рейтингу
    - **new_rate**: Нове значення рейтингу від 1 до 5
    """
    edited_rate = await repository_ratings.edit_rate(rate_id, new_rate, db, current_user)
    if edited_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=COMM_NOT_FOUND)
    return edited_rate


# --------------------------------------------
# DELETE RATING
# --------------------------------------------
@router.delete(
    "/delete/{rate_id}",
    response_model=RatingModel,
    dependencies=[Depends(allowed_remove_ratings)]
)
async def delete_rate(
    rate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Видаляє рейтинг за ID.

    - **rate_id**: ID рейтингу для видалення
    """
    deleted_rate = await repository_ratings.delete_rate(rate_id, db, current_user)
    if deleted_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_RATING)
    return deleted_rate


# --------------------------------------------
# GET ALL RATINGS
# --------------------------------------------
@router.get(
    "/all",
    response_model=List[RatingModel],
    dependencies=[Depends(allowed_get_all_ratings)]
)
async def all_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Повертає всі рейтинги (для admin/moder).
    """
    ratings = await repository_ratings.show_ratings(db, current_user)
    if not ratings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_RATING)
    return ratings


# --------------------------------------------
# GET MY RATINGS
# --------------------------------------------
@router.get(
    "/all_my",
    response_model=List[RatingModel],
    dependencies=[Depends(allowed_commented_by_user)]
)
async def all_my_rates(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Повертає всі рейтинги поточного користувача.
    """
    ratings = await repository_ratings.show_my_ratings(db, current_user)
    if not ratings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_RATING)
    return ratings


# --------------------------------------------
# GET RATING OF SPECIFIC USER FOR POST
# --------------------------------------------
@router.get(
    "/user_post/{user_id}/{post_id}",
    response_model=RatingModel,
    dependencies=[Depends(allowed_user_post_rate)]
)
async def user_rate_post(
    user_id: int,
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Повертає рейтинг користувача для конкретного поста.

    - **user_id**: ID користувача
    - **post_id**: ID поста
    """
    rate = await repository_ratings.user_rate_post(user_id, post_id, db, current_user)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return rate
