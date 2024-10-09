from os import getenv, getcwd
from sqlalchemy import create_engine
import logging

from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

# Initialize authentication database connection
auth_db_url = getenv("AUTH_DATABASE_URL")
if auth_db_url is None:
    logger.error("AUTH_DATABASE_URL environment variable not set")
    exit(1)
engine = create_engine(auth_db_url)
logger.info(f"Connected to authentication DB: {auth_db_url}")
Base = declarative_base()

# Initialize weather database connection
weather_db_url = getenv("DATABASE_URL")
if weather_db_url is None:
    logger.error("DATABASE_URL environment variable not set")
    exit(1)
weather_engine = create_engine(weather_db_url)
logger.info(f"Connected to weather DB: {weather_db_url}")
weather_base = declarative_base()


def get_auth_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


def get_weather_db():
    db = Session(weather_engine)
    try:
        yield db
    finally:
        db.close()
