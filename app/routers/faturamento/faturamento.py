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
    """
    Endpoint para ler informações de faturamento.

    Parâmetros:
    - skip (int): O número de registros a serem pulados. Padrão é 0.
    - limit (int): O número máximo de registros a serem retornados. Padrão é 100.
    - db (Session): Sessão do banco de dados. Padrão é obtido através da função get_db.

    Retorno:
    - List[schemas.ModelScannTech]: Uma lista de objetos ModelScannTech contendo informações de faturamento.

    Exceções:
    - HTTPException: Retorna um erro 404 se nenhum faturamento for encontrado.

    """
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
    centro: str = None,
    db: Session = Depends(get_db),
):
    """
    Obtém o faturamento por data.

    Parâmetros:
    - start (str): Data de início no formato "YYYY-MM-DD".
    - end (str): Data de término no formato "YYYY-MM-DD".
    - centro (str, opcional): Filial do centro. Padrão é None.
    - db (Session): Sessão do banco de dados.

    Retorno:
    - List[schemas.ModelScannTech]: Lista de objetos ModelScannTech contendo o faturamento.

    Exceções:
    - HTTPException: Retorna um erro 404 se o faturamento não for encontrado.
    """
    logger.debug(f"Executing read_faturamento_per_date with start={start}, end={end}")
    faturamento = crud.get_faturamento_per_date(
        db, start, end, agrupar_outros=agrupar_outros_flag, filial=centro
    )
    if faturamento is None:
        logger.error(f"Faturamento not found for date range {start} to {end}")
        raise HTTPException(status_code=404, detail="Faturamento not found")
    logger.info(f"Faturamento for date range {start} to {end}: {faturamento}")
    return faturamento


# @router.get("/faturamento/enviar/")
# async def enviar_faturamento(
#     db: Session = Depends(get_db),
#     start: str = datetime.now().strftime("%d/%m/%Y"),
#     end: str = datetime.now().strftime("%d/%m/%Y"),
#     centro: str = None,
# ):
#     logger.debug("Executing envio de faturamento para API externa")
#     try:
#         utils.enviar_faturamento_para_api_externa(
#             db, start, end, agrupar_outros_flag=agrupar_outros_flag, filial=centro
#         )
#     except Exception as e:
#         logger.error(f"Error sending faturamento: {e}")
#         raise HTTPException(status_code=500, detail="Error sending faturamento")
#     return {"message": "Faturamento enviado com sucesso"}


@router.get("/fechamento", response_model=schemas.Fechamento)
async def read_fechamento(
    db: Session = Depends(get_db),
    start: str = datetime.now().strftime("%d/%m/%Y"),
    end: str = datetime.now().strftime("%d/%m/%Y"),
    centro: str = None,
):
    """
    Obtém o fechamento de faturamento com base nas datas de início e fim e no centro especificado.

    Parâmetros:
    - db (Session): Sessão do banco de dados.
    - start (str): Data de início no formato "%d/%m/%Y". Padrão: data atual.
    - end (str): Data de fim no formato "%d/%m/%Y". Padrão: data atual.
    - centro (str): Centro/filial específico. Padrão: None.

    Retorno:
    - Fechamento (schemas.Fechamento): Objeto que representa o fechamento de faturamento.

    Exceções:
    - HTTPException: Retorna um erro 404 se o fechamento não for encontrado.
    """
    fechamento = crud.get_fechamento_per_date(
        db, start, end, agrupar_outros=agrupar_outros_flag, filial=centro
    )
    if not fechamento:
        logger.error("Fechamento not found")
        raise HTTPException(status_code=404, detail="Fechamento not found")
    logger.info(f"Fechamento: {fechamento}")
    return fechamento


# @router.get("/fechamento/enviar/")
# async def enviar_fechamento(
#     db: Session = Depends(get_db),
#     start: str = datetime.now().strftime("%d/%m/%Y"),
#     end: str = datetime.now().strftime("%d/%m/%Y"),
#     centro: str = None,
# ):
#     logger.debug("Executing envio de fechamento para API externa")
#     try:
#         faturamento = utils.enviar_fechamento_diario(db, start, end, filial=centro)
#         logger.info(f"Fechamento enviado com sucesso: {faturamento}")
#     except Exception as e:
#         logger.error(f"Error sending fechamento: {e}")
#         raise HTTPException(status_code=500, detail="Error sending fechamento")
#     return {"message": "Fechamento enviado com sucesso"}


# @router.get("/cancelamentos/enviar/")
# async def enviar_cancelamentos(
#     db: Session = Depends(get_db),
#     centro: str = None,
# ):
#     logger.debug("Executing envio de cancelamentos para API externa")
#     try:
#         cancelamentos = utils.verificar_cancelamentos_enviar(db, filial=centro)
#         logger.info(f"Cancelamentos enviados com sucesso: {cancelamentos}")
#     except Exception as e:
#         logger.error(f"Error sending cancelamentos: {e}")
#         raise HTTPException(status_code=500, detail="Error sending cancelamentos")
#     return {"message": "Cancelamentos enviados com sucesso"}


@router.get("/solicitacoes", response_model=List[schemas.Solicitacoes])
async def read_solicitacoes(
    centro: str = None,
):
    """
    Obtém as solicitações de reenvio de faturamento.

    Parâmetros:
    - centro (str): O centro de distribuição para filtrar as solicitações. Se não for fornecido, todas as solicitações serão retornadas.

    Retorno:
    - List[schemas.Solicitacoes]: Uma lista de objetos de solicitações de reenvio de faturamento.

    Exceções:
    - Nenhuma exceção é lançada explicitamente neste método.
    """
    solicitacoes = utils.get_solicitacoes_reenvio(filial=centro)
    if not solicitacoes:
        logger.error("Solicitacoes not found")
        return []
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
