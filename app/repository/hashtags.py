"""
hashtags.py — функції для роботи з хештегами у PhotoShare API.

Містить CRUD-операції та методи для отримання тегів користувачів і загальних тегів.
"""

from typing import List
from sqlalchemy.orm import Session
from app.database.models import Hashtag, User
from app.schemas import HashtagBase


async def create_tag(body: HashtagBase, user: User, db: Session) -> Hashtag:
    """
    Створює новий хештег або повертає існуючий, якщо він вже є.

    :param body: Об'єкт HashtagBase з назвою хештегу
    :param user: Поточний користувач, що створює тег
    :param db: SQLAlchemy сесія
    :return: Об'єкт Hashtag
    """
    tag = db.query(Hashtag).filter(Hashtag.title == body.title).first()
    if not tag:
        tag = Hashtag(
            title=body.title,
            user_id=user.id,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag


async def get_my_tags(skip: int, limit: int, user: User, db: Session) -> List[Hashtag]:
    """
    Повертає список хештегів, створених поточним користувачем.

    :param skip: Кількість тегів, що пропускаються (для пагінації)
    :param limit: Максимальна кількість тегів, що повертається
    :param user: Поточний користувач
    :param db: SQLAlchemy сесія
    :return: Список об'єктів Hashtag
    """
    return db.query(Hashtag).filter(Hashtag.user_id == user.id).offset(skip).limit(limit).all()


async def get_all_tags(skip: int, limit: int, db: Session) -> List[Hashtag]:
    """
    Повертає список усіх тегів у системі.

    :param skip: Кількість тегів, що пропускаються (для пагінації)
    :param limit: Максимальна кількість тегів, що повертається
    :param db: SQLAlchemy сесія
    :return: Список об'єктів Hashtag
    """
    return db.query(Hashtag).offset(skip).limit(limit).all()
    # return db.tags[skip: skip + limit]   # <---- так не працює 
    


async def get_tag_by_id(tag_id: int, db: Session) -> Hashtag:
    """
    Повертає конкретний хештег за його ID.

    :param tag_id: ID тегу
    :param db: SQLAlchemy сесія
    :return: Об'єкт Hashtag або None, якщо тег не знайдено
    """
    return db.query(Hashtag).filter(Hashtag.id == tag_id).first()


async def update_tag(tag_id: int, body: HashtagBase, db: Session) -> Hashtag | None:
    """
    Оновлює назву хештегу за його ID.

    :param tag_id: ID тегу для оновлення
    :param body: Об'єкт HashtagBase з новою назвою
    :param db: SQLAlchemy сесія
    :return: Оновлений об'єкт Hashtag або None, якщо тег не знайдено
    """
    tag = db.query(Hashtag).filter(Hashtag.id == tag_id).first()
    if tag:
        tag.title = body.title
        db.commit()
    return tag


async def remove_tag(tag_id: int, db: Session) -> Hashtag | None:
    """
    Видаляє хештег за його ID.

    :param tag_id: ID тегу для видалення
    :param db: SQLAlchemy сесія
    :return: Видалений об'єкт Hashtag або None, якщо тег не знайдено
    """
    tag = db.query(Hashtag).filter(Hashtag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag
