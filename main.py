from __future__ import annotations

import os
from typing import Dict, List
from fastapi import FastAPI, HTTPException, status

from models.user import (
    UserCreate,
    UserRead,
    UserUpdate,
    get_next_user_id,
)
from models.conversation import (
    ConversationCreate,
    ConversationRead,
    ConversationUpdate,
    get_next_conversation_id,
)

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
users: Dict[int, UserRead] = {}
conversations: Dict[int, ConversationRead] = {}

initial_user = UserRead(
    id=get_next_user_id(),
    username="jdoe",
    email="jdoe@example.com",
    conversations=[]
)
users[initial_user.id] = initial_user

# -----------------------------------------------------------------------------
# FastAPI App Definition
# -----------------------------------------------------------------------------
app = FastAPI(
    title="User/Conversation API",
    description="A simple API to manage users and their conversations.",
    version="1.0.0",
)


# -----------------------------------------------------------------------------
# Root Endpoint
# -----------------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the User/Conversation API. See /docs for details."}


# -----------------------------------------------------------------------------
# User Endpoints
# -----------------------------------------------------------------------------
@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_create: UserCreate):
    new_id = get_next_user_id()
    user_data = user_create.model_dump(exclude={"password"})
    new_user = UserRead(id=new_id, **user_data, conversations=[])

    if any(u.email == new_user.email for u in users.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    users[new_id] = new_user
    return new_user


@app.get("/users", response_model=List[UserRead])
def list_users():
    return list(users.values())


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return users[user_id]


@app.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate):
    if user_id not in users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    original_conversations = users[user_id].conversations
    user_data = user_update.model_dump(exclude={"password"})
    updated_user = UserRead(id=user_id, **user_data, conversations=original_conversations)

    users[user_id] = updated_user
    return updated_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_conv_ids = [conv.id for conv in users[user_id].conversations]
    for conv_id in user_conv_ids:
        if conv_id in conversations:
            del conversations[conv_id]

    del users[user_id]
    return None


# -----------------------------------------------------------------------------
# Conversation Endpoints
# -----------------------------------------------------------------------------
@app.post("/users/{user_id}/conversations", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
def create_conversation_for_user(user_id: int, conversation_create: ConversationCreate):
    if user_id not in users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_id = get_next_conversation_id()
    new_conversation = ConversationRead(id=new_id, **conversation_create.model_dump())

    conversations[new_id] = new_conversation
    users[user_id].conversations.append(new_conversation)

    return new_conversation


@app.get("/users/{user_id}/conversations", response_model=List[ConversationRead])
def list_user_conversations(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return users[user_id].conversations


@app.get("/conversations", response_model=List[ConversationRead])
def list_all_conversations():
    return list(conversations.values())


@app.put("/conversations/{conversation_id}", response_model=ConversationRead)
def update_conversation(conversation_id: int, conversation_update: ConversationUpdate):
    if conversation_id not in conversations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    updated_conversation = ConversationRead(id=conversation_id, **conversation_update.model_dump())
    conversations[conversation_id] = updated_conversation

    for user in users.values():
        for i, conv in enumerate(user.conversations):
            if conv.id == conversation_id:
                user.conversations[i] = updated_conversation
                break

    return updated_conversation


@app.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: int):
    if conversation_id not in conversations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    del conversations[conversation_id]

    for user in users.values():
        user.conversations = [conv for conv in user.conversations if conv.id != conversation_id]

    return None


# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
