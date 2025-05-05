from ..models import Round
from sqlalchemy.orm.session import Session

class RoundRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_round(self, round: Round) -> Round:
        self.session.add(round)
        self.session.commit()
        return round