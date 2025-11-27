from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.database.connect_db import get_db
from app.schemas import HashtagBase, HashtagResponse
from app.repository import hashtags as repository_tags
from app.services.roles import RoleChecker
from app.database.models import User, UserRoleEnum
from app.services.auth import auth_service
from app.conf.messages import NOT_FOUND

router = APIRouter(prefix='/hashtags', tags=["hashtags"])

# ---------------- Ролі ---------------- #
allowed_get_all_hashtags = RoleChecker([UserRoleEnum.admin])
allowed_remove_hashtag = RoleChecker([UserRoleEnum.admin])
allowed_edit_hashtag = RoleChecker([UserRoleEnum.admin])

# ---------------- CRUD для хештегів ---------------- #

@router.post("/new/", response_model=HashtagResponse)
async def create_tag(body: HashtagBase, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Створення нового хештегу.
    - Доступно будь-якому автентифікованому користувачу
    """
    return await repository_tags.create_tag(body, current_user, db)


@router.get("/my/", response_model=List[HashtagResponse])
async def read_my_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Повертає хештеги, створені поточним користувачем.
    - `skip` і `limit` для пагінації
    """
    tags = await repository_tags.get_my_tags(skip, limit, current_user, db)
    return tags


@router.get("/all/", response_model=List[HashtagResponse], dependencies=[Depends(allowed_get_all_hashtags)])
async def read_all_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Повертає всі хештеги (тільки для admin).
    """
    tags = await repository_tags.get_all_tags(skip, limit, db)
    return tags


@router.get("/by_id/{tag_id}", response_model=HashtagResponse)
async def read_tag_by_id(tag_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Повертає хештег за його ID.
    """
    tag = await repository_tags.get_tag_by_id(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return tag


@router.put("/upd_tag/{tag_id}", response_model=HashtagResponse, dependencies=[Depends(allowed_edit_hashtag)])
async def update_tag(body: HashtagBase, tag_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Оновлення хештегу (тільки для admin).
    """
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return tag


@router.delete("/del/{tag_id}", response_model=HashtagResponse, dependencies=[Depends(allowed_remove_hashtag)])
async def remove_tag(tag_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(auth_service.get_current_user)):
    """
    Видалення хештегу (тільки для admin).
    """
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return tag
