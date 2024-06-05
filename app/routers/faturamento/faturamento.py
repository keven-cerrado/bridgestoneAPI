from typing import Annotated, List
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from app.routers.login.schemas import User
from ...dependencies import get_current_user, oauth2_scheme
from sqlalchemy.orm import Session
from . import crud, models, schemas
from ...database import SessionLocal

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/faturamento", response_model=List[schemas.Faturamento])
async def read_faturamento(
    # token: Annotated[str, Depends(oauth2_scheme)],
    # current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    faturamento = crud.get_faturamento(db, skip=skip, limit=limit)
    if not faturamento:
        raise HTTPException(status_code=404, detail="Faturamento not found")
    return faturamento  


@router.get("/faturamento/", response_model=List[schemas.Faturamento])
async def read_faturamento_per_date(
    # token: Annotated[str, Depends(oauth2_scheme)],
    # current_user: Annotated[User, Depends(get_current_user)],
    start: str,
    end: str,
    db: Session = Depends(get_db),
):
    faturamento = crud.get_faturamento_per_date(db, start, end)
    if faturamento is None:
        raise HTTPException(status_code=404, detail="Faturamento not found")
    return faturamento
