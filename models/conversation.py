from __future__ import annotations

from pydantic import BaseModel, Field

conversation_id_counter = 0

def get_next_conversation_id():
    global conversation_id_counter
    conversation_id_counter += 1
    return conversation_id_counter

class ConversationBase(BaseModel):
    name: str = Field(
        ...,
        description="A name for the conversation.",
        json_schema_extra={"example": "Project Alpha Planning"},
    )
    messages: str = Field(
        ...,
        description="Messages in the conversation.",
        json_schema_extra={"example": "Initial discussion about project scope..."},
    )

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(ConversationBase):
    pass

class ConversationRead(ConversationBase):
    id: int = Field(
        description="Unique identifier for the conversation.",
        json_schema_extra={"example": 1},
    )
