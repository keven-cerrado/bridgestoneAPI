from datetime import datetime, timedelta
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import List
import requests
from sqlalchemy.orm import Session
from app.log_config import setup_logger
from .crud import get_faturamento_per_date, get_fechamento_per_date
from .models import Envios, ItemFaturamento
from .schemas import ModelScannTech, Fechamento, Solicitacoes
from app.configuracoes import (
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
    data_inicial: str = None,
    data_final: str = None,
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
    faturamento_numeros = [f.numero for f in faturamentos]
    faturamentos_json = [json.loads(f.model_dump_json()) for f in faturamentos]
    faturamentos_json = json.dumps(faturamentos_json)

    try:
        envio = Envios()
        db.add(envio)
        db.commit()
        db.refresh(envio)
        # idBd = envio.id
    except Exception as e:
        logger.error(f"Erro ao salvar envio: {e}")
        print(f"Erro ao salvar envio: {e}")
        db.rollback()
        return

    url_api_externa = f"{url_base}/v2/minoristas/{idEmpresa}/locales/{idLocal}/cajas/{idCaja}/movimientos/lotes"
    try:
        resposta = requests.post(
            url_api_externa, data=faturamentos_json, headers=headers
        )
        resposta.raise_for_status()
        # preenche o idLote no envio
        envio.id_lote = resposta.json()["idLote"]
        envio.conteudo = faturamentos_json
        envio.data_envio = datetime.now()
        envio.enviado = True
        envio.lista_notas = faturamento_numeros
        db.commit()
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
            "Falha ao enviar fechamento. Status code:", err.response.status_code
        )
        logger.error("Detalhes do erro: %s", err.response.text)
        logger.error(fechamento)
        print("Falha ao enviar fechamento. Status code:", err.response.status_code)
        print("Detalhes do erro:", err.response.text)
        print(fechamento)
    except requests.exceptions.RequestException as err:
        logger.error(f"Erro de conexão ao enviar fechamento: {err}")
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
            f"Solicitações de reenvio obtidas com sucesso. {len(lista_solicitacoes)} solicitações obtidas.",
        )
        logger.info(lista_solicitacoes)
        print(
            f"Solicitações de reenvio obtidas com sucesso. {len(lista_solicitacoes)} solicitações obtidas."
        )
        print(lista_solicitacoes)
    except requests.exceptions.HTTPError as err:
        logger.error(
            f"Falha ao obter solicitações de reenvio. Status code: {err.response.status_code}",
        )
        logger.error(f"Detalhes do erro: {err.response.text}")
        print(
            "Falha ao obter solicitações de reenvio. Status code:",
            err.response.status_code,
        )
        print("Detalhes do erro:", err.response.text)

    return lista_solicitacoes


def verificar_cancelamentos_enviar(
    db: Session,
):
    data_atual = datetime.now().date()
    data_inicial = data_atual - timedelta(days=1) if data_atual.day == 1 else data_atual
    data_final = datetime.now().date()
    try:
        envios = db.query(Envios).filter(
            Envios.enviado.isnot(None)
            & Envios.devolucao_cancelamento.is_(None)
            & Envios.data_envio.between(data_inicial, data_final)
        )
        envios_devolucoes = db.query(Envios).filter(
            Envios.devolucao_cancelamento.isnot(None)
            & Envios.data_envio.between(data_inicial, data_final)
        )

        # envio.lista_notas = "{60905,31352,60906,60909,60908,31354,60907,60910,10534,15945,16647,11388,30833}""
        # primeiro preciso transformar ela em uma lista de notas
        notas = []
        notas_devolvidas = []
        for envio in envios:
            notas_envio = (
                (envio.lista_notas if envio.lista_notas else "")
                .replace("{", "")
                .replace("}", "")
                .split(",")
            )
            notas.extend(notas_envio)

        for envio_devolucao in envios_devolucoes:
            notas_devolucao = (
                (envio_devolucao.lista_notas if envio_devolucao.lista_notas else "")
                .replace("{", "")
                .replace("}", "")
                .split(",")
            )
            notas_devolvidas.extend(notas_devolucao)

        notas = filter(None, notas)
        notas = filter(lambda nota: nota not in notas_devolvidas, notas)
        notas_devolvidas = list(filter(None, notas_devolvidas))

        notas_enviadas = get_faturamento_per_date(
            db,
            data_inicial.strftime("%d/%m/%Y"),
            data_final.strftime("%d/%m/%Y"),
            filtrar_canceladas=False,
        )
        notas_canceladas = []
        numeros_notas_canceladas = []
        devolucao = Fechamento(
            fechaVentas=data_atual,
            montoVentaLiquida=0.0,
            montoCancelaciones=0.0,
            cantidadMovimientos=0,
            cantidadCancelaciones=0,
        )
        for numero in notas:
            nota = next((n for n in notas_enviadas if n.numero == numero), None)
            if nota and nota.cancelacion:
                devolucao.montoVentaLiquida += nota.total * -1
                devolucao.montoCancelaciones += nota.total
                devolucao.cantidadCancelaciones += 1
                notas_canceladas.append(nota)
                numeros_notas_canceladas.append(numero)

    except Exception as e:
        print(e)

    try:
        envio = Envios(
            devolucao_cancelamento=True,
        )
        db.add(envio)
        db.commit()
        db.refresh(envio)
        # idBd = envio.id
    except Exception as e:
        logger.error(f"Erro ao salvar envio: {e}")
        print(f"Erro ao salvar envio: {e}")
        db.rollback()
        return

    # enviar fechamento de cancelamentos para a API externa
    url_api_externa = f"{url_base}/v2/minoristas/{idEmpresa}/locales/{idLocal}/cajas/{idCaja}/cierresDiarios"
    try:
        devolucao_json = json.loads(devolucao.model_dump_json())
        devolucao_json = json.dumps(devolucao_json)
        resposta = requests.post(url_api_externa, data=devolucao_json, headers=headers)
        resposta.raise_for_status()
        envio.conteudo = devolucao_json
        envio.data_envio = datetime.now()
        envio.enviado = True
        envio.lista_notas = numeros_notas_canceladas
        db.commit()
        logger.info(
            "Fechamento de cancelamentos enviado com sucesso. Status code: %s",
            resposta.status_code,
        )
        logger.info(resposta.text)
        logger.info(devolucao)
        print(
            "Fechamento de cancelamentos enviado com sucesso. Status code:",
            resposta.status_code,
        )
        print(resposta.text)
        print(devolucao)
    except requests.exceptions.HTTPError as err:
        logger.error(
            "Falha ao enviar fechamento de cancelamentos. Status code: %s",
            err.response.status_code,
        )
        logger.error("Detalhes do erro: %s", err.response.text)
        logger.error(devolucao)
        print(
            "Falha ao enviar fechamento de cancelamentos. Status code:",
            err.response.status_code,
        )
        print("Detalhes do erro:", err.response.text)
        print(devolucao)
    except requests.exceptions.RequestException as err:
        logger.error("Erro de conexão ao enviar fechamento de cancelamentos: %s", err)
        logger.error(devolucao)
        print("Erro de conexão ao enviar fechamento de cancelamentos:", err)
        print(devolucao)


def verificar_devolucoes(
    db: Session,
):

    data_atual = datetime.now().date()
    data_inicial = data_atual - timedelta(days=1) if data_atual.day == 1 else data_atual
    data_final = datetime.now().date()

    devolucoes = (
        db.query(ItemFaturamento)
        .filter(
            ItemFaturamento.COMISSAO_TIPO.like("DEVOLUCOES")
            & ItemFaturamento.CANCELADA.is_(None)
            & ItemFaturamento.DATA_CRIADA.between(data_inicial, data_final)
        )
        .order_by(ItemFaturamento.DATA_CRIADA.desc())
        .all()
    )

    devolucao = Fechamento(
        fechaVentas=data_atual,
        montoVentaLiquida=0.0,
        montoCancelaciones=0.0,
        cantidadMovimientos=0,
        cantidadCancelaciones=0,
    )

    lista_notas = []

    for dev in devolucoes:
        devolucao.montoVentaLiquida += dev.TOTAL * -1
        devolucao.montoCancelaciones += dev.TOTAL
        devolucao.cantidadMovimientos += 1
        devolucao.cantidadCancelaciones += 1
        lista_notas.append(dev.NUMERO_NOTA)

    try:
        envio = Envios(
            devolucao_cancelamento=True,
        )
        db.add(envio)
        db.commit()
        db.refresh(envio)
        # idBd = envio.id
    except Exception as e:
        logger.error(f"Erro ao salvar envio: {e}")
        print(f"Erro ao salvar envio: {e}")
        db.rollback()
        return

    url_api_externa = f"{url_base}/v2/minoristas/{idEmpresa}/locales/{idLocal}/cajas/{idCaja}/cierresDiarios"

    try:
        devolucao_json = json.loads(devolucao.model_dump_json())
        devolucao_json = json.dumps(devolucao_json)
        resposta = requests.post(url_api_externa, data=devolucao_json, headers=headers)
        resposta.raise_for_status()
        envio.conteudo = devolucao_json
        envio.data_envio = datetime.now()
        envio.enviado = True
        envio.lista_notas = lista_notas
        db.commit()
        logger.info(
            "Fechamento de devoluções enviado com sucesso. Status code: %s",
            resposta.status_code,
        )
        logger.info(resposta.text)
        logger.info(devolucao)
        print(
            "Fechamento de devoluções enviado com sucesso. Status code: %s",
            resposta.status_code,
        )
        print(resposta.text)
        print(devolucao)
    except requests.exceptions.HTTPError as err:
        logger.error(
            "Falha ao enviar fechamento de devoluções. Status code: %s",
            err.response.status_code,
        )
        logger.error("Detalhes do erro: %s", err.response.text)
        logger.error(devolucao)
        print(
            "Falha ao enviar fechamento de devoluções. Status code: %s",
            err.response.status_code,
        )
        print("Detalhes do erro:", err.response.text)
        print(devolucao)
    except requests.exceptions.RequestException as err:
        logger.error("Erro de conexão ao enviar fechamento de devoluções: %s", err)
        logger.error(devolucao)
        print("Erro de conexão ao enviar fechamento de devoluções:", err)
        print(devolucao)
