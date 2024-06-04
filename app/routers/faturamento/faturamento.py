from typing import List
from fastapi import APIRouter, FastAPI, Depends, HTTPException
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
def read_faturamento(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    faturamento = crud.get_faturamento(db, skip=skip, limit=limit)
    if not faturamento:
        raise HTTPException(status_code=404, detail="Faturamento not found")
    return faturamento

        
@router.get("/faturamento/", response_model=List[schemas.Faturamento])
def read_faturamento_per_date(start: str, end: str, db: Session = Depends(get_db)):
    faturamento = crud.get_faturamento_per_date(db, start, end)
    if faturamento is None:
        raise HTTPException(status_code=404, detail="Faturamento not found")
    return faturamento