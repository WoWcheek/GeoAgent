from models import Vendor
from sqlalchemy.orm.session import Session

class VendorRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_vendor(self, vendor: Vendor) -> Vendor:
        self.session.add(vendor)
        self.session.commit()
        return vendor