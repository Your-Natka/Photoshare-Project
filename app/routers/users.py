from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.connect_db import get_db
from app.database.models import User, UserRoleEnum
from app.schemas import PostResponse, UserProfileModel, UserDb, RequestEmail, RequestRole
from app.services.auth import auth_service
from app.services.roles import RoleChecker
from app.repository import users as repository_users
from app.conf.messages import NOT_FOUND, USER_ROLE_EXISTS, INVALID_EMAIL, USER_NOT_ACTIVE, USER_ALREADY_NOT_ACTIVE, USER_CHANGE_ROLE_TO

router = APIRouter(prefix='/users', tags=["users"])

# --------------------------------------------
# ROLE CHECKERS
# --------------------------------------------
allowed_get_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_create_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_get_all_users = RoleChecker([UserRoleEnum.admin])
allowed_remove_user = RoleChecker([UserRoleEnum.admin])
allowed_ban_user = RoleChecker([UserRoleEnum.admin])
allowed_change_user_role = RoleChecker([UserRoleEnum.admin])


# --------------------------------------------
# PROFILE ENDPOINTS
# --------------------------------------------
@router.get("/me/", response_model=UserDb)
async def read_my_profile(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отримати профіль поточного користувача.

    :param current_user: Поточний авторизований користувач
    :param db: Сесія бази даних
    :return: Інформація про користувача у форматі `UserDb`
    """
    user = await repository_users.get_me(current_user, db)
    return user


@router.put("/edit_me/", response_model=UserDb)
async def edit_my_profile(
    avatar: UploadFile = File(...),
    new_username: str = Form(None),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Редагувати профіль поточного користувача (аватар або ім'я).

    :param avatar: Файл нового аватара
    :param new_username: Нове ім'я користувача
    :param current_user: Поточний авторизований користувач
    :param db: Сесія бази даних
    :return: Оновлена інформація про користувача
    """
    updated_user = await repository_users.edit_my_profile(avatar, new_username, current_user, db)
    return updated_user


# --------------------------------------------
# USER MANAGEMENT
# --------------------------------------------
@router.get("/all", response_model=List[UserDb], dependencies=[Depends(allowed_get_all_users)])
def read_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Отримати список всіх користувачів з пагінацією.

    :param skip: Кількість пропущених записів
    :param limit: Максимальна кількість записів
    :param db: Сесія бази даних
    :return: Список користувачів
    """
    users = repository_users.get_users(skip, limit, db)
    return users


@router.get("/users_with_username/{username}", response_model=List[UserDb], dependencies=[Depends(allowed_get_user)])
async def read_users_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Отримати користувачів за username.

    :param username: Ім'я користувача
    :param db: Сесія бази даних
    :param current_user: Поточний авторизований користувач
    :return: Список користувачів
    """
    users = await repository_users.get_users_with_username(username, db)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return users


@router.get("/user_profile_with_username/{username}", response_model=UserProfileModel, dependencies=[Depends(allowed_get_user)])
async def read_user_profile_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Отримати детальний профіль користувача за username.

    :param username: Ім'я користувача
    :param db: Сесія бази даних
    :param current_user: Поточний авторизований користувач
    :return: Профіль користувача
    """
    user_profile = await repository_users.get_user_profile(username, db)
    if user_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return user_profile


# --------------------------------------------
# POSTS BY USER
# --------------------------------------------
@router.get("/commented_posts_by_me/", response_model=List[PostResponse])
async def read_commented_posts_by_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Отримати всі пости, які коментував поточний користувач.

    :param db: Сесія бази даних
    :param current_user: Поточний авторизований користувач
    :return: Список постів
    """
    posts = await repository_users.get_all_commented_posts(current_user, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/rated_posts_by_me/", response_model=List[PostResponse])
async def read_liked_posts_by_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Отримати всі пости, які лайкнув поточний користувач.

    :param db: Сесія бази даних
    :param current_user: Поточний авторизований користувач
    :return: Список постів
    """
    posts = await repository_users.get_all_liked_posts(current_user, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


# --------------------------------------------
# ADMIN ACTIONS
# --------------------------------------------
@router.patch("/ban/{email}/", dependencies=[Depends(allowed_ban_user)])
async def ban_user_by_email(body: RequestEmail, db: Session = Depends(get_db)):
    """
    Заблокувати користувача за email.

    :param body: Об'єкт з email користувача
    :param db: Сесія бази даних
    :return: Повідомлення про статус блокування
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if user.is_active:
        await repository_users.ban_user(user.email, db)
        return {"message": USER_NOT_ACTIVE}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_NOT_ACTIVE)


@router.patch("/make_role/{email}/", dependencies=[Depends(allowed_change_user_role)])
async def make_role_by_email(body: RequestRole, db: Session = Depends(get_db)):
    """
    Змінити роль користувача за email.

    :param body: Об'єкт з email користувача та новою роллю
    :param db: Сесія бази даних
    :return: Повідомлення про успішну зміну ролі
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if body.role == user.role:
        return {"message": USER_ROLE_EXISTS}
    else:
        await repository_users.make_user_role(body.email, body.role, db)
        return {"message": f"{USER_CHANGE_ROLE_TO} {body.role.value}"}