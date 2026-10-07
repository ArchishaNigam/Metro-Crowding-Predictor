from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Station, PublicHoliday, TimetablePattern, SavedPredictionResult, DayType, CrowdingLevel
from schemas import JourneyPredictionRequest, JourneyPredictionResponse

router = APIRouter(prefix="/api/journey-predictions", tags=["journey_predictions"])


def _derive_day_type(journey_date_str, holidays):
    dt = datetime.strptime(journey_date_str, "%Y-%m-%d").date()
    for h in holidays:
        if h.calendar_date == journey_date_str:
            return DayType.holiday
    if dt.weekday() >= 5:
        return DayType.weekend
    return DayType.weekday


def _compute_suggested_date_time(journey_date_str, planned_time_str):
    dt = datetime.strptime(f"{journey_date_str} {planned_time_str}", "%Y-%m-%d %H:%M")
    suggested = dt - timedelta(minutes=20)
    return suggested.strftime("%Y-%m-%d"), suggested.strftime("%H:%M")


@router.post("", response_model=JourneyPredictionResponse)
def create_journey_prediction(body: JourneyPredictionRequest, db: Session = Depends(get_db)):
    if body.origin_station_id == body.destination_station_id:
        raise HTTPException(422, detail="Origin and destination stations must differ")

    origin = db.query(Station).filter(Station.id == body.origin_station_id).first()
    if not origin:
        raise HTTPException(422, detail="Origin station not found")
    dest = db.query(Station).filter(Station.id == body.destination_station_id).first()
    if not dest:
        raise HTTPException(422, detail="Destination station not found")

    try:
        datetime.strptime(body.journey_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(422, detail="Invalid journey date format")

    holidays = db.query(PublicHoliday).all()
    day_type = _derive_day_type(body.journey_date, holidays)

    pattern = (
        db.query(TimetablePattern)
        .filter(
            TimetablePattern.origin_station_id == body.origin_station_id,
            TimetablePattern.destination_station_id == body.destination_station_id,
            TimetablePattern.day_type == day_type.value,
            TimetablePattern.start_time <= body.planned_departure_time,
            TimetablePattern.end_time >= body.planned_departure_time,
        )
        .first()
    )

    if not pattern:
        return JourneyPredictionResponse(
            prediction_available=False,
            origin_station_name=origin.name,
            destination_station_name=dest.name,
            journey_date=body.journey_date,
            planned_departure_time=body.planned_departure_time,
            derived_day_type=day_type.value,
        )

    crowding = CrowdingLevel(pattern.baseline_crowding_level)
    is_high = crowding == CrowdingLevel.high
    is_leave_earlier_alert_shown = is_high

    suggested_date = None
    suggested_time = None
    alert_text = None
    if is_high:
        alert_text = "Leave 20 minutes earlier"
        suggested_date, suggested_time = _compute_suggested_date_time(
            body.journey_date, body.planned_departure_time
        )

    result = SavedPredictionResult(
        origin_station_name=origin.name,
        destination_station_name=dest.name,
        journey_date=body.journey_date,
        planned_departure_time=body.planned_departure_time,
        derived_day_type=day_type.value,
        crowding_level=crowding.value,
        is_leave_earlier_alert_shown=is_leave_earlier_alert_shown,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return JourneyPredictionResponse(
        prediction_available=True,
        origin_station_name=origin.name,
        destination_station_name=dest.name,
        journey_date=body.journey_date,
        planned_departure_time=body.planned_departure_time,
        derived_day_type=day_type.value,
        crowding_level=crowding.value,
        is_leave_earlier_alert_shown=is_leave_earlier_alert_shown,
        alert_text=alert_text,
        suggested_departure_date=suggested_date,
        suggested_departure_time=suggested_time,
        saved_prediction_result_id=result.id,
    )