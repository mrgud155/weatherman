import httpx
from sqlalchemy import Select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import Session

import constants
from datetime import datetime
from src.weatherman.ormodels import (
    Location,
    CurrentWeather,
    Condition,
    Forecast,
    Daily,
    Astro,
    Hourly,
)
from src.weatherman.db import engine, save_to_db
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class WeatherApi:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_and_save_weather(self, location, data_type):
        url = f"{constants.BASE_URL}/{data_type}.json?key={self.api_key}&q={location}"
        logger.debug(f"Trying URL: {url}")
        with httpx.Client() as client:
            response = client.get(url)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Failed to get data from weather API: {e}")
        logger.debug(
            f"Got successful response from weather API: {response.status_code}"
        )
        logger.debug(f"Trying to save response to DB")
        return save_orm_from_json(response.json())


def save_orm_from_json(json_data):

    db = Session(engine)
    data = json_data
    # Create Location instance
    location_data = data["location"]
    location = Location(
        name=location_data["name"],
        region=location_data["region"],
        country=location_data["country"],
        lat=location_data["lat"],
        lon=location_data["lon"],
        tz_id=location_data["tz_id"],
    )
    try:
        db.add(location)
        db.commit()
        logger.debug(f"Location {location.name} added to database")
    except IntegrityError as e:
        logging.debug(f"Failed to save data to database, exception: {e}")
        db.rollback()
        logger.debug(f"Location {location.name} already exists in database, retrieving")
        select = (
            Select(Location)
            .where(Location.name == location.name)
            .where(Location.region == location.region)
            .where(Location.country == location.country)
        )
        location = db.exec(select).one_or_none()[0]

    # Create Condition instance for current weather
    current_condition_data = data["current"]["condition"]
    current_condition = Condition(
        text=current_condition_data["text"],
        icon=current_condition_data["icon"],
        code=current_condition_data["code"],
    )

    # Create CurrentWeather instance
    current_weather_data = data["current"]
    current_weather = CurrentWeather(
        location_id=location.id,
        last_updated=datetime.strptime(
            current_weather_data["last_updated"], "%Y-%m-%d %H:%M"
        ),
        temp_c=current_weather_data["temp_c"],
        temp_f=current_weather_data["temp_f"],
        is_day=current_weather_data["is_day"],
        wind_mph=current_weather_data["wind_mph"],
        wind_kph=current_weather_data["wind_kph"],
        wind_degree=current_weather_data["wind_degree"],
        wind_dir=current_weather_data["wind_dir"],
        pressure_mb=current_weather_data["pressure_mb"],
        pressure_in=current_weather_data["pressure_in"],
        precip_mm=current_weather_data["precip_mm"],
        precip_in=current_weather_data["precip_in"],
        humidity=current_weather_data["humidity"],
        cloud=current_weather_data["cloud"],
        feelslike_c=current_weather_data["feelslike_c"],
        feelslike_f=current_weather_data["feelslike_f"],
        vis_km=current_weather_data["vis_km"],
        vis_miles=current_weather_data["vis_miles"],
        uv=current_weather_data["uv"],
        gust_mph=current_weather_data["gust_mph"],
        gust_kph=current_weather_data["gust_kph"],
        condition=current_condition,
    )
    try:
        logger.debug(f"Adding current weather data to database")
        db.add(current_weather)
        db.commit()
        logging.debug(f"Current weather data added to database")
    except SQLAlchemyError as e:
        logger.debug(f"Failed to save data to database: {e}")
        db.rollback()

    # Create Forecast instance
    forecast_data = data["forecast"]["forecastday"][0]
    forecast = Forecast(
        date=datetime.strptime(forecast_data["date"], "%Y-%m-%d"),
        location_id=location.id,
    )
    try:
        logger.debug(f"Adding forecast data to database")
        db.add(forecast)
        db.commit()
    except IntegrityError:
        logger.debug(
            f"Failed to save forecast data to database due to IntegrityError - data already exists"
        )
        db.rollback()
        select = Select(Forecast).where(Forecast.date == forecast.date)
        forecast = db.exec(select).one_or_none()[0]

    # Create Daily instance
    daily_data = forecast_data["day"]
    daily_condition_data = daily_data["condition"]
    daily_condition = Condition(
        text=daily_condition_data["text"],
        icon=daily_condition_data["icon"],
        code=daily_condition_data["code"],
    )
    daily = Daily(
        maxtemp_c=daily_data["maxtemp_c"],
        maxtemp_f=daily_data["maxtemp_f"],
        mintemp_c=daily_data["mintemp_c"],
        mintemp_f=daily_data["mintemp_f"],
        avgtemp_c=daily_data["avgtemp_c"],
        avgtemp_f=daily_data["avgtemp_f"],
        maxwind_mph=daily_data["maxwind_mph"],
        maxwind_kph=daily_data["maxwind_kph"],
        totalprecip_mm=daily_data["totalprecip_mm"],
        totalprecip_in=daily_data["totalprecip_in"],
        totalsnow_cm=daily_data["totalsnow_cm"],
        avgvis_km=daily_data["avgvis_km"],
        avgvis_miles=daily_data["avgvis_miles"],
        avghumidity=daily_data["avghumidity"],
        daily_will_it_rain=daily_data["daily_will_it_rain"],
        daily_chance_of_rain=daily_data["daily_chance_of_rain"],
        daily_will_it_snow=daily_data["daily_will_it_snow"],
        daily_chance_of_snow=daily_data["daily_chance_of_snow"],
        uv=daily_data["uv"],
        condition=daily_condition,
        forecast_id=forecast.id,
    )
    try:
        save_to_db(daily, db)
    except IntegrityError:
        logger.debug(f"Daily data already exists in database, skipping")

    # Create Astro instance
    astro_data = forecast_data["astro"]
    astro = Astro(
        sunrise=astro_data["sunrise"],
        sunset=astro_data["sunset"],
        moonrise=astro_data["moonrise"],
        moonset=astro_data["moonset"],
        moon_phase=astro_data["moon_phase"],
        moon_illumination=astro_data["moon_illumination"],
        is_moon_up=astro_data["is_moon_up"],
        is_sun_up=astro_data["is_sun_up"],
        forecast_id=forecast.id,
    )
    try:
        save_to_db(astro, db)
    except IntegrityError:
        logger.debug(f"Astro data already exists in database, skipping")

    # Create Hourly instances
    hourly_instances = []
    for hour_data in forecast_data["hour"]:
        hour_condition_data = hour_data["condition"]
        hour_condition = Condition(
            text=hour_condition_data["text"],
            icon=hour_condition_data["icon"],
            code=hour_condition_data["code"],
        )
        hourly = Hourly(
            time=datetime.strptime(hour_data["time"], "%Y-%m-%d %H:%M"),
            temp_c=hour_data["temp_c"],
            temp_f=hour_data["temp_f"],
            is_day=hour_data["is_day"],
            wind_mph=hour_data["wind_mph"],
            wind_kph=hour_data["wind_kph"],
            wind_degree=hour_data["wind_degree"],
            wind_dir=hour_data["wind_dir"],
            pressure_mb=hour_data["pressure_mb"],
            pressure_in=hour_data["pressure_in"],
            precip_mm=hour_data["precip_mm"],
            precip_in=hour_data["precip_in"],
            snow_cm=hour_data["snow_cm"],
            humidity=hour_data["humidity"],
            cloud=hour_data["cloud"],
            feelslike_c=hour_data["feelslike_c"],
            feelslike_f=hour_data["feelslike_f"],
            windchill_c=hour_data["windchill_c"],
            windchill_f=hour_data["windchill_f"],
            heatindex_c=hour_data["heatindex_c"],
            heatindex_f=hour_data["heatindex_f"],
            dewpoint_c=hour_data["dewpoint_c"],
            dewpoint_f=hour_data["dewpoint_f"],
            will_it_rain=hour_data["will_it_rain"],
            chance_of_rain=hour_data["chance_of_rain"],
            will_it_snow=hour_data["will_it_snow"],
            chance_of_snow=hour_data["chance_of_snow"],
            vis_km=hour_data["vis_km"],
            vis_miles=hour_data["vis_miles"],
            gust_mph=hour_data["gust_mph"],
            gust_kph=hour_data["gust_kph"],
            uv=hour_data["uv"],
            condition=hour_condition,
            forecast_id=forecast.id,
        )
        hourly_instances.append(hourly)
        try:
            logger.debug(f"Adding hourly data to database")
            db.add(hourly)
            db.commit()
        except SQLAlchemyError as e:
            logger.debug(f"Failed to save data to database: {e}")
            db.rollback()
            print(f"Failed to save data to database: {e}")

    # Add relationships
    forecast.daily = daily
    forecast.astro = astro
    forecast.hourly = hourly_instances

    db.close()
    return forecast
