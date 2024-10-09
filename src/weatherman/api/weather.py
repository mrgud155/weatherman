import logging
from fastapi import APIRouter, Depends, Security, HTTPException
from sqlalchemy import Select
from sqlalchemy.orm import Session

from src.weatherman.api import auth
from src.weatherman.api.database import get_weather_db
from src.weatherman.ormodels import Location, Daily, Condition
from src.weatherman.ormodels import CurrentWeather as ORCurrentWeather
from src.weatherman.ormodels import Forecast as ORForecast
from src.weatherman.api.models import CurrentWeather, DailyForecast, ForecastMetadata

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/weather")


@router.get("/latest_current/{location_id}", response_model=CurrentWeather)
async def get_current_weather(
    location_id: int,
    db: Session = Depends(get_weather_db),
    current_user=Security(auth.get_current_user),
):
    select_weather = (
        Select(ORCurrentWeather)
        .where(ORCurrentWeather.location_id == location_id)
        .order_by(ORCurrentWeather.last_updated.desc())
    )
    latest_weather = db.execute(select_weather).first()
    location = db.get(Location, location_id)
    if latest_weather and location:
        weather = CurrentWeather.model_validate(latest_weather[0])
        weather.location = location
        return weather
    else:
        raise HTTPException(
            status_code=404, detail="Weather data not found for location"
        )


@router.get("/forecast_daily/{location_id}", response_model=DailyForecast)
async def get_forecast(
    location_id: int,
    db: Session = Depends(get_weather_db),
    current_user=Security(auth.get_current_user),
):
    select_forecast = (
        Select(ORForecast)
        .where(ORForecast.location_id == location_id)
        .order_by(ORForecast.date.desc())
    )
    latest_forecast = db.execute(select_forecast).first()[0]
    logger.debug(f"Latest forecast: {latest_forecast}")
    if latest_forecast:
        data_stmt = Select(Daily).where(Daily.forecast_id == latest_forecast.id)
        forecast_data = db.execute(data_stmt).one()[0]
        logger.debug(f"Forecast data: {forecast_data}")
        cond_stmt = Select(Condition).where(Condition.daily_id == forecast_data.id)
        condition = db.execute(cond_stmt).one()[0]
        forecast = DailyForecast.model_validate(forecast_data)
        forecast.condition = Condition.model_validate(condition)
        forecast.forecast_metadata = ForecastMetadata.model_validate(latest_forecast)
        return forecast
    else:
        raise HTTPException(
            status_code=404, detail="Forecast data not found for location"
        )


@router.get("/locations")
async def get_locations(
    db: Session = Depends(get_weather_db),
    current_user=Security(auth.get_current_user),
):
    locations = db.query(Location).all()
    return locations
