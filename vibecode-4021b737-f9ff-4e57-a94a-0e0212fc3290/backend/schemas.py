from datetime import datetime, timedelta, date
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from models import DayType, CrowdingLevel


class Pagination(BaseModel):
    limit: int
    offset: int
    total: int


class StationCreate(BaseModel):
    name: str = Field(..., min_length=1)

    @model_validator(mode="before")
    @classmethod
    def trim_name(cls, data):
        if isinstance(data, dict) and "name" in data:
            data["name"] = data["name"].strip()
        return data


class StationUpdate(BaseModel):
    name: str = Field(..., min_length=1)

    @model_validator(mode="before")
    @classmethod
    def trim_name(cls, data):
        if isinstance(data, dict) and "name" in data:
            data["name"] = data["name"].strip()
        return data


class StationOut(BaseModel):
    id: int
    name: str
    created_at: str

    model_config = {"from_attributes": True}


class StationListResponse(BaseModel):
    items: list[StationOut]
    pagination: Pagination


class TimetablePatternCreate(BaseModel):
    origin_station_id: int
    destination_station_id: int
    day_type: DayType
    start_time: str = Field(..., pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: str = Field(..., pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    baseline_crowding_level: CrowdingLevel


class TimetablePatternUpdate(BaseModel):
    origin_station_id: int
    destination_station_id: int
    day_type: DayType
    start_time: str = Field(..., pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: str = Field(..., pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    baseline_crowding_level: CrowdingLevel


class TimetablePatternOut(BaseModel):
    id: int
    origin_station_id: int
    origin_station_name: str
    destination_station_id: int
    destination_station_name: str
    day_type: str
    start_time: str
    end_time: str
    baseline_crowding_level: str
    created_at: str

    model_config = {"from_attributes": True}


class TimetablePatternListResponse(BaseModel):
    items: list[TimetablePatternOut]
    pagination: Pagination


class PublicHolidayCreate(BaseModel):
    calendar_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    display_name: str = Field(..., min_length=1)

    @model_validator(mode="before")
    @classmethod
    def trim_display_name(cls, data):
        if isinstance(data, dict) and "display_name" in data:
            data["display_name"] = data["display_name"].strip()
        return data


class PublicHolidayUpdate(BaseModel):
    calendar_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    display_name: str = Field(..., min_length=1)

    @model_validator(mode="before")
    @classmethod
    def trim_display_name(cls, data):
        if isinstance(data, dict) and "display_name" in data:
            data["display_name"] = data["display_name"].strip()
        return data


class PublicHolidayOut(BaseModel):
    id: int
    calendar_date: str
    display_name: str
    created_at: str

    model_config = {"from_attributes": True}


class PublicHolidayListResponse(BaseModel):
    items: list[PublicHolidayOut]
    pagination: Pagination


class JourneyPredictionRequest(BaseModel):
    origin_station_id: int
    destination_station_id: int
    journey_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    planned_departure_time: str = Field(..., pattern=r"^([01]\d|2[0-3]):[0-5]\d$")


class JourneyPredictionResponse(BaseModel):
    prediction_available: bool
    origin_station_name: Optional[str] = None
    destination_station_name: Optional[str] = None
    journey_date: Optional[str] = None
    planned_departure_time: Optional[str] = None
    derived_day_type: Optional[str] = None
    crowding_level: Optional[str] = None
    is_leave_earlier_alert_shown: Optional[bool] = None
    alert_text: Optional[str] = None
    suggested_departure_date: Optional[str] = None
    suggested_departure_time: Optional[str] = None
    saved_prediction_result_id: Optional[int] = None


class SavedPredictionResultOut(BaseModel):
    id: int
    origin_station_name: str
    destination_station_name: str
    journey_date: str
    planned_departure_time: str
    derived_day_type: str
    crowding_level: str
    is_leave_earlier_alert_shown: bool
    alert_text: Optional[str] = None
    suggested_departure_date: Optional[str] = None
    suggested_departure_time: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}


class SavedPredictionResultListResponse(BaseModel):
    items: list[SavedPredictionResultOut]
    pagination: Pagination