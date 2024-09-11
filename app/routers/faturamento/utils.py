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
    filial: str = None,
):
    """
    Envia dados de faturamento para uma API externa.

    Parâmetros:
    - db (Session): Sessão do banco de dados para realizar operações de leitura e gravação.
    - data_inicial (str, opcional): Data inicial para filtrar os faturamentos. Se não fornecida, usa a data atual.
    - data_final (str, opcional): Data final para filtrar os faturamentos. Se não fornecida, usa a data atual.
    - agrupar_outros_flag (bool): Flag para determinar se outros itens devem ser agrupados.
    - filial (str, opcional): Código da filial para filtrar os faturamentos.

    Retorna:
    - List[ModelScannTech]: Lista de objetos de faturamento enviados.

    Descrição:
    Esta função recupera os dados de faturamento de acordo com o período especificado e, em seguida,
    envia esses dados para uma API externa. A função também realiza o registro do envio no banco de dados
    e trata possíveis erros durante o processo de envio.

    Passos:
    1. Recupera os dados de faturamento para as datas fornecidas ou para a data atual se as datas não forem especificadas.
    2. Converte os dados de faturamento em formato JSON.
    3. Tenta registrar o envio no banco de dados local. Se falhar, faz o rollback e termina a função.
    4. Tenta enviar os dados de faturamento para a API externa.
    5. Se o envio for bem-sucedido, atualiza o registro no banco de dados com informações adicionais como idLote e data de envio.
    6. Caso ocorram erros HTTP ou de conexão, os erros são logados e impressos.
    7. Retorna a lista de faturamentos enviados.

    Exceções tratadas:
    - `requests.exceptions.HTTPError`: Erros relacionados a respostas HTTP.
    - `requests.exceptions.RequestException`: Erros gerais de requisições HTTP.
    - `Exception`: Erros gerais ao salvar o envio no banco de dados.

    Logs:
    - A função registra logs de sucesso e falhas, incluindo detalhes como status code e conteúdo JSON enviado.
    """
    current_date = datetime.now().strftime("%d/%m/%Y")

    # Get the faturamentos for the current date
    # faturamentos = get_faturamento_per_date(db, current_date, current_date)
    faturamentos: List[ModelScannTech] = get_faturamento_per_date(
        db,
        (data_inicial if data_inicial else current_date),
        (data_final if data_final else current_date),
        agrupar_outros=agrupar_outros_flag,
        filial=filial,
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

    url_api_externa = f"{url_base}/v2/minoristas/{idEmpresa}/locales/{filial}/cajas/{idCaja}/movimientos/lotes"
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
            "Faturamento enviado com sucesso. %s notas enviadas do centro %s. Status code: %s",
            len(faturamentos),
            resposta.status_code,
            filial,
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
    data_inicial: str = None,
    data_final: str = None,
    agrupar_outros_flag: bool = agrupar_outros_flag,
    filial: str = None,
):
    """
    Envia os dados de fechamento diário para uma API externa.

    Parâmetros:
    - db (Session): Sessão do banco de dados para realizar operações de leitura.
    - data_inicial (str, opcional): Data inicial para filtrar o fechamento. Se não fornecida, usa a data atual.
    - data_final (str, opcional): Data final para filtrar o fechamento. Se não fornecida, usa a data atual.
    - agrupar_outros_flag (bool): Flag para determinar se outros itens devem ser agrupados.
    - filial (str, opcional): Código da filial para filtrar o fechamento.

    Retorna:
    - Fechamento: Objeto de fechamento diário enviado.

    Descrição:
    Esta função recupera os dados de fechamento diário de acordo com o período especificado e os envia para uma API externa.
    O fechamento é recuperado a partir da base de dados e enviado para uma API que processa o fechamento diário. A função também
    realiza tratamento de erros relacionados ao envio e registro de logs.

    Passos:
    1. Recupera os dados de fechamento diário para as datas fornecidas ou para a data atual se as datas não forem especificadas.
    2. Monta a URL da API externa utilizando informações de filial e caixa.
    3. Tenta enviar os dados de fechamento para a API externa.
    4. Se o envio for bem-sucedido, loga as informações de sucesso, incluindo o status code e o conteúdo do fechamento.
    5. Caso ocorram erros HTTP ou de conexão, os erros são logados e impressos.
    6. Retorna o objeto de fechamento enviado.

    Exceções tratadas:
    - `requests.exceptions.HTTPError`: Erros relacionados a respostas HTTP.
    - `requests.exceptions.RequestException`: Erros gerais de requisições HTTP.

    Logs:
    - A função registra logs de sucesso e falhas, incluindo detalhes como status code e o conteúdo do fechamento.
    """
    current_date = datetime.now().strftime("%d/%m/%Y")

    fechamento = get_fechamento_per_date(
        db=db,
        data_inicial=(data_inicial if data_inicial else current_date),
        data_final=(data_final if data_final else current_date),
        agrupar_outros=agrupar_outros_flag,
        filial=filial,
    )

    url_api_externa = f"{url_base}/v2/minoristas/{idEmpresa}/locales/{filial}/cajas/{idCaja}/cierresDiarios"
    try:
        fechamento_json = json.dumps(json.loads(fechamento.model_dump_json()))
        resposta = requests.post(url_api_externa, data=fechamento_json, headers=headers)
        resposta.raise_for_status()
        logger.info(
            "Fechamento enviado com sucesso. Status code: %s", resposta.status_code
        )
        logger.info(resposta.text)
        logger.info(fechamento_json)
        print("Fechamento enviado com sucesso. Status code:", resposta.status_code)
        print(resposta.text)
        print(fechamento_json)
    except requests.exceptions.HTTPError as err:
        logger.error(
            "Falha ao enviar fechamento. Status code: %s", err.response.status_code
        )
        logger.error("Detalhes do erro: %s", err.response.text)
    except requests.exceptions.RequestException as err:
        logger.error(f"Erro de conexão ao enviar fechamento: {err}")
        logger.error(fechamento_json)
        print("Erro de conexão ao enviar fechamento:", err)
        print(fechamento_json)

    return fechamento


def get_solicitacoes_reenvio(
    filial: str = None,
    tipo: str = None,
):
    """
    Obtém solicitações de reenvio de uma API externa.

    Parâmetros:
    - filial (str, opcional): Código da filial para filtrar as solicitações de reenvio.

    Retorna:
    - List[Solicitacoes]: Lista de objetos de solicitações de reenvio obtidos da API externa.

    Descrição:
    Esta função faz uma requisição GET a uma API externa para obter uma lista de solicitações de reenvio.
    As solicitações são filtradas pelo código da filial, se fornecido. A função trata erros HTTP durante a
    requisição e registra logs informando o sucesso ou falha da operação.

    Passos:
    1. Constrói a URL da API externa usando o código da filial fornecido.
    2. Faz uma requisição GET à API externa para obter as solicitações de reenvio.
    3. Converte a resposta JSON da API em uma lista de objetos `Solicitacoes`.
    4. Registra logs e imprime o número de solicitações obtidas e os detalhes dessas solicitações.
    5. Em caso de erro HTTP, registra os detalhes do erro e imprime as informações relevantes.
    6. Retorna a lista de solicitações obtidas, mesmo que vazia se ocorrer algum erro.

    Exceções tratadas:
    - `requests.exceptions.HTTPError`: Erros relacionados a respostas HTTP, incluindo status code e detalhes do erro.

    Logs:
    - A função registra logs do sucesso na obtenção das solicitações, incluindo o número de solicitações obtidas.
    - Em caso de erro, os logs incluem o status code e detalhes do erro retornado pela API.

    Exemplo de Uso:
    ```
    solicitacoes = get_solicitacoes_reenvio(filial="001")
    if solicitacoes:
        # Processa as solicitações de reenvio
    else:
        # Trata a ausência de solicitações
    ```
    """
    lista_solicitacoes: Solicitacoes = []

    try:
        url_api_externa = (
            f"{url_base}/v2/minoristas/{idEmpresa}/locales/{filial}/solicitudes/{tipo}"
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
    filial: str = None,
):
    """
    Verifica cancelamentos de notas fiscais e envia um fechamento diário para uma API externa.

    Parâmetros:
    - db (Session): Sessão do banco de dados utilizada para realizar consultas e operações.
    - filial (str, opcional): Código da filial para filtrar os envios e cancelamentos.

    Retorna:
    - Fechamento: Objeto de fechamento de cancelamentos enviado.

    Descrição:
    Esta função realiza a verificação de notas fiscais enviadas e seus cancelamentos no período determinado,
    e em seguida, envia um fechamento diário de cancelamentos para uma API externa. A função lida com a
    extração, validação e envio dos dados, além de registrar logs e tratar possíveis erros durante o processo.

    Passos:
    1. Define o período de data para a verificação de envios e cancelamentos.
    2. Consulta no banco de dados os envios que ocorreram dentro do período e aqueles que não possuem registro
       de devolução/cancelamento.
    3. Filtra e agrupa as notas fiscais enviadas, separando aquelas que foram canceladas.
    4. Cria um objeto de fechamento (`Fechamento`) com as informações agregadas de cancelamentos.
    5. Tenta salvar um novo registro de envio no banco de dados, identificando-o como uma devolução/cancelamento.
    6. Envia o fechamento de cancelamentos para a API externa.
    7. Se o envio for bem-sucedido, atualiza o registro no banco de dados com informações como conteúdo do envio,
       data de envio e notas fiscais associadas.
    8. Em caso de erro HTTP ou de conexão, os erros são logados e impressos.
    9. Retorna o objeto de fechamento enviado.

    Exceções tratadas:
    - `requests.exceptions.HTTPError`: Erros relacionados a respostas HTTP, incluindo status code e detalhes do erro.
    - `requests.exceptions.RequestException`: Erros gerais de conexão e requisições HTTP.
    - `Exception`: Erros gerais durante a consulta e manipulação dos dados no banco de dados.

    Logs:
    - A função registra logs detalhados sobre o sucesso ou falha na obtenção, processamento e envio de cancelamentos,
      incluindo status code, detalhes da resposta da API e o conteúdo do fechamento.

    Exemplo de Uso:
    ```
    fechamento = verificar_cancelamentos_enviar(db=session, filial="001")
    if fechamento:
        # Processa o fechamento retornado
    else:
        # Trata a ausência de cancelamentos
    ```
    """
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
            filial=filial,
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
    url_api_externa = f"{url_base}/v2/minoristas/{idEmpresa}/locales/{filial}/cajas/999/cierresDiarios"
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

    return devolucao


def verificar_devolucoes(
    db: Session,
    filial: str = None,
):
    """
    Verifica devoluções de notas fiscais em um período específico e envia um fechamento diário para uma API externa.

    Parâmetros:
    - db (Session): Sessão do banco de dados utilizada para realizar consultas e operações.
    - filial (str, opcional): Código da filial para filtrar os envios de devoluções.

    Retorna:
    - Fechamento: Objeto de fechamento de devoluções enviado.

    Descrição:
    Esta função verifica as devoluções de notas fiscais ocorridas em um período específico,
    cria um objeto de fechamento com os dados agregados dessas devoluções e envia as informações para uma API externa.

    Passos:
    1. Define o período de data para a verificação de devoluções.
    2. Consulta no banco de dados todas as devoluções (`ItemFaturamento`) que ocorreram no período definido e que não foram canceladas.
    3. Cria um objeto de fechamento (`Fechamento`) e agrega as informações das devoluções, como valores e quantidade de devoluções.
    4. Tenta salvar um novo registro de envio no banco de dados, identificando-o como uma devolução/cancelamento.
    5. Envia o fechamento de devoluções para a API externa.
    6. Se o envio for bem-sucedido, atualiza o registro no banco de dados com informações como o conteúdo do envio, data de envio e notas fiscais associadas.
    7. Em caso de erro HTTP ou de conexão, os erros são logados e impressos.
    8. Retorna o objeto de fechamento enviado.

    Exceções tratadas:
    - `requests.exceptions.HTTPError`: Erros relacionados a respostas HTTP, incluindo status code e detalhes do erro.
    - `requests.exceptions.RequestException`: Erros gerais de conexão e requisições HTTP.
    - `Exception`: Erros gerais durante a consulta e manipulação dos dados no banco de dados.

    Logs:
    - A função registra logs detalhados sobre o sucesso ou falha na obtenção, processamento e envio de devoluções,
      incluindo status code, detalhes da resposta da API e o conteúdo do fechamento.

    Exemplo de Uso:
    ```
    fechamento_devolucoes = verificar_devolucoes(db=session, filial="001")
    if fechamento_devolucoes:
        # Processa o fechamento de devoluções retornado
    else:
        # Trata a ausência de devoluções
    ```
    """
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

    url_api_externa = f"{url_base}/v2/minoristas/{idEmpresa}/locales/{filial}/cajas/999/cierresDiarios"

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

    return devolucao
