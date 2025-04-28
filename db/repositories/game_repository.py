from ..models.game import Game
from sqlalchemy.orm.session import Session

class GameRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_game(self, game: Game) -> Game:
        self.session.add(game)
        self.session.commit()
        return game

    def update_game(self, game: Game) -> Game:
        db_game = self.session.query(Game).filter_by(token=game.token).one()

        db_game.map = game.map
        db_game.player_id = game.player_id
        
        db_game.rounds_count = game.rounds_count
        db_game.total_score = game.total_score
        db_game.total_distance_km = game.total_distance_km

        self.session.commit()
        return db_game