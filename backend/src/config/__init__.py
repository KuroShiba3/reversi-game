import os

from dotenv import load_dotenv

load_dotenv(override=True)

POSTGRES_URL = os.getenv("POSTGRES_URL")