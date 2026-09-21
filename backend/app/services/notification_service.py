import logging
import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.analytics import Notification
from app.models.user import User

logger = logging.getLogger(__name__)


class NotificationService:
    """Persist notifications. Sends a real email when SMTP is configured
    (Gmail App Password / any SMTP relay); falls back to a log-only mock."""

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

        user = db.get(User, user_id)
        recipient = user.email if user else None
        if recipient and settings.smtp_password:
            self._send_email(recipient=recipient, subject=title, body=body)
        else:
            logger.info(
                "[email-mock] to=%s subject=%s body=%s",
                recipient or settings.mail_from,
                title,
                body,
            )
        return notification

    def _send_email(self, recipient: str, subject: str, body: str) -> None:
        """Send via SMTP (starttls) using the configured Gmail/app-specific account."""
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.mail_from or settings.smtp_user
        msg["To"] = recipient
        msg.set_content(body)

        host = settings.smtp_host or "smtp.gmail.com"
        port = settings.smtp_port or 587
        try:
            with smtplib.SMTP(host, port, timeout=15) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(msg)
            logger.info("[email-sent] to=%s via=%s:%s", recipient, host, port)
        except Exception:
            logger.exception("[email-failed] to=%s", recipient)


notification_service = NotificationService()
