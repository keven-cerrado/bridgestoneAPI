import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

schema = os.getenv("PG_SCHEMA")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"options": "-c search_path=dbo,{schema}".format(schema=schema)})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
