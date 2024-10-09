from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    disabled: bool | None = None
    hashed_password: str


class UserInDB(User):
    hashed_password: str


class Location(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    region: str
    country: str
    lat: float
    lon: float
    tz_id: str


class Condition(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    text: str
    icon: str
    code: int


class CurrentWeather(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
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
    location: Location
    condition: Condition


class ForecastMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    location_id: int
    date: datetime
    location: Optional[Location]


class DailyForecast(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
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
    forecast_id: int
    condition: Optional[Condition] = None
    forecast_metadata: Optional[ForecastMetadata] = None
