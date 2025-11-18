from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
from app.database.models import UserRoleEnum


# ------------------- User Models -------------------

class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    email: EmailStr
    password: str = Field(min_length=6, max_length=30)
    avatar: Optional[str] = None
    created_at: Optional[datetime]


class UserUpdateModel(BaseModel):
    username: str = Field(min_length=5, max_length=25)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    avatar: Optional[str]
    role: UserRoleEnum
    created_at: datetime

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class UserProfileModel(BaseModel):
    username: str
    email: EmailStr
    avatar: Optional[str]
    post_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    rates_count: Optional[int] = 0
    is_active: Optional[bool] = True
    created_at: datetime


# ------------------- Auth / Token -------------------

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ------------------- Hashtags -------------------

class HashtagBase(BaseModel):
    title: str = Field(max_length=50)


class HashtagModel(HashtagBase):
    model_config = {"from_attributes": True}


class HashtagResponse(HashtagBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class HashtagsLimited(BaseModel):
    hashtags: List[str] = []

    @field_validator("hashtags")
    def validate_tags(cls, v):
        if len(v or []) > 5:
            raise ValueError("Too many hashtags. Maximum 5 tags allowed.")
        return v



# ------------------- Comments -------------------

class CommentBase(BaseModel):
    text: str = Field(max_length=500)


class CommentModel(CommentBase):
    id: int
    text: str
    user_id: int
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class CommentUpdate(CommentModel):
    update_status: bool = True
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


# ------------------- Ratings -------------------

class RatingBase(BaseModel):
    rate: int


class RatingModel(RatingBase):
    id: int
    created_at: datetime
    post_id: int
    user_id: int

    model_config = {"from_attributes": True}


# ------------------- Posts -------------------

class PostBase(HashtagsLimited):
    id: int
    image_url: Optional[str] = Field(max_length=300, default=None)
    transform_url: Optional[str] = Field(max_length=450, default=None)
    title: str = Field(max_length=45)
    descr: str = Field(max_length=450)
    # id: int
    # image_url: Optional[str] = Field(max_length=300, default=None)
    # transform_url: Optional[str] = Field(max_length=450, default=None)
    # title: str = Field(max_length=45)
    # descr: str = Field(max_length=450)
    # hashtags: List[str] = []

    # @field_validator("hashtags")
    # def validate_tags(cls, v):
    #     if len(v or []) > 5:
    #         raise ValueError("Too many hashtags. Maximum 5 tags allowed.")
    #     return v


class PostModel(PostBase):
    pass


class PostUpdate(HashtagsLimited):
    title: str = Field(max_length=45)
    descr: str = Field(max_length=450)
    # hashtags: List[str] = []


class PostResponse(PostBase):
    hashtags: List[HashtagModel]
    avg_rating: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ------------------- Email / Roles -------------------

class RequestEmail(BaseModel):
    email: EmailStr


class RequestRole(BaseModel):
    email: EmailStr
    role: UserRoleEnum
