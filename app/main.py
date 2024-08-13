import threading
from fastapi import FastAPI, Depends
from app.routers.faturamento.scriptSend import iniciar_agendamento
from .routers.login import login
from .routers.faturamento import faturamento
from .database import SessionLocal
import ssl

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ssl
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain("./app/cert/cert.pem", "./app/cert/key.pem")


# app.include_router(login.router)
app.include_router(faturamento.router)


# # Função para ser chamada no evento de startup
# def iniciar_agendamento_thread():
#     print("Iniciando agendamento...")
#     try:
#         iniciar_agendamento()
#     except Exception as e:
#         print(f"Erro ao iniciar agendamento: {e}")


# # Adicionar o evento de startup
# app.add_event_handler(
#     "startup", lambda: threading.Thread(target=iniciar_agendamento_thread).start()
# )
