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
    """
    Função assíncrona responsável por enviar o faturamento.

    Returns:
        enviar (objeto): Objeto contendo informações sobre o envio do faturamento.

    Raises:
        HTTPException: Exceção lançada caso ocorra um erro ao enviar o faturamento.

    """
    try:
        enviar = scriptSend.tarefa_periodica_envio_faturamento(filial=filiais)
        logger.info("Faturamento enviado")
        return enviar
    except Exception as e:
        logger.error(f"Erro ao enviar faturamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar faturamento: {e}")


@router.get("/enviar/faturamento/")
async def enviar_faturamento(
    start: str = datetime.now().strftime("%d/%m/%Y"),
    end: str = datetime.now().strftime("%d/%m/%Y"),
):
    """
    Função assíncrona responsável por enviar o faturamento.

    Args:
        start (str): Data de início do período de envio. Padrão é a data atual.
        end (str): Data de fim do período de envio. Padrão é a data atual.

    Returns:
        enviar (objeto): Objeto contendo informações sobre o envio do faturamento.

    Raises:
        HTTPException: Exceção lançada caso ocorra um erro ao enviar o faturamento.
    """
    try:
        enviar = scriptSend.tarefa_periodica_envio_faturamento(
            filial=filiais, data_inicial=start, data_final=end
        )
        logger.info("Faturamento enviado")
        return enviar
    except Exception as e:
        logger.error(f"Erro ao enviar faturamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar faturamento: {e}")


@router.get("/enviar/fechamento")
async def enviar_fechamento():
    """
    Endpoint para enviar o fechamento.

    Este endpoint é responsável por enviar o fechamento para uma determinada filial.
    Ele chama a função `tarefa_periodica_envio_fechamento` do módulo `scriptSend` passando a filial como parâmetro.
    Em caso de sucesso, o endpoint retorna o resultado do envio.
    Em caso de erro, o endpoint registra o erro no log e retorna uma resposta de erro com código 500.

    Parâmetros:
        Nenhum.

    Retorno:
        O resultado do envio do fechamento.

    Exceções:
        - `HTTPException`: Caso ocorra um erro ao enviar o fechamento.

    Exemplo de uso:
        GET /enviar/fechamento

    """
    try:
        enviar = scriptSend.tarefa_periodica_envio_fechamento(filial=filiais)
        logger.info("Fechamento enviado")
        return enviar
    except Exception as e:
        logger.error(f"Erro ao enviar fechamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar fechamento: {e}")


@router.get("/enviar/fechamento/")
async def enviar_fechamento(
    start: str = datetime.now().strftime("%d/%m/%Y"),
    end: str = datetime.now().strftime("%d/%m/%Y"),
):
    """
    Função assíncrona responsável por enviar o fechamento.

    Args:
        start (str): Data de início do período de envio. Padrão é a data atual.
        end (str): Data de fim do período de envio. Padrão é a data atual.

    Returns:
        enviar (objeto): Objeto contendo informações sobre o envio do fechamento.

    Raises:
        HTTPException: Exceção lançada caso ocorra um erro ao enviar o fechamento.
    """
    try:
        enviar = scriptSend.tarefa_periodica_envio_fechamento(
            filial=filiais, data_inicial=start, data_final=end
        )
        logger.info("Fechamento enviado")
        return enviar
    except Exception as e:
        logger.error(f"Erro ao enviar fechamento: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao enviar fechamento: {str(e)}"
        )


@router.get("/verificar/reenvio")
async def verificar_reenvio():
    """
    Verifica se há necessidade de reenvio de envios.

    Retorna o resultado da verificação.

    Raises:
        HTTPException: Se ocorrer um erro ao verificar o reenvio.

    Returns:
        O resultado da verificação.
    """
    try:
        verificar = scriptSend.verificar_reenvio(filial=filiais)
        logger.info("Reenvio verificado")
        return verificar
    except Exception as e:
        logger.error(f"Erro ao verificar reenvio: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar reenvio: {e}")


@router.get("/verificar/cancelamentos")
async def verificar_cancelamentos():
    """
    Verifica cancelamentos.

    Verifica os cancelamentos de envios periodicamente. Retorna o resultado da verificação.

    Raises:
        HTTPException: Se ocorrer um erro ao verificar os cancelamentos.

    Returns:
        O resultado da verificação dos cancelamentos.
    """
    try:
        verificar = scriptSend.tarefa_periodica_verificacao_cancelamentos(
            filial=filiais
        )
        logger.info("Cancelamentos verificados")
        return verificar
    except Exception as e:
        logger.error(f"Erro ao verificar cancelamentos: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao verificar cancelamentos: {e}"
        )


@router.get("/verificar/devolucoes")
async def verificar_devolucoes():
    """
    Verifica as devoluções.

    Verifica as devoluções através da execução da função `tarefa_periodica_verificacao_devolucoes` do script `scriptSend`.
    Caso ocorra algum erro durante a verificação, uma exceção `HTTPException` será levantada com o status code 500 e uma mensagem de detalhe informando o erro.

    Returns:
        O resultado da verificação das devoluções.

    Raises:
        HTTPException: Caso ocorra algum erro durante a verificação das devoluções.
    """
    try:
        verificar = scriptSend.tarefa_periodica_verificacao_devolucoes(filial=filiais)
        logger.info("Devoluções verificadas")
        return verificar
    except Exception as e:
        logger.error(f"Erro ao verificar devoluções: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao verificar devoluções: {e}"
        )
