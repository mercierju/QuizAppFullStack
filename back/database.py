import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#Docker
engine = create_engine(os.environ['DATABASE_URL'])

#Local
#engine = create_engine("postgresql://postgres:postgres@localhost:5432/quiz")

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base = declarative_base()