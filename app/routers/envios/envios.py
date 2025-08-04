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
        enviar = scriptSend.tarefa_periodica_envio_faturamento()
        logger.info("Faturamento enviado")
        return enviar
    except Exception as e:
        logger.error(f"Erro ao enviar faturamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar faturamento: {e}")


@router.get("/enviar/faturamento/")
async def enviar_faturamento(
    start: str = datetime.now().strftime("%d/%m/%Y"),
    end: str = datetime.now().strftime("%d/%m/%Y"),
    centro: str = None,
):
    """
    Função assíncrona responsável por enviar o faturamento.

    Args:
        start (str): Data de início do período de envio. Padrão é a data atual.
        end (str): Data de fim do período de envio. Padrão é a data atual.
        centro (str): Centro/filial específico. Padrão: None.

    Returns:
        enviar (objeto): Objeto contendo informações sobre o envio do faturamento.

    Raises:
        HTTPException: Exceção lançada caso ocorra um erro ao enviar o faturamento.
    """
    try:
        enviar = scriptSend.tarefa_periodica_envio_faturamento(
            centro=centro, data_inicial=start, data_final=end
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
        enviar = scriptSend.tarefa_periodica_envio_fechamento()
        logger.info("Fechamento enviado")
        return enviar
    except Exception as e:
        logger.error(f"Erro ao enviar fechamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar fechamento: {e}")


@router.get("/enviar/fechamento/")
async def enviar_fechamento(
    start: str = datetime.now().strftime("%d/%m/%Y"),
    end: str = datetime.now().strftime("%d/%m/%Y"),
    centro: str = None,
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
            centro=centro, data_inicial=start, data_final=end
        )
        logger.info("Fechamento enviado")
        return enviar
    except Exception as e:
        logger.error(f"Erro ao enviar fechamento: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao enviar fechamento: {str(e)}"
        )


@router.get("/verificar/reenvio")
async def verificar_reenvio(
    centro: str = None,
):
    """
    Verifica se há necessidade de reenvio de envios e executa os reenvios automaticamente.

    Args:
        centro (str, optional): Código da filial específica para verificar.
                               Se não fornecido, verifica todas as filiais.

    Returns:
        dict: Resultado detalhado da verificação incluindo:
            - resumo: Estatísticas gerais (filiais verificadas, total de solicitações, sucessos, erros)
            - detalhes_por_filial: Informações específicas de cada filial
            - reenvios_executados: Lista completa de todos os reenvios executados
            - timestamp: Momento da execução

    Raises:
        HTTPException: Se ocorrer um erro ao verificar o reenvio.

    Example Response:
        {
            "resumo": {
                "filiais_verificadas": ["0101", "0102"],
                "total_solicitacoes_encontradas": 3,
                "total_reenvios_executados": 3,
                "sucessos": 2,
                "erros": 1
            },
            "detalhes_por_filial": {
                "0101": {
                    "tipos_verificados": {
                        "movimientos": {"solicitacoes_encontradas": 2, "sucessos": 2, "erros": 0},
                        "cierresDiarios": {"solicitacoes_encontradas": 0, "sucessos": 0, "erros": 0}
                    },
                    "total_solicitacoes": 2,
                    "reenvios_executados": 2,
                    "sucessos": 2,
                    "erros": 0
                }
            },
            "reenvios_executados": [...],
            "timestamp": 1642678800.123
        }
    """
    try:
        resultado = await scriptSend.verificar_reenvio(centro=centro)

        # Log das informações principais
        if resultado.get("resumo"):
            resumo = resultado["resumo"]
            logger.info(
                f"Verificação de reenvio concluída - "
                f"Filiais: {len(resumo.get('filiais_verificadas', []))}, "
                f"Solicitações: {resumo.get('total_solicitacoes_encontradas', 0)}, "
                f"Sucessos: {resumo.get('sucessos', 0)}, "
                f"Erros: {resumo.get('erros', 0)}"
            )

        return {
            "status": "success",
            "message": "Verificação de reenvio concluída com sucesso",
            "data": resultado,
        }
    except Exception as e:
        logger.error(f"Erro ao verificar reenvio: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Erro ao verificar reenvio: {str(e)}",
                "error_type": type(e).__name__,
            },
        )


@router.post("/executar/reenvio")
async def executar_reenvio(
    data: str,
    tipo: str,
    centro: str,
):
    """
    Executa um reenvio manual para uma data, tipo e filial específicos.

    Args:
        data (str): Data para reenvio no formato dd/mm/yyyy
        tipo (str): Tipo de reenvio ('movimientos' ou 'cierresDiarios')
        centro (str): Código da filial

    Returns:
        Resultado do reenvio executado

    Raises:
        HTTPException: Se ocorrer um erro ao executar o reenvio
    """
    try:
        from app.database import SessionLocal
        from app.routers.faturamento.schemas import Solicitacoes
        from datetime import datetime

        # Valida o tipo
        tipos_validos = [
            "movimientos",
            "cierresDiarios",
            "MOVIMIENTOS",
            "CIERRES_DIARIOS",
            "cierres_diarios",
        ]
        if tipo not in tipos_validos:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo deve ser um dos seguintes: {', '.join(tipos_validos)}",
            )

        # Converte a data string para objeto date
        try:
            data_obj = datetime.strptime(data, "%d/%m/%Y").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Data deve estar no formato dd/mm/yyyy"
            )

        # Cria uma solicitação fictícia para usar a função processar_reenvio
        solicitacao_ficticia = Solicitacoes(
            fecha=data_obj, codigoCaja=1, tipo=tipo  # Valor padrão
        )

        db = SessionLocal()
        try:
            resultado = scriptSend.processar_reenvio(db, solicitacao_ficticia, centro)

            if resultado["status"] == "sucesso":
                logger.info(f"Reenvio manual executado com sucesso: {resultado}")
                return {
                    "message": "Reenvio executado com sucesso",
                    "resultado": resultado,
                }
            else:
                logger.error(f"Erro no reenvio manual: {resultado}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao executar reenvio: {resultado['mensagem']}",
                )
        finally:
            db.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao executar reenvio manual: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao executar reenvio: {str(e)}"
        )


@router.get("/verificar/cancelamentos")
async def verificar_cancelamentos(
    centro: str = None,
):
    """
    Verifica cancelamentos.

    Verifica os cancelamentos de envios periodicamente. Retorna o resultado da verificação.

    Raises:
        HTTPException: Se ocorrer um erro ao verificar os cancelamentos.

    Returns:
        O resultado da verificação dos cancelamentos.
    """
    try:
        verificar = scriptSend.tarefa_periodica_verificacao_cancelamentos(centro=centro)
        logger.info("Cancelamentos verificados")
        return verificar
    except Exception as e:
        logger.error(f"Erro ao verificar cancelamentos: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao verificar cancelamentos: {e}"
        )


@router.get("/verificar/devolucoes")
async def verificar_devolucoes(
    centro: str = None,
):
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
        verificar = scriptSend.tarefa_periodica_verificacao_devolucoes(centro=centro)
        logger.info("Devoluções verificadas")
        return verificar
    except Exception as e:
        logger.error(f"Erro ao verificar devoluções: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao verificar devoluções: {e}"
        )
