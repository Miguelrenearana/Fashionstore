from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.analytics import Notification
from app.schemas.notification import NotificationRead

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
def my_notifications(
    db: DbSession,
    current: CurrentUser,
    unread_only: bool = False,
    limit: int = Query(50, ge=1, le=200),
):
    query = db.query(Notification).filter(Notification.user_id == current.id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.order_by(Notification.id.desc()).limit(limit).all()


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_read(db: DbSession, notification_id: int, current: CurrentUser):
    notification = db.get(Notification, notification_id)
    if not notification:
        raise NotFoundError("Notification not found.")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
