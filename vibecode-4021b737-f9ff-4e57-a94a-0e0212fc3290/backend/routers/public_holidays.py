from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import PublicHoliday
from schemas import (
    PublicHolidayCreate, PublicHolidayUpdate,
    PublicHolidayOut, PublicHolidayListResponse, Pagination
)

router = APIRouter(prefix="/api/public-holidays", tags=["public_holidays"])


@router.get("", response_model=PublicHolidayListResponse)
def list_public_holidays(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    total = db.query(func.count(PublicHoliday.id)).scalar()
    holidays = (
        db.query(PublicHoliday)
        .order_by(PublicHoliday.calendar_date, PublicHoliday.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return PublicHolidayListResponse(
        items=[PublicHolidayOut.model_validate(h) for h in holidays],
        pagination=Pagination(limit=limit, offset=offset, total=total),
    )


@router.post("", response_model=PublicHolidayOut, status_code=201)
def create_public_holiday(body: PublicHolidayCreate, db: Session = Depends(get_db)):
    existing = db.query(PublicHoliday).filter(PublicHoliday.calendar_date == body.calendar_date).first()
    if existing:
        raise HTTPException(422, detail="A holiday already exists for this date")
    holiday = PublicHoliday(
        calendar_date=body.calendar_date,
        display_name=body.display_name.strip(),
    )
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return PublicHolidayOut.model_validate(holiday)


@router.put("/{holiday_id}", response_model=PublicHolidayOut)
def update_public_holiday(holiday_id: int, body: PublicHolidayUpdate, db: Session = Depends(get_db)):
    holiday = db.query(PublicHoliday).filter(PublicHoliday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(404, detail="Public holiday not found")
    duplicate = (
        db.query(PublicHoliday)
        .filter(PublicHoliday.calendar_date == body.calendar_date, PublicHoliday.id != holiday_id)
        .first()
    )
    if duplicate:
        raise HTTPException(422, detail="A holiday already exists for this date")
    holiday.calendar_date = body.calendar_date
    holiday.display_name = body.display_name.strip()
    db.commit()
    db.refresh(holiday)
    return PublicHolidayOut.model_validate(holiday)


@router.delete("/{holiday_id}", status_code=204)
def delete_public_holiday(holiday_id: int, db: Session = Depends(get_db)):
    holiday = db.query(PublicHoliday).filter(PublicHoliday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(404, detail="Public holiday not found")
    db.delete(holiday)
    db.commit()
    return None