from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_session
from .. import crud, schemas

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items