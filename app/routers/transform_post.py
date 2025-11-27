from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session

from app.conf.messages import NOT_FOUND
from app.database.connect_db import get_db
from app.database.models import User
from app.schemas import PostResponse
from app.tramsform_schemas import TransformBodyModel
from app.services.auth import auth_service
from app.repository import transform_post as repository_transform_post

router = APIRouter(prefix='/transformations', tags=["transformations"])


# --------------------------------------------
# TRANSFORM POST
# --------------------------------------------
@router.patch("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def transform_method(
    post_id: int,
    body: TransformBodyModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Виконує трансформацію поста за вказаним `post_id` та даними з body.

    - **post_id**: ID поста, який потрібно трансформувати
    - **body**: Тіло запиту з параметрами трансформації
    - **db**: Сесія бази даних
    - **current_user**: Поточний авторизований користувач

    Повертає трансформований пост у форматі `PostResponse`.
    """
    post = await repository_transform_post.transform_metod(post_id, body, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post


# --------------------------------------------
# SHOW QR CODE
# --------------------------------------------
@router.post("/qr/{post_id}", status_code=status.HTTP_200_OK)
async def show_qr(
    post_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Генерує та повертає QR-код для вказаного поста.

    - **post_id**: ID поста
    - **request**: Об'єкт запиту FastAPI
    - **db**: Сесія бази даних
    - **current_user**: Поточний авторизований користувач

    Повертає пост з QR-кодом або викликає 404, якщо пост не знайдено.
    """
    post = await repository_transform_post.show_qr(post_id, current_user, db, request)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post
