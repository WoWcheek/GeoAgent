from models import Model
from sqlalchemy.orm.session import Session

class ModelRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_model(self, model: Model) -> Model:
        self.session.add(model)
        self.session.commit()
        return model