from pydantic import BaseModel

from app.schemas.common import ORMModel


class NotificationRead(ORMModel):
    id: int
    type: str
    title: str
    body: str
    is_read: bool
    created_at: str


class NotificationCreate(BaseModel):
    user_id: int
    type: str
    title: str
    body: str
