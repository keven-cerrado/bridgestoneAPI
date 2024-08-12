import threading
from fastapi import FastAPI, Depends
from app.routers.faturamento.scriptSend import iniciar_agendamento
from .routers.login import login
from .routers.faturamento import faturamento
from .database import SessionLocal

app = FastAPI()

print("Iniciando aplicação...")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# app.include_router(login.router)
app.include_router(faturamento.router)

print("Iniciando aplicação...")


# Função para ser chamada no evento de startup
def iniciar_agendamento_thread():
    try:
        iniciar_agendamento()
    except Exception as e:
        print(f"Erro ao iniciar agendamento: {e}")


print("Iniciando aplicação...")
# Adicionar o evento de startup
app.add_event_handler(
    "startup", lambda: threading.Thread(target=iniciar_agendamento_thread).start()
)
