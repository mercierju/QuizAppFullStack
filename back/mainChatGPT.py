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
import json

# Configurez votre clé API OpenAI
client = openai.OpenAI(api_key='key')

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

def generate_question_and_choices():

    prompt = [{'role': 'user', 'content' : "Je veux un résultat comme celui-ci mais pour plusieurs questions au format json : 'questions' : [{'theme': 'API', 'question_text': 'Qu'est-ce que signifie l'acronyme API?', 'choices': [ {'choice_text': 'a) Application Programming Interface', 'is_correct': true}, {'choice_text': 'b) Advanced Programming Interface', 'is_correct': false}, {'choice_text': 'c) Automated Processing Interface', 'is_correct': false}, {'choice_text': 'd) Application Process Integration', 'is_correct': false} ] }], Génère une question pour chacun de ces thèmes ('API','Docker', 'HTML') avec pour chaque question 4 choix possibles et une valeur True ou False en fonction de si le choix est le bon. Je veux que tout soit en français. Répond juste avec le json sans aucun texte."}]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt
    )
    out = response.choices[0].message.content
    print(response.choices[0].message.content)
    index_accolade = out.find('{')

    if index_accolade != -1:
        reponse = out[index_accolade:]


    return json.loads(reponse)

# Remplissage de la base de données
def fill_database():
    session = SessionLocal()
    data = generate_question_and_choices()
    position = 0

    # Parcours du dictionnaire et ajout à la base de données
    for question_data in data["questions"]:
        # Ajoutez la question à la base de données
        question = models.Questions(question_text=question_data["question_text"], position=position)
        session.add(question)
        session.flush()  # Pour récupérer l'ID de la question
        position+=1

        # Ajoutez les choix à la base de données
        for choice_data in question_data["choices"]:
            choice = models.Choices(
                choice_text=choice_data["choice_text"],
                is_correct=choice_data["is_correct"],
                question_id=question.id
            )
            session.add(choice)

    # Committez les changements à la base de données
    session.commit()
    u0 = models.Users(username = "mercierj", clerk_id = "user_2YX6QAdQGXXLSNRngvgcoBtZIjX", best_score = 2)    
    session.add(u0)
    session.commit()

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
