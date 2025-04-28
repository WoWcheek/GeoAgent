from ..models import Model
from sqlalchemy.orm.session import Session

class ModelRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_model_if_not_exists(self, model: Model) -> Model:
        existing_model = self.session.query(Model).filter_by(model_name=model.model_name, vendor_id=model.vendor_id).first()
        if existing_model:
            return existing_model

        self.session.add(model)
        self.session.commit()
        return model