from models import Round
from typing import Optional
from sqlalchemy.orm.session import Session

class RoundRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_round(self, round: Round) -> Round:
        self.session.add(round)
        self.session.commit()
        return round

    def get_round(self, round_id: int) -> Optional[Round]:
        return self.session.query(Round).filter(Round.id == round_id).first()