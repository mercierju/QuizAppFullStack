from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from typing_extensions import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func
import openai
import random

# Configurez votre clé API OpenAI
openai.api_key = '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'

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChoiceBase(BaseModel):
    choice_text: str
    is_correct : bool

class QuestionBase(BaseModel):
    question_text: str
    choices : List[ChoiceBase]
    position : int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]



# Fonction pour générer une question et des choix de réponse avec GPT-3
def generate_question_and_choices(theme):
    prompt = f"Generate a question about {theme}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150
    )
    question_text = response.choices[0].text.strip()

    # Génération de 4 choix de réponse avec un correct et trois incorrects
    choices = [generate_choice(theme) for _ in range(4)]
    correct_choice = random.choice(choices)
    return question_text, choices, correct_choice

def generate_choice(theme):
    prompt = f"Generate a choice about {theme}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50
    )
    return response.choices[0].text.strip()

# Remplissage de la base de données
def fill_database():
    session = SessionLocal()

    themes = ["Docker", "API"]
    i = 0
    for theme in themes:
        
        question_text, choices, correct_choice = generate_question_and_choices(theme)

        # Enregistrement de la question dans la base de données
        question = models.Questions(question_text=question_text, position=i)
        session.add(question)
        session.commit()

        # Enregistrement des choix dans la base de données
        for choice_text in choices:
            is_correct = (choice_text == correct_choice)
            choice = models.Choices(choice_text=choice_text, is_correct=is_correct, question_id=question.id)
            session.add(choice)
            session.commit()
        i+=1



def is_table_empty():
    session = SessionLocal()
    try:
        result = session.query(models.Questions).first()
        return result is None
    finally:
        session.close()

@app.on_event("startup")
async def startup_event():
    if is_table_empty():
        fill_database()  
    else:
        print("La table n'est pas vide au démarrage.")


@app.get("/quiz_infos")
async def quiz_infos(db: db_dependency):
    size = db.query(models.Questions).count()
    scores = db.query(models.Users).order_by(models.Users.best_score.desc()).limit(5).all()
    
    # Convertissez les résultats en dictionnaires si nécessaire
    scores_data = [{"username": user.username, "score": user.best_score} for user in scores]
    
    return {"size": size, "scores": scores_data}


@app.get('/questions/{position}')
async def get_question(position: int, db : db_dependency):
    question = db.query(models.Questions).filter(models.Questions.position == position).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    answers =db.query(models.Choices).filter(models.Choices.question_id == question.id).all()
    return question, answers


@app.post('/participation')
async def add_participation(db: db_dependency, request: Request):
    print(f"Received request data: {await request.body()}")
    data = await request.json()
    answers = data.get('answers')
    user_id = data.get('clerkId')
    user_name = data.get('username')
    questions = db.query(models.Questions).order_by(models.Questions.position.asc()).all()
    if len(answers) != len(questions):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le nombre de réponses ne correspond pas au nombre de questions.")
    # Recherchez les positions des bonnes réponses pour chaque question
    id_good_answers = []
    for question in questions:
        question_answers_id = db.query(models.Choices.id).filter(models.Choices.is_correct == True, models.Choices.question_id == question.id).first()
        if question_answers_id:
            id_good_answers.append(question_answers_id[0])
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Réponse correcte introuvable pour une question.")
    # Comptez le nombre de bonnes réponses
    score = sum([1 for i in range(len(answers)) if answers[i] == id_good_answers[i]])
    # Vérifiez si l'utilisateur existe déjà
    user_record = db.query(models.Users).filter(models.Users.clerk_id == user_id).first()
    if user_record is None:
        # L'utilisateur n'existe pas, créez-le
        new_user = models.Users(clerk_id=user_id, best_score=score, username = user_name)
        db.add(new_user)
        db.commit()
    elif score > user_record.best_score:
        # Mettez à jour le score si le score de la participation est supérieur
        user_record.best_score = score
        db.commit()
    # Enregistrez la participation du joueur dans la base de données
    participation = models.Participation(score=score, clerk_id = user_id)
    db.add(participation)
    db.commit()
    db.refresh(participation)
    return participation
