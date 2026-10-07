import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import relationship
from database import Base


class DayType(str, enum.Enum):
    weekday = "weekday"
    weekend = "weekend"
    holiday = "holiday"


class CrowdingLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    created_at = Column(String, nullable=False, server_default="CURRENT_TIMESTAMP")

    __table_args__ = (
        Index("stations_trimmed_name_unique", "name"),
        CheckConstraint("length(trim(name)) > 0", name="stations_name_not_blank"),
    )


class PublicHoliday(Base):
    __tablename__ = "public_holidays"

    id = Column(Integer, primary_key=True, autoincrement=True)
    calendar_date = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=False)
    created_at = Column(String, nullable=False, server_default="CURRENT_TIMESTAMP")

    __table_args__ = (
        CheckConstraint("length(trim(display_name)) > 0", name="holidays_display_name_not_blank"),
    )


class TimetablePattern(Base):
    __tablename__ = "timetable_patterns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin_station_id = Column(Integer, ForeignKey("stations.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    destination_station_id = Column(Integer, ForeignKey("stations.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    day_type = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    baseline_crowding_level = Column(String, nullable=False)
    created_at = Column(String, nullable=False, server_default="CURRENT_TIMESTAMP")

    origin_station = relationship("Station", foreign_keys=[origin_station_id])
    destination_station = relationship("Station", foreign_keys=[destination_station_id])

    __table_args__ = (
        CheckConstraint("origin_station_id <> destination_station_id", name="patterns_stations_distinct"),
        CheckConstraint("start_time < end_time", name="patterns_time_ordering"),
        Index("timetable_patterns_origin_station_day_type_time_index", "origin_station_id", "destination_station_id", "day_type", "start_time", "end_time"),
        Index("timetable_patterns_destination_station_id_index", "destination_station_id"),
    )


class SavedPredictionResult(Base):
    __tablename__ = "saved_prediction_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin_station_name = Column(String, nullable=False)
    destination_station_name = Column(String, nullable=False)
    journey_date = Column(String, nullable=False)
    planned_departure_time = Column(String, nullable=False)
    derived_day_type = Column(String, nullable=False)
    crowding_level = Column(String, nullable=False)
    is_leave_earlier_alert_shown = Column(Boolean, nullable=False)
    created_at = Column(String, nullable=False, server_default="CURRENT_TIMESTAMP")

    __table_args__ = (
        CheckConstraint("length(trim(origin_station_name)) > 0", name="results_origin_not_blank"),
        CheckConstraint("length(trim(destination_station_name)) > 0", name="results_dest_not_blank"),
        CheckConstraint("origin_station_name <> destination_station_name", name="results_stations_distinct"),
        Index("saved_prediction_results_journey_date_time_creation_index", "journey_date", "planned_departure_time", "id"),
        Index("saved_prediction_results_crowding_level_journey_date_time_index", "crowding_level", "journey_date", "planned_departure_time", "id"),
    )