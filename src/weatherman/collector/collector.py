import os

from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger

from asyncio import run
from weatherapi import WeatherApi

# TODO: remove imports and pick location from config file
from constants import LOCATION


async def main():
    key = os.getenv("WEATHER_API_KEY")
    weather = WeatherApi(key)
    async with AsyncScheduler() as scheduler:
        await scheduler.add_schedule(
            weather.get_weather,
            args=[LOCATION, "current"],
            trigger=IntervalTrigger(seconds=30),
        )
        await scheduler.run_until_stopped()


run(main())
