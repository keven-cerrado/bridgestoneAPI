from datetime import datetime
import os
from typing import Annotated, List
from fastapi import APIRouter, FastAPI, Depends, HTTPException
from app.log_config import setup_logger
from app.routers.faturamento import scriptSend

from ..faturamento import crud, models, schemas, utils
from ...database import SessionLocal
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from ...configuracoes import agrupar_outros_flag, filiais

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


@router.get("/enviar/faturamento", response_model=List[schemas.ModelScannTech])
async def enviar_faturamento():
    enviar = scriptSend.tarefa_periodica_envio_faturamento(filial=filiais)
    if not enviar:
        logger.error("Faturamento não enviado")
        raise HTTPException(status_code=500, detail="Faturamento não enviado")
    logger.info("Faturamento enviado")
    return enviar


@router.get("/verificar/reenvio", response_model=List[schemas.Solicitacoes])
async def verificar_reenvio():
    verificar = await scriptSend.verificar_reenvio(filial=filiais)
    logger.info("Reenvio verificado")
    return verificar


@router.get("/verificar/cancelamentos")
async def verificar_cancelamentos():
    verificar = scriptSend.tarefa_periodica_verificacao_cancelamentos(filial=filiais)
    if not verificar:
        logger.error("Cancelamentos não verificados")
        raise HTTPException(status_code=500, detail="Cancelamentos não verificados")
    logger.info("Cancelamentos verificados")
    return {"message": "Cancelamentos verificados"}


@router.get("/verificar/devolucoes")
async def verificar_devolucoes():
    verificar = scriptSend.tarefa_periodica_verificacao_devolucoes(filial=filiais)
    if not verificar:
        logger.error("Devoluções não verificadas")
        raise HTTPException(status_code=500, detail="Devoluções não verificadas")
    logger.info("Devoluções verificadas")
    return {"message": "Devoluções verificadas"}
