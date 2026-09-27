from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, NotFoundError
from app.models.user import Branch, City
from app.schemas.location import BranchCreate, BranchUpdate, CityCreate, CityUpdate


class LocationService:
    def list_cities(self, db: Session):
        return db.query(City).order_by(City.name).all()

    def list_branches(self, db: Session, include_inactive: bool = False):
        query = db.query(Branch).options(joinedload(Branch.city))
        if not include_inactive:
            query = query.filter(Branch.is_active)
        return query.order_by(Branch.name).all()

    def create_branch(self, db: Session, payload: BranchCreate) -> Branch:
        if not db.get(City, payload.city_id):
            raise NotFoundError("City not found.")
        if db.query(Branch).filter(Branch.name == payload.name).first():
            raise ConflictError("La sucursal ya se encuentra registrada.")
        branch = Branch(
            city_id=payload.city_id,
            name=payload.name,
            address=payload.address,
            phone=payload.phone,
        )
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch

    def update_branch(self, db: Session, branch_id: int, payload: BranchUpdate) -> Branch:
        branch = db.get(Branch, branch_id)
        if not branch:
            raise NotFoundError("Sucursal no encontrada.")

        data = payload.model_dump(exclude_unset=True)
        if data.get("city_id") and not db.get(City, data["city_id"]):
            raise NotFoundError("City not found.")
        if data.get("name") and data["name"] != branch.name:
            if db.query(Branch).filter(Branch.name == data["name"]).first():
                raise ConflictError("La sucursal ya se encuentra registrada.")

        for field, value in data.items():
            setattr(branch, field, value)

        db.commit()
        db.refresh(branch)
        return branch

    # CU-06: ciudades multi-ciudad

    def create_city(self, db: Session, payload: CityCreate) -> City:
        if db.query(City).filter(City.name == payload.name).first():
            raise ConflictError("La ciudad ya se encuentra registrada.")
        city = City(name=payload.name, state=payload.state)
        db.add(city)
        db.commit()
        db.refresh(city)
        return city

    def update_city(self, db: Session, city_id: int, payload: CityUpdate) -> City:
        city = db.get(City, city_id)
        if not city:
            raise NotFoundError("Ciudad no encontrada.")

        data = payload.model_dump(exclude_unset=True)
        if data.get("name") and data["name"] != city.name:
            if db.query(City).filter(City.name == data["name"]).first():
                raise ConflictError("La ciudad ya se encuentra registrada.")

        for field, value in data.items():
            setattr(city, field, value)

        db.commit()
        db.refresh(city)
        return city


location_service = LocationService()
