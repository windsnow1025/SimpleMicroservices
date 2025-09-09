from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from .conversation import ConversationRead

user_id_counter = 1

def get_next_user_id():
    global user_id_counter
    user_id_counter += 1
    return user_id_counter

class UserBase(BaseModel):
    username: str = Field(
        ...,
        description="User's username.",
        json_schema_extra={"example": "johndoe"},
    )
    email: str = Field(
        ...,
        description="User's email address.",
        json_schema_extra={"example": "john.doe@example.com"},
    )

class UserCreate(UserBase):
    password: str = Field(
        ...,
        description="User's password.",
        json_schema_extra={"example": "a-secure-password"},
    )

class UserUpdate(UserCreate):
    pass

class UserRead(UserBase):
    id: int = Field(
        description="Unique identifier for the user.",
        json_schema_extra={"example": 1},
    )
    conversations: List[ConversationRead] = Field(
        default_factory=list,
        description="A list of conversations for the user.",
    )
