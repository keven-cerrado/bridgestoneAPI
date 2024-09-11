import asyncio
import os
import schedule
import time
from telegram import Bot
from ...configuracoes import (
    hora_envio_faturamento,
    hora_verificacao_reenvio,
    hora_verificacao_cancelamentos,
    hora_verificacao_devolucoes,
    filiais,
)

from app.database import SessionLocal
from app.routers.faturamento.faturamento import get_db
from app.routers.faturamento.utils import (
    enviar_faturamento_para_api_externa,
    get_solicitacoes_reenvio,
    verificar_cancelamentos_enviar,
    verificar_devolucoes,
    enviar_fechamento_diario,
)


bot = Bot(token=os.getenv("BOT_TOKEN_TELEGRAM"))


def tarefa_periodica_envio_faturamento(
    centro: str = None, data_inicial: str = None, data_final: str = None
):
    """
    Esta função é responsável por enviar periodicamente as informações de faturamento para uma API externa de uma determinada filial.

    Parâmetros:
    - filial (str): A filial para a qual as informações de faturamento devem ser enviadas. Se não for fornecida, a função enviará as informações de faturamento para todas as filiais.

    Retorna:
    - envios (list): Uma lista contendo os resultados do processo de envio das informações de faturamento para cada filial.

    Lança:
    - Exception: Se ocorrer um erro ao enviar as informações de faturamento.

    """
    db = SessionLocal()
    try:
        envios = []
        # Para cada filial, envia as informações de faturamento separadamente
        for filial in filiais if not centro else [centro]:
            envio = enviar_faturamento_para_api_externa(
                db, filial=filial, data_inicial=data_inicial, data_final=data_final
            )
            envios.append(envio)
            print(f"Enviando faturamento da filial {filial}")
        return envios
    except Exception as e:
        print(f"Erro ao enviar faturamento: {e}")
        return []
    finally:
        db.close()


def tarefa_periodica_envio_fechamento(
    centro: str = None, data_inicial: str = None, data_final: str = None
):
    """
    Envia o fechamento diário para a filial especificada.

    Parâmetros:
    - filial (str): A filial para a qual o fechamento será enviado. Se não for especificada, será enviado para todas as filiais.

    Retorna:
    - envios (list): Uma lista dos fechamentos enviados.

    Lança:
    - Exception: Se ocorrer um erro ao enviar o fechamento.
    """
    db = SessionLocal()
    try:
        envios = []
        # Para cada filial, envia o fechamento diário
        for filial in filiais if not centro else [centro]:
            envio = enviar_fechamento_diario(
                db, filial=filial, data_inicial=data_inicial, data_final=data_final
            )
            envios.append(envio)
            print(f"Enviando fechamento da filial {filial}")
        return envios
    except Exception as e:
        print(f"Erro ao enviar fechamento: {e}")
        return []


def tarefa_periodica_verificacao_cancelamentos(centro: str = None):
    """
    Função responsável por realizar a verificação periódica de cancelamentos e enviar os dados para processamento.

    Parâmetros:
    - filial (str): Opcional. Filial específica a ser verificada. Caso não seja fornecida, serão verificadas todas as filiais.

    Retorna:
    - cancelamentos (list): Lista contendo os cancelamentos verificados para cada filial. Caso ocorra algum erro durante a verificação, uma lista vazia será retornada.

    Comportamento:
    - Inicializa uma conexão com o banco de dados.
    - Inicializa uma lista vazia para armazenar os cancelamentos.
    - Para cada filial fornecida ou todas as filiais, realiza a verificação de cancelamentos e adiciona o resultado à lista de cancelamentos.
    - Retorna a lista de cancelamentos.
    - Em caso de exceção, imprime o erro ocorrido e retorna uma lista vazia.
    - Fecha a conexão com o banco de dados.

    """
    db = SessionLocal()
    try:
        cancelamentos = []
        for filial in filiais if not centro else [centro]:
            cancelamento = verificar_cancelamentos_enviar(db, filial=filial)
            cancelamentos.append(cancelamento)
        return cancelamentos
    except Exception as e:
        print(f"Erro ao verificar cancelamentos: {e}")
        return []
    finally:
        db.close()


def tarefa_periodica_verificacao_devolucoes(centro: str = None):
    """
    Função responsável por realizar a verificação periódica de devoluções em uma determinada filial.

    Parâmetros:
    - filial (str): Opcional. O código da filial a ser verificada. Se não for fornecido, serão verificadas todas as filiais.

    Retorna:
    - devolucoes (list): Uma lista contendo as devoluções encontradas em cada filial verificada.

    Exceções:
    - Exception: Caso ocorra algum erro durante a verificação das devoluções.

    Observações:
    - A função utiliza uma conexão com o banco de dados local.
    - Caso ocorra algum erro durante a verificação das devoluções, a função retorna uma lista vazia.
    - A conexão com o banco de dados é fechada ao final da execução da função.
    """
    db = SessionLocal()
    try:
        devolucoes = []
        for filial in filiais if not centro else [centro]:
            devolucao = verificar_devolucoes(db, filial=filial)
            devolucoes.append(devolucao)
        return devolucoes
    except Exception as e:
        print(f"Erro ao verificar devoluções: {e}")
        return []
    finally:
        db.close()


async def send_message(message):
    """
    Envia uma mensagem para um chat específico.

    Parâmetros:
    - message (str): A mensagem a ser enviada.

    Retorna:
    - None

    Exemplo de uso:
    ```
    await send_message("Olá, mundo!")
    ```
    """
    await bot.send_message(chat_id=-4209916479, text=message)


async def verificar_reenvio(centro: str = None):
    """
    Verifica se há solicitações de reenvio pendentes para uma determinada filial.

    Parâmetros:
    - filial (str): O código da filial para a qual deseja verificar as solicitações de reenvio. Se nenhum valor for fornecido, todas as filiais serão verificadas.

    Retorna:
    - resultado (list): Uma lista contendo as solicitações de reenvio pendentes encontradas.

    Exceções:
    - Exception: Se ocorrer algum erro durante a verificação de reenvio.

    Descrição:
    Esta função verifica se há solicitações de reenvio pendentes para uma determinada filial ou para todas as filiais, se nenhum valor for fornecido. Ela obtém as solicitações de reenvio usando a função get_solicitacoes_reenvio e, se houver solicitações encontradas, envia uma mensagem contendo a quantidade de solicitações e os detalhes de cada uma delas. Em seguida, retorna uma lista contendo todas as solicitações de reenvio pendentes encontradas.

    Se ocorrer algum erro durante a verificação de reenvio, a função captura a exceção e a imprime, retornando uma lista vazia como resultado.

    """
    resultado = []
    tipos = ["movimientos", "cierresDiarios"]
    try:
        for filial in filiais if not centro else [centro]:
            for tipo in tipos:
                solicitacoes = get_solicitacoes_reenvio(filial=filial, tipo=tipo)
                if solicitacoes:
                    qtd_solicitacoes = len(solicitacoes)
                    await send_message(
                        f"Existem {qtd_solicitacoes} solicitações de reenvio pendentes. filial: {filial}"
                        + "\n\n".join(
                            [f"{solicitacao}" for solicitacao in solicitacoes]
                        )
                    )
                    resultado.extend(solicitacoes)
        return resultado
    except Exception as e:
        print(f"Erro ao verificar reenvio: {e}")
        return resultado


def start_verificacao_reenvio(
    centro: str = None,
):
    """
    Função responsável por iniciar a verificação de reenvio.

    Essa função cria um novo loop de eventos assíncronos e define-o como o loop atual.
    Em seguida, executa a função verificar_reenvio de forma assíncrona no loop criado.
    O resultado da verificação de reenvio é retornado como resultado da função.

    Ela era necessário para chamar a funcao de verificacao de reenvio no evento de agendamento, mas não está sendo usada.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    reenvios = loop.run_until_complete(verificar_reenvio(centro=centro))
    return reenvios


# Função que seria usada para fazer os agendamentos, mas não está sendo usada
# Agendamentos sendo feitos pelo N8N
def iniciar_agendamento():
    # print("Iniciando agendamento...")
    # print(
    #     f"Horário de envio de faturamento e verificação de cancelamentos: {hora_envio_faturamento}"
    # )
    # print(f"Horário de verificação de reenvio: {hora_verificacao_reenvio}")
    # print(f"Horário de verificação de devoluções: {hora_verificacao_devolucoes}")

    # schedule.every().day.at(hora_envio_faturamento).do(
    #     tarefa_periodica_envio_faturamento
    # )
    # schedule.every().day.at(hora_verificacao_reenvio).do(
    #     start_verificacao_reenvio
    # )
    # schedule.every().day.at(hora_verificacao_cancelamentos).do(
    #     tarefa_periodica_verificacao_cancelamentos
    # )
    # schedule.every().day.at(hora_verificacao_devolucoes).do(
    #     tarefa_periodica_verificacao_devolucoes
    # )

    # tarefa_periodica_envio_faturamento()
    # time.sleep(30)
    # tarefa_periodica_verificacao_cancelamentos()
    # time.sleep(30)
    # start_verificacao_reenvio()
    # time.sleep(30)
    # tarefa_periodica_verificacao_devolucoes()
    # time.sleep(30)
    # tarefa_periodica_envio_faturamento()
    # time.sleep(60)
    # tarefa_periodica_verificacao_cancelamentos()
    # time.sleep(60)
    # start_verificacao_reenvio()
    # time.sleep(60)
    # tarefa_periodica_verificacao_devolucoes()

    while True:
        schedule.run_pending()
        time.sleep(5)
