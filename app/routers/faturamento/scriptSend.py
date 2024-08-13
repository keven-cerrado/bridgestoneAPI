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
)


bot = Bot(token=os.getenv("BOT_TOKEN_TELEGRAM"))


def tarefa_periodica_envio_faturamento(filial: str = None):
    db = SessionLocal()
    try:
        for filial in filiais:
            envio = enviar_faturamento_para_api_externa(db, filial=filial)
            return envio
        # print("Enviando faturamento...")
    finally:
        db.close()


def tarefa_periodica_verificacao_cancelamentos(filial: str = None):
    db = SessionLocal()
    try:
        for filial in filiais:
            verificar_cancelamentos_enviar(db, filial=filial)
    finally:
        db.close()


def tarefa_periodica_verificacao_devolucoes(filial: str = None):
    db = SessionLocal()
    try:
        for filial in filiais:
            verificar_devolucoes(db, filial=filial)
    finally:
        db.close()


async def send_message(message):
    await bot.send_message(chat_id=-4209916479, text=message)


async def verificar_reenvio(filial: str = None):
    for filial in filiais:
        solicitacoes = get_solicitacoes_reenvio(filial=filial)
        if solicitacoes:
            qtd_solicitacoes = len(solicitacoes)
            await send_message(
                f"Existem {qtd_solicitacoes} solicitações de reenvio pendentes. Centro: {filial}"
                + "\n\n".join([f"{solicitacao}" for solicitacao in solicitacoes])
            )
        return solicitacoes


def start_verificacao_reenvio():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    reenvios = loop.run_until_complete(verificar_reenvio())
    return reenvios


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
