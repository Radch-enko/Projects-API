from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

LOCAL_SQLALCHEMY_DATABASE_URL = "postgresql://postgres@localhost:5432/projects?client_encoding=utf8"
DEV_SQLALCHEMY_DATABASE_URL = "postgresql://robtwxhuwoquuq:7a4f9ac896eb0efe21381d84d3711abfebaf2377ad404edd7db92729685a5428@ec2-52-71-23-11.compute-1.amazonaws.com:5432/daopggc629urvq"
SQLALCHEMY_DATABASE_URL = "postgresql://ppqjemqmbcfweh:b93424410e16e426d20b0f8e407b71323f3710ae148b1d85ab49f464f0f73905@ec2-44-195-169-163.compute-1.amazonaws.com:5432/df2bisqg0k6hmf"

engine = create_engine(
    DEV_SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    client_encoding="utf8"
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()