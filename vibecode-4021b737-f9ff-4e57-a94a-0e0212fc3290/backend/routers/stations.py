from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Station, TimetablePattern
from schemas import (
    StationCreate, StationUpdate, StationOut, StationListResponse, Pagination
)

router = APIRouter(prefix="/api/stations", tags=["stations"])


@router.get("", response_model=StationListResponse)
def list_stations(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    total = db.query(func.count(Station.id)).scalar()
    stations = (
        db.query(Station)
        .order_by(func.trim(Station.name), Station.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return StationListResponse(
        items=[StationOut.model_validate(s) for s in stations],
        pagination=Pagination(limit=limit, offset=offset, total=total),
    )


@router.post("", response_model=StationOut, status_code=201)
def create_station(body: StationCreate, db: Session = Depends(get_db)):
    trimmed = body.name.strip()
    existing = db.query(Station).filter(func.trim(Station.name) == trimmed).first()
    if existing:
        raise HTTPException(422, detail="Station name must be unique")
    station = Station(name=trimmed)
    db.add(station)
    db.commit()
    db.refresh(station)
    return StationOut.model_validate(station)


@router.put("/{station_id}", response_model=StationOut)
def update_station(station_id: int, body: StationUpdate, db: Session = Depends(get_db)):
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(404, detail="Station not found")
    trimmed = body.name.strip()
    duplicate = (
        db.query(Station)
        .filter(func.trim(Station.name) == trimmed, Station.id != station_id)
        .first()
    )
    if duplicate:
        raise HTTPException(422, detail="Station name must be unique")
    station.name = trimmed
    db.commit()
    db.refresh(station)
    return StationOut.model_validate(station)


@router.delete("/{station_id}", status_code=204)
def delete_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(Station).filter(Station.id == station_id).first()
    if not station:
        raise HTTPException(404, detail="Station not found")
    referenced = (
        db.query(TimetablePattern)
        .filter(
            (TimetablePattern.origin_station_id == station_id)
            | (TimetablePattern.destination_station_id == station_id)
        )
        .first()
    )
    if referenced:
        raise HTTPException(409, detail="Station is referenced by a timetable pattern")
    db.delete(station)
    db.commit()
    return None