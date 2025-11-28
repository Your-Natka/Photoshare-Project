"""
users.py — функції для роботи з користувачами та чорним списком токенів.

Містить:
- CRUD для користувачів
- Управління аватарками через Cloudinary
- Робота з ролями, блокуванням та підтвердженням email
- Робота з чорним списком JWT токенів
"""

from datetime import datetime
from typing import List, Optional

import cloudinary
import cloudinary.uploader
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.conf.config import init_cloudinary
from app.database.models import User, UserRoleEnum, Comment, Rating, Post, BlacklistToken
from app.schemas import UserModel, UserProfileModel


# ---------------- USER CRUD ---------------- #

async def get_me(user: User, db: Session) -> User:
    """
    Повертає об'єкт поточного користувача.

    :param user: Поточний користувач
    :param db: SQLAlchemy сесія
    :return: Об'єкт User
    """
    return db.query(User).filter(User.id == user.id).first()


async def edit_my_profile(file, new_username: Optional[str], user: User, db: Session) -> User:
    """
    Редагує профіль користувача, оновлює username та аватарку через Cloudinary.

    :param file: Нове зображення аватарки
    :param new_username: Нове ім'я користувача
    :param user: Поточний користувач
    :param db: SQLAlchemy сесія
    :return: Оновлений об'єкт User
    """
    me = db.query(User).filter(User.id == user.id).first()
    if new_username:
        me.username = new_username

    if file:
        init_cloudinary()
        cloudinary.uploader.upload(
            file.file,
            public_id=f'Photoshare/{me.username}',
            overwrite=True,
            invalidate=True
        )
        url = cloudinary.CloudinaryImage(f'Photoshare/{me.username}').build_url(width=250, height=250, crop='fill')
        me.avatar = url

    db.commit()
    db.refresh(me)
    return me


def get_users(skip: int, limit: int, db: Session) -> List[User]:
    """
    Повертає список користувачів з пагінацією.

    :param skip: Кількість пропущених записів
    :param limit: Ліміт на кількість записів
    :param db: SQLAlchemy сесія
    :return: Список користувачів
    """
    return db.query(User).offset(skip).limit(limit).all()


async def get_users_with_username(username: str, db: Session) -> List[User]:
    """
    Повертає користувачів за частковим збігом username.

    :param username: Частина username для пошуку
    :param db: SQLAlchemy сесія
    :return: Список користувачів
    """
    return db.query(User).filter(func.lower(User.username).like(f'%{username.lower()}%')).all()


async def get_user_profile(username: str, db: Session) -> Optional[UserProfileModel]:
    """
    Повертає профіль користувача з підрахунком постів, коментарів та оцінок.

    :param username: username користувача
    :param db: SQLAlchemy сесія
    :return: UserProfileModel або None, якщо користувач не знайдений
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None

    post_count = db.query(Post).filter(Post.user_id == user.id).count()
    comment_count = db.query(Comment).filter(Comment.user_id == user.id).count()
    rates_count = db.query(Rating).filter(Rating.user_id == user.id).count()

    return UserProfileModel(
        username=user.username,
        email=user.email,
        avatar=user.avatar,
        created_at=user.created_at,
        is_active=user.is_active,
        post_count=post_count,
        comment_count=comment_count,
        rates_count=rates_count
    )


async def get_all_commented_posts(user: User, db: Session) -> List[Post]:
    """
    Повертає всі пости, де користувач залишав коментарі.

    :param user: Поточний користувач
    :param db: SQLAlchemy сесія
    :return: Список постів
    """
    return db.query(Post).join(Comment).filter(Comment.user_id == user.id).all()


async def get_all_liked_posts(user: User, db: Session) -> List[Post]:
    """
    Повертає всі пости, які користувач оцінив.

    :param user: Поточний користувач
    :param db: SQLAlchemy сесія
    :return: Список постів
    """
    return db.query(Post).join(Rating).filter(Rating.user_id == user.id).all()


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """
    Повертає користувача за email.

    :param email: Email користувача
    :param db: SQLAlchemy сесія
    :return: Об'єкт User або None
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Створює нового користувача. Перший користувач отримує роль admin.

    :param body: UserModel — дані користувача
    :param db: SQLAlchemy сесія
    :return: Створений користувач
    """
    new_user = User(**body.dict())
    if db.query(User).count() == 0:  # First user is admin
        new_user.role = UserRoleEnum.admin
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: Optional[str], db: Session) -> None:
    """
    Оновлює refresh_token користувача.

    :param user: Поточний користувач
    :param token: Новий refresh_token
    :param db: SQLAlchemy сесія
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Позначає email користувача як підтверджений.

    :param email: Email користувача
    :param db: SQLAlchemy сесія
    """
    user = await get_user_by_email(email, db)
    if user:
        user.is_verify = True
        db.commit()


async def ban_user(email: str, db: Session) -> None:
    """
    Блокує користувача (is_active = False).

    :param email: Email користувача
    :param db: SQLAlchemy сесія
    """
    user = await get_user_by_email(email, db)
    if user:
        user.is_active = False
        db.commit()


async def make_user_role(email: str, role: UserRoleEnum, db: Session) -> None:
    """
    Змінює роль користувача.

    :param email: Email користувача
    :param role: Нова роль користувача
    :param db: SQLAlchemy сесія
    """
    user = await get_user_by_email(email, db)
    if user:
        user.role = role
        db.commit()


# ---------------- BLACKLIST ---------------- #

async def add_to_blacklist(token: str, db: Session) -> None:
    """
    Додає токен у чорний список.

    :param token: JWT токен
    :param db: SQLAlchemy сесія
    """
    if not await find_blacklisted_token(token, db):
        blacklist_token = BlacklistToken(token=token, blacklisted_on=datetime.utcnow())
        db.add(blacklist_token)
        db.commit()


async def find_blacklisted_token(token: str, db: Session) -> Optional[BlacklistToken]:
    """
    Перевіряє наявність токена у чорному списку.

    :param token: JWT токен
    :param db: SQLAlchemy сесія
    :return: BlacklistToken або None
    """
    return db.query(BlacklistToken).filter(BlacklistToken.token == token).first()


async def remove_from_blacklist(token: str, db: Session) -> None:
    """
    Видаляє токен з чорного списку.

    :param token: JWT токен
    :param db: SQLAlchemy сесія
    """
    blacklist_token = await find_blacklisted_token(token, db)
    if blacklist_token:
        db.delete(blacklist_token)
        db.commit()
        
async def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    """
    Повертає користувача за ID.
    """
    return db.query(User).filter(User.id == user_id).first()


async def delete_user(user_id: int, db: Session) -> None:
    """
    Видаляє користувача за ID.
    """
    user = await get_user_by_id(user_id, db)
    if user:
        db.delete(user)
        db.commit()
