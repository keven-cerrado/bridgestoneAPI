import asyncio
import os
import schedule
import time
from telegram import Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from app.database import SessionLocal
from app.routers.faturamento.utils import (
    enviar_faturamento_para_api_externa,
    get_solicitacoes_reenvio,
)


bot = Bot(token=os.getenv("BOT_TOKEN_TELEGRAM"))


def tarefa_periodica():
    db = SessionLocal()
    try:
        enviar_faturamento_para_api_externa(db)
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
    # Agendar a tarefa para ser executada a cada dia às 22:00
    # schedule.every().day.at("22:00").do(tarefa_periodica)
    # schedule.every(2).seconds.do(tarefa_periodica)
    # schedule.every().day.at("22:00").do(start_verificacao_reenvio)
    start_verificacao_reenvio()
    # schedule.every(2).seconds.do(start)

    while True:
        schedule.run_pending()
        time.sleep(5)
