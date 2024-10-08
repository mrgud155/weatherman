import os

from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from asyncio import run

from sqlmodel import SQLModel
from src.weatherman.db import engine
from src.weatherman.ormodels import Location, CurrentWeather, Condition, Forecast
from src.weatherman.collector.weatherapi import WeatherApi


# TODO: remove imports and pick location from config file
from constants import LOCATION
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.StreamHandler()],
)


async def main():
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    key = os.getenv("WEATHER_API_KEY")
    weather = WeatherApi(key)
    logging.debug("Creating tables")
    SQLModel.metadata.create_all(engine)
    async with AsyncScheduler() as scheduler:
        await scheduler.add_schedule(
            weather.fetch_and_save_weather,
            args=[LOCATION, "forecast"],
            trigger=IntervalTrigger(seconds=60),
        )
        await scheduler.run_until_stopped()


run(main())
