from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.user import Branch, City
from app.schemas.location import BranchCreate


class LocationService:
    def list_cities(self, db: Session):
        return db.query(City).order_by(City.name).all()

    def list_branches(self, db: Session):
        return db.query(Branch).filter(Branch.is_active).order_by(Branch.name).all()

    def create_branch(self, db: Session, payload: BranchCreate) -> Branch:
        if not db.get(City, payload.city_id):
            raise NotFoundError("City not found.")
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


location_service = LocationService()
