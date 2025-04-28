from ..models import Vendor
from sqlalchemy.orm.session import Session

class VendorRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_vendor_if_not_exists(self, vendor: Vendor) -> Vendor:
        existing_vendor = self.session.query(Vendor).filter_by(name=vendor.name).first()
        if existing_vendor:
            return existing_vendor

        self.session.add(vendor)
        self.session.commit()
        return vendor