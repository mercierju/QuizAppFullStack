from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

class Questions(Base):
    __tablename__ = "Questions"

    id = Column(Integer, primary_key=True, index = True)
    question_text = Column(String, index = True)
    position = Column(Integer, index = True)
    is_chatgpt = Column(Boolean, index = True )

class Choices(Base):
    __tablename__ = "Choix"

    id = Column(Integer, primary_key=True, index = True)
    choice_text = Column(String, index = True)
    is_correct = Column(Boolean, default = False)
    question_id = Column(Integer, ForeignKey("Questions.id"))

class Users(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key = True, index=True)
    username = Column(String, unique = True)
    clerk_id = Column(String)
    best_score = Column(Integer, index = True)

class Participation(Base):
    __tablename__ = "Participation"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String)
    score = Column(Integer)



