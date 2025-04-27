from models import Game
from typing import Optional
from sqlalchemy.orm.session import Session

class GameRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_game(self, game: Game) -> Game:
        self.session.add(game)
        self.session.commit()
        return game

    def get_game(self, token: str) -> Optional[Game]:
        return self.session.query(Game).filter(Game.token == token).first()