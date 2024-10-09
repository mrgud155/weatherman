import os

from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from asyncio import run

from sqlalchemy import inspect
from sqlmodel import SQLModel
from src.weatherman.db import engine
from src.weatherman.ormodels import Location, CurrentWeather, Condition, Forecast
from src.weatherman.collector.weatherapi import WeatherApi


# TODO: remove imports and pick location from config file
from constants import LOCATIONS
import logging

loglevel = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=logging.getLevelName(loglevel),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.StreamHandler()],
)


async def validate_configuration_line(location, interval):
    if not isinstance(location, str):
        return False
    if not interval.isdigit():
        return False
    return True


async def main():
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())

    # Check if API key is present
    key = os.getenv("WEATHER_API_KEY")
    if not key:
        logger.error("No API key found. Exiting.")
        exit(1)
    weather = WeatherApi(key)

    # Check if tables are present and create them if not
    logging.debug("Checking if tables are present and creating tables")
    if not inspect(engine).has_table(engine, "location"):
        SQLModel.metadata.create_all(engine)

    # Get list of locations to fetch weather for
    input_file = os.getenv("LOCATION_FILE", None)
    if input_file:
        with open(input_file, "r") as f:
            locations = f.readlines()
    else:
        locations = LOCATIONS

    async with AsyncScheduler() as scheduler:
        for item in locations:
            location, interval_minutes = item.strip().split(",")
            if not validate_configuration_line(location, interval_minutes):
                logger.error(f"Invalid configuration line: {item}")
                continue
            logger.info(
                f"Adding schedule for {location}, with interval {interval_minutes} minutes"
            )
            await scheduler.add_schedule(
                weather.fetch_and_save_weather,
                args=[location, "forecast"],
                trigger=IntervalTrigger(minutes=int(interval_minutes)),
            )
        await scheduler.run_until_stopped()


run(main())
