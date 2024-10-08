from os import getenv, getcwd

from sqlalchemy.exc import IntegrityError
from sqlmodel import create_engine
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
db_url = getenv("DATABASE_URL")
logger.debug(f"Current workdir is {getcwd()}")
logger.debug(f"Connecting to database at {db_url}")
engine = create_engine(db_url)


def save_to_db(data, db):
    try:
        db.add(data)
        db.commit()
        logger.debug(f"Data added to database")
    except IntegrityError as e:
        logging.debug(
            f"Failed to save data to database, row violates data integrity: {e}"
        )
        db.rollback()
        raise e
