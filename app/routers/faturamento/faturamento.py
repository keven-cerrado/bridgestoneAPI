from datetime import datetime
import os
from typing import Annotated, List
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from app.log_config import setup_logger
from app.routers.login.schemas import User
from ...dependencies import get_current_user, oauth2_scheme
from sqlalchemy.orm import Session
from . import crud, models, schemas, utils
from ...database import SessionLocal
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from ...configuracoes import agrupar_outros_flag

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Verifica se o logger já foi configurado
if not logging.getLogger().hasHandlers():
    logger = setup_logger()
else:
    logger = logging.getLogger(__name__)


@router.get("/faturamento", response_model=List[schemas.ModelScannTech])
async def read_faturamento(
    # token: Annotated[str, Depends(oauth2_scheme)],
    # current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    faturamento = crud.get_faturamento(
        db, skip=skip, limit=limit, agrupar_outros=agrupar_outros_flag
    )
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
    faturamento = crud.get_faturamento_per_date(
        db, start, end, agrupar_outros=agrupar_outros_flag
    )
    if faturamento is None:
        logger.error(f"Faturamento not found for date range {start} to {end}")
        raise HTTPException(status_code=404, detail="Faturamento not found")
    logger.info(f"Faturamento for date range {start} to {end}: {faturamento}")
    return faturamento


@router.get("/faturamento/enviar/")
async def enviar_faturamento(
    db: Session = Depends(get_db),
    start: str = datetime.now().strftime("%d/%m/%Y"),
    end: str = datetime.now().strftime("%d/%m/%Y"),
):
    logger.debug("Executing envio de faturamento para API externa")
    try:
        utils.enviar_faturamento_para_api_externa(
            db, start, end, agrupar_outros_flag=agrupar_outros_flag
        )
    except Exception as e:
        logger.error(f"Error sending faturamento: {e}")
        raise HTTPException(status_code=500, detail="Error sending faturamento")
    return {"message": "Faturamento enviado com sucesso"}


@router.get("/fechamento", response_model=schemas.Fechamento)
async def read_fechamento(
    db: Session = Depends(get_db),
    start: str = datetime.now().strftime("%d/%m/%Y"),
    end: str = datetime.now().strftime("%d/%m/%Y"),
):
    fechamento = crud.get_fechamento_per_date(
        db, start, end, agrupar_outros=agrupar_outros_flag
    )
    if not fechamento:
        logger.error("Fechamento not found")
        raise HTTPException(status_code=404, detail="Fechamento not found")
    logger.info(f"Fechamento: {fechamento}")
    return fechamento


@router.get("/fechamento/enviar/")
async def enviar_fechamento(
    db: Session = Depends(get_db),
    start: str = datetime.now().strftime("%d/%m/%Y"),
    end: str = datetime.now().strftime("%d/%m/%Y"),
):
    logger.debug("Executing envio de fechamento para API externa")
    try:
        faturamento = utils.enviar_fechamento_diario(db, start, end)
        logger.info(f"Fechamento enviado com sucesso: {faturamento}")
    except Exception as e:
        logger.error(f"Error sending fechamento: {e}")
        raise HTTPException(status_code=500, detail="Error sending fechamento")
    return {"message": "Fechamento enviado com sucesso"}


@router.get("/solicitacoes", response_model=List[schemas.Solicitacoes])
async def read_solicitacoes():
    solicitacoes = utils.get_solicitacoes_reenvio()
    if not solicitacoes:
        logger.error("Solicitacoes not found")
        raise HTTPException(status_code=404, detail="Solicitacoes not found")
    logger.info(f"Solicitacoes: {solicitacoes}")
    return solicitacoes


# @router.post("/set_agrupar_outros")
# async def set_agrupar_outros(request: schemas.AgruparOutrosRequest):
#     global agrupar_outros_flag
#     agrupar_outros_flag = request.agrupar_outros
#     return {"agrupar_outros": agrupar_outros_flag}


# @router.get(f"/get_agrupar_outros")
# async def get_agrupar_outros():
#     return {"agrupar_outros": agrupar_outros_flag}
