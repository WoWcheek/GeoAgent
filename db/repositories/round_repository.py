from ..models import Round
from sqlalchemy.orm.session import Session

class RoundRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_round(self, round: Round) -> Round:
        self.session.add(round)
        self.session.commit()
        return round

    def update_round(self, round: Round) -> Round:
        db_round = self.session.query(Round).filter_by(id=round.id).one()

        db_round.game_token = round.game_token
        db_round.round_number = round.round_number
        db_round.true_latitude = round.true_latitude
        db_round.true_longitude = round.true_longitude
        db_round.panorama_id = round.panorama_id
        db_round.country_code = round.country_code
        db_round.round_image_url = round.round_image_url

        db_round.score = round.score
        db_round.distance_km = round.distance_km
        db_round.aggregated_latitude = round.aggregated_latitude
        db_round.aggregated_longitude = round.aggregated_longitude

        self.session.commit()
        return db_round