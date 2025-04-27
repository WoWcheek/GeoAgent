from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey

class Round(Base):
    __tablename__ = 'Rounds'
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_token = Column(String(100), ForeignKey('Games.token'), nullable=False)
    round_number = Column(Integer, nullable=False)
    true_latitude = Column(Float)
    true_longitude = Column(Float)
    panorama_id = Column(String(255))
    country_code = Column(String(2))
    predicted_latitude = Column(Float)
    predicted_longitude = Column(Float)
    score = Column(Float)
    distance_km = Column(Float)
    seconds_spent = Column(Integer)
    reasoning = Column(String, nullable=True)
    round_image_url = Column(String(512), nullable=True)
    aggregated_latitude = Column(Float)
    aggregated_longitude = Column(Float)

    game = relationship('Game', back_populates='rounds')

Round.guesses = relationship('Guess', back_populates='round')