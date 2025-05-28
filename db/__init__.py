import os
from db.models import *
from db.repositories import *
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
connection_string = os.getenv("DB_CONNECTION_STRING")
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()

image_repo = ImageRepository()
game_repo = GameRepository(session)
guess_repo = GuessRepository(session)
round_repo = RoundRepository(session)
model_repo = ModelRepository(session)
vendor_repo = VendorRepository(session)