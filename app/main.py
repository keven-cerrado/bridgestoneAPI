import threading
from fastapi import FastAPI, Depends
from fastapi.concurrency import asynccontextmanager
from app.routers.faturamento.scriptSend import iniciar_agendamento
from .routers.login import login
from .routers.faturamento import faturamento
from .database import SessionLocal

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# app.include_router(login.router)
app.include_router(faturamento.router)


# Função para ser chamada no evento de startup
def iniciar_agendamento_thread():
    try:
        iniciar_agendamento()
    except Exception as e:
        print(f"Erro ao iniciar agendamento: {e}")


# Adicionar o evento de startup
# app.add_event_handler(
#     "startup", lambda: threading.Thread(target=iniciar_agendamento_thread).start()
# )
# @app.on_event("startup")
# def startup_event():
#     threading.Thread(target=iniciar_agendamento_thread, daemon=True).start()


# Usar um lifespan handler para gerenciar o ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar agendamento na thread no startup
    threading.Thread(target=iniciar_agendamento_thread, daemon=True).start()
    yield
    # Código de cleanup, se necessário, pode ser adicionado aqui


app.router.lifespan_context = lifespan
