from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .game import Game
from .round import Round
from .model import Model
from .guess import Guess
from .vendor import Vendor