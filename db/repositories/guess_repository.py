from models import Guess
from typing import Optional
from sqlalchemy.orm.session import Session

class GuessRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_guess(self, guess: Guess) -> Guess:
        self.session.add(guess)
        self.session.commit()
        return guess

    def get_guess(self, guess_id: int) -> Optional[Guess]:
        return self.session.query(Guess).filter(Guess.id == guess_id).first()