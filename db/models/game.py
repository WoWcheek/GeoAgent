from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float

class Game(Base):
    __tablename__ = 'Games'
    token = Column(String(100), primary_key=True)
    map = Column(String(100))
    rounds_count = Column(Integer)
    total_score = Column(Integer)
    total_distance_km = Column(Float)
    player_id = Column(String(100))

Game.rounds = relationship('Round', back_populates='game')