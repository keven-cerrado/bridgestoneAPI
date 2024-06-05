import os
from fastapi import FastAPI, Depends

from .routers.login import login

from .internal import admin
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
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    # dependencies=[Depends(get_token_header)],
    responses={418: {"description": ""}},
)
