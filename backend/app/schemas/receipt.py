from datetime import datetime

from app.schemas.common import ORMModel


class ReceiptRead(ORMModel):
    id: int
    sale_id: int
    type: str
    rnc_or_cuf: str | None = None
    document_url: str | None = None
    created_at: datetime
