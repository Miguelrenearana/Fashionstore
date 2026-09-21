from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.models.user import Employee
from app.schemas.reception import ReceptionCreate, ReceptionFullRead
from app.services.reception_service import reception_service

router = APIRouter(prefix="/receptions", tags=["receptions"])

branch_manager = require_roles("ADMIN", "MANAGER", "BRANCH_MANAGER")


@router.post("", response_model=ReceptionFullRead, dependencies=[Depends(branch_manager)])
def create_reception(db: DbSession, payload: ReceptionCreate, current: CurrentUser):
    employee = db.query(Employee).filter(Employee.user_id == current.id).first()
    payload.employee_id = employee.id if employee else None
    return reception_service.create(db, payload)


@router.get("/{reception_id}", response_model=ReceptionFullRead)
def get_reception(db: DbSession, reception_id: int, current: CurrentUser):
    return reception_service.get(db, reception_id)
