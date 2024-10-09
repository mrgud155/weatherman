import logging
import os

from fastapi import FastAPI
from sqlalchemy import inspect

import src.weatherman.api.auth as auth
import src.weatherman.api.weather as weather
from src.weatherman.api.database import Base, weather_engine, engine, get_auth_db
from src.weatherman.api.authschemas import UserSchema

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
app = FastAPI()
app.include_router(auth.router)
app.include_router(weather.router)

# check whether the table structure is present in the database
logger.debug(f"Checking for auth table structure in database: {engine.url}")
if not inspect(engine).has_table(engine, "users"):
    logger.info("Auth tables not found, creating table structure")
    Base.metadata.create_all(engine)

db = next(get_auth_db())
if not db.query(UserSchema).count():
    logger.info("No users found in database, creating default user")
    default_pw = os.getenv("DEFAULT_ADMIN_PASSWORD")
    if default_pw is None:
        logger.error("No default password set, exiting")
        exit(1)
    user = UserSchema(
        username="admin",
        email="admin@azul.com",
        first_name="Admin",
        last_name="User",
        disabled=False,
        hashed_password=auth.get_password_hash(default_pw),
    )
    db.add(user)
    db.commit()

if not inspect(weather_engine).has_table("location"):
    logger.error("Weather tables not found, exiting!")
    exit(1)
