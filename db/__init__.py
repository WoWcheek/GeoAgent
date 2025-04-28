from db.repositories import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('mssql+pyodbc://localhost/geo_agent?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
Session = sessionmaker(bind=engine)
session = Session()

image_repo = ImageRepository()
game_repo = GameRepository(session)
guess_repo = GuessRepository(session)
round_repo = RoundRepository(session)
model_repo = ModelRepository(session)
vendor_repo = VendorRepository(session)