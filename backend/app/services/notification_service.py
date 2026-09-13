import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.analytics import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Persist notifications. Email/SMS is log-only until Ciclo 2 (SendGrid/Mailgun)."""

    def notify(
        self,
        db: Session,
        user_id: int,
        type: str,
        title: str,
        body: str,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        logger.info(f"[email-mock] to={settings.mail_from} subject={title} body={body}")
        return notification


notification_service = NotificationService()
