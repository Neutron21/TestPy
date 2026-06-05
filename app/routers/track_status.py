from fastapi import APIRouter

from app.db import SessionDep
from app.models import Track_Status, TrackStatusResponse, TrackStatusCreate


router = APIRouter(tags=["Track_Status"])

@router.post("/track-status", response_model=TrackStatusResponse)
async def create_track_status(data: TrackStatusCreate, session: SessionDep):

    new_status = Track_Status(**data.model_dump())

    session.add(new_status)
    session.commit()
    session.refresh(new_status)

    return new_status