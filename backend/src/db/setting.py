from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv(override=True)

engine = create_engine(os.getenv("DATABASE_URL"))