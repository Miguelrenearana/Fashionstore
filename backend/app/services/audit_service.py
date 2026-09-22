import json
from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.analytics import AuditLog
from app.models.user import User


class AuditService:
    """Servicio de bitácora y trazabilidad (CU-34)."""

    def __init__(self, db: Session):
        self.db = db

    def log_action(
        self,
        action: str,
        entity: str,
        entity_id: int | None = None,
        user_id: int | None = None,
        metadata: dict | None = None,
    ):
        """Registrar acción en bitácora."""
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        self.db.add(log)
        self.db.commit()

    def get_audit_log(
        self,
        page: int = 1,
        size: int = 20,
        user_id: int | None = None,
        action: str | None = None,
        entity: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> tuple[list[dict], int]:
        """Obtener bitácora con filtros."""
        query = self.db.query(AuditLog)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if entity:
            query = query.filter(AuditLog.entity == entity)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        total = query.count()
        logs = query.order_by(desc(AuditLog.created_at)).offset((page - 1) * size).limit(size).all()

        items_list = []
        for log in logs:
            user = self.db.get(User, log.user_id) if log.user_id else None
            items_list.append(
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "user_email": user.email if user else None,
                    "action": log.action,
                    "entity": log.entity,
                    "entity_id": log.entity_id,
                    "metadata_json": log.metadata_json,
                    "created_at": log.created_at,
                }
            )

        return items_list, total


def get_audit_service(db: Session) -> AuditService:
    return AuditService(db)
