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


def tarefa_periodica_envio_faturamento():
    db = SessionLocal()
    try:
        enviar_faturamento_para_api_externa(db)
        verificar_cancelamentos_enviar(db)
    finally:
        db.close()


async def send_message(message):
    await bot.send_message(chat_id=-4209916479, text=message)


async def verificar_reenvio():
    solicitacoes = get_solicitacoes_reenvio()
    if solicitacoes:
        qtd_solicitacoes = len(solicitacoes)
        await send_message(
            f"Existem {qtd_solicitacoes} solicitações de reenvio pendentes."
        )


def start_verificacao_reenvio():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(verificar_reenvio())


def iniciar_agendamento():
    print("Iniciando agendamento...")
    schedule.every().day.at(hora_envio_faturamento).do(
        tarefa_periodica_envio_faturamento
    )
    schedule.every().day.at(hora_verificacao_reenvio).do(start_verificacao_reenvio)
    schedule.every().day.at(hora_verificacao_cancelamentos).do(
        verificar_cancelamentos_enviar
    )
    schedule.every().day.at(hora_verificacao_devolucoes).do(verificar_devolucoes)
    # tarefa_periodica_envio_faturamento()
    # start_verificacao_reenvio()
    # verificar_cancelamentos_enviar()

    while True:
        schedule.run_pending()
        time.sleep(5)
