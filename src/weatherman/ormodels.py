from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Location(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "region", "country", name="unique_city_constraint"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str

    current_weather: Optional["CurrentWeather"] = Relationship(
        back_populates="location"
    )
    forecast: List["Forecast"] = Relationship(back_populates="location")


class CurrentWeather(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "last_updated", "location_id", name="unique_time_location_constraint"
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    last_updated: datetime
    temp_c: float
    temp_f: float
    is_day: int
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    vis_km: float
    vis_miles: float
    uv: float
    gust_mph: float
    gust_kph: float

    location_id: Optional[int] = Field(default=None, foreign_key="location.id")
    location: Optional[Location] = Relationship(back_populates="current_weather")
    condition: "Condition" = Relationship(back_populates="current_weather")


class Condition(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            "current_weather_id", name="unique_current_weather_observation_constraint"
        ),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    icon: str
    code: int

    current_weather_id: Optional[int] = Field(
        default=None, foreign_key="currentweather.id"
    )
    current_weather: Optional[CurrentWeather] = Relationship(back_populates="condition")
    daily_id: Optional[int] = Field(default=None, foreign_key="daily.id")
    daily: Optional["Daily"] = Relationship(back_populates="condition")
    hourly_id: Optional[int] = Field(default=None, foreign_key="hourly.id")
    hourly: Optional["Hourly"] = Relationship(back_populates="condition")


class Forecast(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("date", "location_id", name="unique_date_location_constraint"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime

    location_id: Optional[int] = Field(default=None, foreign_key="location.id")
    location: Optional[Location] = Relationship(back_populates="forecast")
    daily: "Daily" = Relationship(back_populates="forecast")
    astro: "Astro" = Relationship(back_populates="forecast")
    hourly: List["Hourly"] = Relationship(back_populates="forecast")


class Daily(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("forecast_id", name="unique_daily_per_forecast_constraint"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    maxtemp_c: float
    maxtemp_f: float
    mintemp_c: float
    mintemp_f: float
    avgtemp_c: float
    avgtemp_f: float
    maxwind_mph: float
    maxwind_kph: float
    totalprecip_mm: float
    totalprecip_in: float
    totalsnow_cm: float
    avgvis_km: float
    avgvis_miles: float
    avghumidity: float
    daily_will_it_rain: int
    daily_chance_of_rain: int
    daily_will_it_snow: int
    daily_chance_of_snow: int
    uv: float

    forecast_id: Optional[int] = Field(default=None, foreign_key="forecast.id")
    forecast: Optional[Forecast] = Relationship(back_populates="daily")
    condition: Condition = Relationship(back_populates="daily")


class Astro(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("forecast_id", name="unique_astro_per_forecast_constraint"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    sunrise: str
    sunset: str
    moonrise: str
    moonset: str
    moon_phase: str
    moon_illumination: str
    is_moon_up: int
    is_sun_up: int

    forecast_id: Optional[int] = Field(default=None, foreign_key="forecast.id")
    forecast: Optional[Forecast] = Relationship(back_populates="astro")


class Hourly(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("time", name="unique_time_constraint"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    time: datetime
    temp_c: float
    temp_f: float
    is_day: int
    wind_mph: float
    wind_kph: float
    wind_degree: int
    wind_dir: str
    pressure_mb: float
    pressure_in: float
    precip_mm: float
    precip_in: float
    snow_cm: float
    humidity: int
    cloud: int
    feelslike_c: float
    feelslike_f: float
    windchill_c: float
    windchill_f: float
    heatindex_c: float
    heatindex_f: float
    dewpoint_c: float
    dewpoint_f: float
    will_it_rain: int
    chance_of_rain: int
    will_it_snow: int
    chance_of_snow: int
    vis_km: float
    vis_miles: float
    gust_mph: float
    gust_kph: float
    uv: float

    forecast_id: Optional[int] = Field(default=None, foreign_key="forecast.id")
    forecast: Optional[Forecast] = Relationship(back_populates="hourly")
    condition: Condition = Relationship(back_populates="hourly")
