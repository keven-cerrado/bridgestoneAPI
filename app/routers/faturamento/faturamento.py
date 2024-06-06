import os
from typing import Annotated, List
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from app.routers.login.schemas import User
from ...dependencies import get_current_user, oauth2_scheme
from sqlalchemy.orm import Session
from . import crud, models, schemas
from ...database import SessionLocal
import logging
import sys
from logging.handlers import TimedRotatingFileHandler

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Verifica se a pasta de log existe, se não, cria
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Stream handler for console output
# stream_handler = logging.StreamHandler(sys.stdout)
# stream_formatter = logging.Formatter(
#     "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] "
#     "[%(levelname)s] %(name)s: %(message)s"
# )
# stream_handler.setFormatter(stream_formatter)
# logger.addHandler(stream_handler)

# Timed rotating file handler for daily log files
file_handler = TimedRotatingFileHandler(
    filename=os.path.join(log_directory, "app.log"),
    when="midnight",
    interval=1,
    backupCount=30  # Keep logs for the last 7 days
)
file_handler.suffix = "%Y-%m-%d"
file_formatter = logging.Formatter(
    "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] "
    "[%(levelname)s] %(name)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


@router.get("/faturamento", response_model=List[schemas.ModelScannTech])
async def read_faturamento(
    # token: Annotated[str, Depends(oauth2_scheme)],
    # current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    faturamento = crud.get_faturamento(db, skip=skip, limit=limit)
    if not faturamento:
        logger.error("Faturamento not found")
        raise HTTPException(status_code=404, detail="Faturamento not found")
    logger.info(f"Faturamento: {faturamento}")
    return faturamento


@router.get("/faturamento/", response_model=List[schemas.ModelScannTech])
async def read_faturamento_per_date(
    # token: Annotated[str, Depends(oauth2_scheme)],
    # current_user: Annotated[User, Depends(get_current_user)],
    start: str,
    end: str,
    db: Session = Depends(get_db),
):
    logger.debug(f"Executing read_faturamento_per_date with start={start}, end={end}")
    faturamento = crud.get_faturamento_per_date(db, start, end)
    if faturamento is None:
        logger.error(f"Faturamento not found for date range {start} to {end}")
        raise HTTPException(status_code=404, detail="Faturamento not found")
    logger.info(f"Faturamento for date range {start} to {end}: {faturamento}")
    return faturamento
