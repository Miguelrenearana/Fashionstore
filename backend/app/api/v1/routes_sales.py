from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.models.user import Employee
from app.schemas.sale import SaleGenerate, SaleRead
from app.services.sales_service import sales_service

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("", response_model=SaleRead)
def create_sale(db: DbSession, payload: SaleGenerate, current: CurrentUser):
    employee = db.query(Employee).filter(Employee.user_id == current.id).first()
    return sales_service.create_sale(db, payload, employee_id=employee.id if employee else None)


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(db: DbSession, sale_id: int):
    return sales_service.get(db, sale_id)
