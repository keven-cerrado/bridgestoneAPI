import json
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import List
import requests
from sqlalchemy.orm import Session

from app.log_config import setup_logger
from .crud import get_faturamento_per_date, get_fechamento_per_date
from .schemas import ModelScannTech, Fechamento, Solicitacoes
from datetime import datetime
from app.constants import (
    url_base,
    idEmpresa,
    idLocal,
    idCaja,
    headers,
    agrupar_outros_flag,
)


# Verifica se o logger já foi configurado
if not logging.getLogger().hasHandlers():
    logger = setup_logger()
else:
    logger = logging.getLogger(__name__)


def enviar_faturamento_para_api_externa(
    db: Session,
    data_inicial: str,
    data_final: str,
    agrupar_outros_flag: bool = agrupar_outros_flag,
):
    current_date = datetime.now().strftime("%d/%m/%Y")

    # Get the faturamentos for the current date
    # faturamentos = get_faturamento_per_date(db, current_date, current_date)
    faturamentos: List[ModelScannTech] = get_faturamento_per_date(
        db,
        (data_inicial if data_inicial else current_date),
        (data_final if data_final else current_date),
        agrupar_outros=agrupar_outros_flag,
    )
    faturamentos_json = [json.loads(f.model_dump_json()) for f in faturamentos]
    faturamentos_json = json.dumps(faturamentos_json)

    url_api_externa = f"{url_base}/v2/minoristas/{idEmpresa}/locales/{idLocal}/cajas/{idCaja}/movimientos/lotes"
    try:
        resposta = requests.post(
            url_api_externa, data=faturamentos_json, headers=headers
        )
        resposta.raise_for_status()
        logger.info(
            "Faturamento enviado com sucesso. %s notas enviadas. Status code: %s",
            len(faturamentos),
            resposta.status_code,
        )
        logger.info(resposta.text)
        logger.info(faturamentos_json)
        print(f"Faturamento enviado com sucesso. {len(faturamentos)} notas enviadas.")
        print(faturamentos_json)
    except requests.exceptions.HTTPError as err:
        logger.error(
            "Falha ao enviar faturamento. Status code: %s", err.response.status_code
        )
        logger.error("Detalhes do erro: %s", err.response.text)
        logger.error(faturamentos_json)
        print("Falha ao enviar faturamento. Status code:", err.response.status_code)
        print("Detalhes do erro:", err.response.text)
        print(faturamentos_json)
    except requests.exceptions.RequestException as err:
        logger.error("Erro de conexão ao enviar faturamento: %s", err)
        logger.error(faturamentos_json)
        print("Erro de conexão ao enviar faturamento:", err)
        print(faturamentos_json)

    return faturamentos


def enviar_fechamento_diario(
    db: Session,
    data_inicial: str,
    data_final: str,
    agrupar_outros_flag: bool = agrupar_outros_flag,
):
    current_date = datetime.now().strftime("%d/%m/%Y")

    # # Get the faturamentos for the current date
    # faturamentos: List[ModelScannTech] = get_faturamento_per_date(
    #     db,
    #     (data_inicial if data_inicial else current_date),
    #     (data_final if data_final else current_date),
    #     agrupar_outros=agrupar_outros_flag,
    # )
    # fechamento_data = faturamentos[0].fecha
    # total_vendas = sum([f.total for f in faturamentos])
    # # total_cancelamentos = sum([f. for f in faturamentos])
    # qtd_vendas = len(faturamentos)
    # qtd_cancelamentos = len([f for f in faturamentos if f.cancelacion])

    # fechamento: Fechamento = Fechamento(
    #     fechaVentas=fechamento_data,
    #     montoVentaLiquida=total_vendas,
    #     montoCancelaciones=0.0,
    #     cantidadMovimientos=qtd_vendas,
    #     cantidadCancelaciones=qtd_cancelamentos,
    # )
    fechamento: Fechamento = get_fechamento_per_date(
        db,
        (data_inicial if data_inicial else current_date),
        (data_final if data_final else current_date),
        agrupar_outros=agrupar_outros_flag,
    )

    url_api_externa = f"{url_base}/v2/minoristas/{idEmpresa}/locales/{idLocal}/cajas/{idCaja}/cierresDiarios"
    try:
        resposta = requests.post(url_api_externa, data=fechamento, headers=headers)
        resposta.raise_for_status()
        logger.info(
            "Fechamento enviado com sucesso. Status code: %s", resposta.status_code
        )
        logger.info(resposta.text)
        logger.info(fechamento)
        print("Fechamento enviado com sucesso. Status code:", resposta.status_code)
        print(resposta.text)
        print(fechamento)
    except requests.exceptions.HTTPError as err:
        logger.error(
            "Falha ao enviar fechamento. Status code: %s", err.response.status_code
        )
        logger.error("Detalhes do erro: %s", err.response.text)
        logger.error(fechamento)
        print("Falha ao enviar fechamento. Status code:", err.response.status_code)
        print("Detalhes do erro:", err.response.text)
        print(fechamento)
    except requests.exceptions.RequestException as err:
        logger.error("Erro de conexão ao enviar fechamento: %s", err)
        logger.error(fechamento)
        print("Erro de conexão ao enviar fechamento:", err)
        print(fechamento)

    return fechamento


def get_solicitacoes_reenvio():
    lista_solicitacoes: Solicitacoes = []

    try:
        url_api_externa = (
            f"{url_base}/v2/minoristas/{idEmpresa}/locales/{idLocal}/solicitudes"
        )
        resposta = requests.get(url_api_externa, headers=headers)
        resposta.raise_for_status()
        lista_solicitacoes = [
            Solicitacoes.model_validate(s) for s in json.loads(resposta.text)
        ]

        logger.info(
            "Solicitações de reenvio obtidas com sucesso. %s solicitações obtidas.",
            len(lista_solicitacoes),
        )
        logger.info(lista_solicitacoes)
        print(
            "Solicitações de reenvio obtidas com sucesso. %s solicitações obtidas.",
            len(lista_solicitacoes),
        )
        print(lista_solicitacoes)
    except requests.exceptions.HTTPError as err:
        logger.error(
            "Falha ao obter solicitações de reenvio. Status code: %s",
            err.response.status_code,
        )
        logger.error("Detalhes do erro: %s", err.response.text)
        print(
            "Falha ao obter solicitações de reenvio. Status code:",
            err.response.status_code,
        )
        print("Detalhes do erro:", err.response.text)

    return lista_solicitacoes
