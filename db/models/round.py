from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey

class Round(Base):
    __tablename__ = 'Rounds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_token = Column(String(100), ForeignKey('Games.token'), nullable=False)
    round_number = Column(Integer, nullable=False)
    panorama_id = Column(String(255))
    image_url = Column(String(512))
    true_latitude = Column(Float, nullable=False)
    true_longitude = Column(Float, nullable=False)
    true_country_code = Column(String(2), nullable=False)
    aggregated_latitude = Column(Float, nullable=False)
    aggregated_longitude = Column(Float, nullable=False)
    aggregated_country_code = Column(String(2))
    score = Column(Integer, nullable=False)
    distance_km = Column(Float, nullable=False)

    game = relationship('Game', back_populates='rounds')

Round.guesses = relationship('Guess', back_populates='round')