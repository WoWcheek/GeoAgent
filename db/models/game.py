from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Float, String, Column, Integer, DateTime

class Game(Base):
    __tablename__ = 'Games'
    token = Column(String(100), primary_key=True)
    map = Column(String(100), nullable=False)
    max_distance_km = Column(Float, nullable=False)
    rounds_count = Column(Integer)
    total_score = Column(Integer)
    total_distance_km = Column(Float)
    start_datetime_utc = Column(DateTime)
    player_id = Column(String(100))

Game.rounds = relationship('Round', back_populates='game')