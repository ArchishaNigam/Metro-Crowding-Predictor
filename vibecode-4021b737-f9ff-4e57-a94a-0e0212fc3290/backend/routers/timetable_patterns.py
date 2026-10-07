from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Station, TimetablePattern
from schemas import (
    TimetablePatternCreate, TimetablePatternUpdate,
    TimetablePatternOut, TimetablePatternListResponse, Pagination
)

router = APIRouter(prefix="/api/timetable-patterns", tags=["timetable_patterns"])


def _pattern_to_out(p, db):
    origin = db.query(Station).filter(Station.id == p.origin_station_id).first()
    dest = db.query(Station).filter(Station.id == p.destination_station_id).first()
    return TimetablePatternOut(
        id=p.id,
        origin_station_id=p.origin_station_id,
        origin_station_name=origin.name if origin else "",
        destination_station_id=p.destination_station_id,
        destination_station_name=dest.name if dest else "",
        day_type=p.day_type,
        start_time=p.start_time,
        end_time=p.end_time,
        baseline_crowding_level=p.baseline_crowding_level,
        created_at=p.created_at,
    )


@router.get("", response_model=TimetablePatternListResponse)
def list_timetable_patterns(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    total = db.query(func.count(TimetablePattern.id)).scalar()
    patterns = (
        db.query(TimetablePattern)
        .order_by(
            TimetablePattern.origin_station_id,
            TimetablePattern.destination_station_id,
            TimetablePattern.day_type,
            TimetablePattern.start_time,
            TimetablePattern.id,
        )
        .offset(offset)
        .limit(limit)
        .all()
    )
    return TimetablePatternListResponse(
        items=[_pattern_to_out(p, db) for p in patterns],
        pagination=Pagination(limit=limit, offset=offset, total=total),
    )


def _check_overlap(db, origin_id, dest_id, day_type, start_time, end_time, exclude_id=None):
    query = db.query(TimetablePattern).filter(
        TimetablePattern.origin_station_id == origin_id,
        TimetablePattern.destination_station_id == dest_id,
        TimetablePattern.day_type == day_type,
        TimetablePattern.start_time <= end_time,
        TimetablePattern.end_time >= start_time,
    )
    if exclude_id is not None:
        query = query.filter(TimetablePattern.id != exclude_id)
    return query.first()


@router.post("", response_model=TimetablePatternOut, status_code=201)
def create_timetable_pattern(body: TimetablePatternCreate, db: Session = Depends(get_db)):
    if body.origin_station_id == body.destination_station_id:
        raise HTTPException(422, detail="Origin and destination stations must differ")
    origin = db.query(Station).filter(Station.id == body.origin_station_id).first()
    if not origin:
        raise HTTPException(422, detail="Origin station not found")
    dest = db.query(Station).filter(Station.id == body.destination_station_id).first()
    if not dest:
        raise HTTPException(422, detail="Destination station not found")
    if body.start_time >= body.end_time:
        raise HTTPException(422, detail="Start time must be earlier than end time")
    overlap = _check_overlap(db, body.origin_station_id, body.destination_station_id, body.day_type.value, body.start_time, body.end_time)
    if overlap:
        raise HTTPException(422, detail="Time range overlaps an existing pattern")
    pattern = TimetablePattern(
        origin_station_id=body.origin_station_id,
        destination_station_id=body.destination_station_id,
        day_type=body.day_type.value,
        start_time=body.start_time,
        end_time=body.end_time,
        baseline_crowding_level=body.baseline_crowding_level.value,
    )
    db.add(pattern)
    db.commit()
    db.refresh(pattern)
    return _pattern_to_out(pattern, db)


@router.put("/{pattern_id}", response_model=TimetablePatternOut)
def update_timetable_pattern(pattern_id: int, body: TimetablePatternUpdate, db: Session = Depends(get_db)):
    pattern = db.query(TimetablePattern).filter(TimetablePattern.id == pattern_id).first()
    if not pattern:
        raise HTTPException(404, detail="Timetable pattern not found")
    if body.origin_station_id == body.destination_station_id:
        raise HTTPException(422, detail="Origin and destination stations must differ")
    origin = db.query(Station).filter(Station.id == body.origin_station_id).first()
    if not origin:
        raise HTTPException(422, detail="Origin station not found")
    dest = db.query(Station).filter(Station.id == body.destination_station_id).first()
    if not dest:
        raise HTTPException(422, detail="Destination station not found")
    if body.start_time >= body.end_time:
        raise HTTPException(422, detail="Start time must be earlier than end time")
    overlap = _check_overlap(db, body.origin_station_id, body.destination_station_id, body.day_type.value, body.start_time, body.end_time, exclude_id=pattern_id)
    if overlap:
        raise HTTPException(422, detail="Time range overlaps an existing pattern")
    pattern.origin_station_id = body.origin_station_id
    pattern.destination_station_id = body.destination_station_id
    pattern.day_type = body.day_type.value
    pattern.start_time = body.start_time
    pattern.end_time = body.end_time
    pattern.baseline_crowding_level = body.baseline_crowding_level.value
    db.commit()
    db.refresh(pattern)
    return _pattern_to_out(pattern, db)


@router.delete("/{pattern_id}", status_code=204)
def delete_timetable_pattern(pattern_id: int, db: Session = Depends(get_db)):
    pattern = db.query(TimetablePattern).filter(TimetablePattern.id == pattern_id).first()
    if not pattern:
        raise HTTPException(404, detail="Timetable pattern not found")
    db.delete(pattern)
    db.commit()
    return None