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


@router.get("/enviar/faturamento")
async def enviar_faturamento():
    try:
        enviar = scriptSend.tarefa_periodica_envio_faturamento(filial=filiais)
        logger.info("Faturamento enviado")
        return enviar
    except Exception as e:
        logger.error(f"Erro ao enviar faturamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar faturamento: {e}")
    

@router.get("/enviar/fechamento")
async def enviar_fechamento():
    try:
        enviar = scriptSend.tarefa_periodica_envio_fechamento(filial=filiais)
        logger.info("Fechamento enviado")
        return enviar
    except Exception as e:
        logger.error(f"Erro ao enviar fechamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar fechamento: {e}")


@router.get("/verificar/reenvio")
async def verificar_reenvio():
    try:
        verificar = scriptSend.verificar_reenvio(filial=filiais)
        logger.info("Reenvio verificado")
        return verificar
    except Exception as e:
        logger.error(f"Erro ao verificar reenvio: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar reenvio: {e}")


@router.get("/verificar/cancelamentos")
async def verificar_cancelamentos():
    try:
        verificar = scriptSend.tarefa_periodica_verificacao_cancelamentos(filial=filiais)
        logger.info("Cancelamentos verificados")
        return verificar
    except Exception as e:
        logger.error(f"Erro ao verificar cancelamentos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar cancelamentos: {e}")


@router.get("/verificar/devolucoes")
async def verificar_devolucoes():
    try:
        verificar = scriptSend.tarefa_periodica_verificacao_devolucoes(filial=filiais)
        logger.info("Devoluções verificadas")
        return verificar
    except Exception as e:
        logger.error(f"Erro ao verificar devoluções: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar devoluções: {e}")
