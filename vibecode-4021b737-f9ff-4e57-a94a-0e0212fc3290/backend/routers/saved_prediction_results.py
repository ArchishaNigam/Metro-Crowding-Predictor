from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import SavedPredictionResult, CrowdingLevel
from schemas import SavedPredictionResultOut, SavedPredictionResultListResponse, Pagination

router = APIRouter(prefix="/api/saved-prediction-results", tags=["saved_prediction_results"])


def _result_to_out(r):
    alert_text = None
    suggested_date = None
    suggested_time = None
    if r.is_leave_earlier_alert_shown:
        alert_text = "Leave 20 minutes earlier"
        dt = datetime.strptime(f"{r.journey_date} {r.planned_departure_time}", "%Y-%m-%d %H:%M")
        suggested = dt - timedelta(minutes=20)
        suggested_date = suggested.strftime("%Y-%m-%d")
        suggested_time = suggested.strftime("%H:%M")
    return SavedPredictionResultOut(
        id=r.id,
        origin_station_name=r.origin_station_name,
        destination_station_name=r.destination_station_name,
        journey_date=r.journey_date,
        planned_departure_time=r.planned_departure_time,
        derived_day_type=r.derived_day_type,
        crowding_level=r.crowding_level,
        is_leave_earlier_alert_shown=bool(r.is_leave_earlier_alert_shown),
        alert_text=alert_text,
        suggested_departure_date=suggested_date,
        suggested_departure_time=suggested_time,
        created_at=r.created_at,
    )


@router.get("", response_model=SavedPredictionResultListResponse)
def list_saved_prediction_results(
    crowding_level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(SavedPredictionResult)
    if crowding_level is not None:
        if crowding_level not in ("low", "medium", "high"):
            raise HTTPException(422, detail="Invalid crowding level filter")
        query = query.filter(SavedPredictionResult.crowding_level == crowding_level)

    total = query.with_entities(func.count(SavedPredictionResult.id)).scalar()

    results = (
        query
        .order_by(
            SavedPredictionResult.journey_date,
            SavedPredictionResult.planned_departure_time,
            SavedPredictionResult.id,
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    return SavedPredictionResultListResponse(
        items=[_result_to_out(r) for r in results],
        pagination=Pagination(limit=limit, offset=offset, total=total),
    )