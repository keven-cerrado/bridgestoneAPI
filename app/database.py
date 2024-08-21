import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

"""
Módulo de Banco de Dados

Este módulo contém a configuração e a inicialização do banco de dados utilizado pela aplicação.

Variáveis:
- SQLALCHEMY_DATABASE_URL: A URL de conexão com o banco de dados.
- schema: O esquema do banco de dados.
- engine: O objeto de conexão com o banco de dados.
- SessionLocal: A classe de sessão do banco de dados.
- Base: A classe base para a definição de modelos do banco de dados.
"""

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

schema = os.getenv("PG_SCHEMA")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"options": "-c search_path=dbo,{schema}".format(schema=schema)})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
