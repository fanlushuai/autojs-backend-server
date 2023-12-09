from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# pip install mysql-connector-python

# for docker to get
connection_string = os.getenv("CONNECTION")
if connection_string == None:
    connection_string = "mysql+mysqlconnector://fls:fls@127.0.0.1:3306/test"
SQLALCHEMY_DATABASE_URL = connection_string

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# echo=True 打印sql日志
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
