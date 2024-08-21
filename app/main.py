import threading
from fastapi import FastAPI, Depends
from app.routers.faturamento.scriptSend import iniciar_agendamento
from .routers.login import login
from .routers.faturamento import faturamento
from .routers.envios import envios
from .database import SessionLocal
import ssl

app = FastAPI()


# Dependency
def get_db():
    """
    Retorna uma instância do banco de dados.

    Retorna uma instância do banco de dados que pode ser usada para realizar operações de leitura e escrita.
    Certifica-se de fechar a conexão com o banco de dados quando a função é concluída ou ocorre uma exceção.

    Returns:
        db: Uma instância do banco de dados.

    """
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
app.include_router(envios.router)


# # Função para ser chamada no evento de startup
# def iniciar_agendamento_thread():
#     print("Iniciando agendamento...")
#     try:
#         iniciar_agendamento()
#     except Exception as e:
#         print(f"Erro ao iniciar agendamento: {e}")


# Adicionar o evento de startup
# app.add_event_handler(
#     "startup", lambda: threading.Thread(target=iniciar_agendamento_thread).start()
# )
