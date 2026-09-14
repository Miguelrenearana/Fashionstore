from datetime import date

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class RoleRead(ORMModel):
    id: int
    name: str
    description: str | None = None


class BranchBrief(ORMModel):
    id: int
    name: str


class EmployeeBase(BaseModel):
    first_name: str = Field(min_length=2)
    last_name: str = Field(min_length=2)
    branch_id: int
    hire_date: str | None = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeRead(EmployeeBase, ORMModel):
    id: int
    user_id: int
    branch: BranchBrief | None = None
    hire_date: date | None = None


class UserRead(ORMModel):
    id: int
    email: EmailStr
    phone: str | None = None
    is_active: bool
    is_verified: bool
    roles: list[RoleRead] = []


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    phone: str | None = None
    roles: list[str] = Field(default_factory=list)


class UserUpdate(BaseModel):
    phone: str | None = None
    roles: list[str] | None = None
    is_active: bool | None = None


class SupplierCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=150)
    contact_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None


class SupplierUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=2, max_length=150)
    contact_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    is_active: bool | None = None


class SupplierRead(ORMModel):
    id: int
    company_name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    is_active: bool
