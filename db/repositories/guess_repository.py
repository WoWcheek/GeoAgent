from ..models import Guess
from sqlalchemy.orm.session import Session

class GuessRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_guess(self, guess: Guess) -> Guess:
        self.session.add(guess)
        self.session.commit()
        return guess