from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from typing_extensions import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func
import openai
import json
from dotenv import load_dotenv
import os

# Accès a la clé api ChatGPT
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_key)

# Création de l'application FastApi
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


# Génération des questions par ChatGPT
def generate_question_and_choices():
    prompt = [{'role': 'user', 'content' : "Je veux un résultat comme celui-ci mais pour plusieurs questions au format json : 'questions' : [{'theme': 'API', 'question_text': 'Qu'est-ce que signifie l'acronyme API?', 'choices': [ {'choice_text': 'a) Application Programming Interface', 'is_correct': true}, {'choice_text': 'b) Advanced Programming Interface', 'is_correct': false}, {'choice_text': 'c) Automated Processing Interface', 'is_correct': false}, {'choice_text': 'd) Application Process Integration', 'is_correct': false} ] }], Génère une question pour chacun de ces thèmes ('API','Docker', 'HTML') avec pour chaque question 4 choix possibles et une valeur True ou False en fonction de si le choix est le bon, je veux la réponse true placée au hasard. Je veux que tout soit en français. Répond juste avec le json sans aucun texte."}]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=prompt)
    out = response.choices[0].message.content
    index_accolade = out.find('{')
    if index_accolade != -1:
        reponse = out[index_accolade:]
    print(reponse)
    return json.loads(reponse)


# Remplissage de la base de données avec les données de ChatGPT
def fill_database_chatgpt():
    db = SessionLocal()
    data = generate_question_and_choices()
    position = 0
    for question_data in data["questions"]:
        question = models.Questions(question_text=question_data["question_text"], position=position, is_chatgpt = True)
        db.add(question)
        db.flush() 
        position+=1
        for choice_data in question_data["choices"]:
            choice = models.Choices(
                choice_text=choice_data["choice_text"],
                is_correct=choice_data["is_correct"],
                question_id=question.id)
            db.add(choice)
    db.commit()
    u0 = models.Users(username = "mercierj", clerk_id = "user_2YX6QAdQGXXLSNRngvgcoBtZIjX", best_score = 2)    
    db.add(u0)
    db.commit()


# Remplissage de la base de données avec des questions définies si nous n'arrivons pas a déchiffrer la réponse
# de ChatGPT
def fill_database_auto():
    db = SessionLocal()
    q0= models.Questions(question_text = "Qu'est-ce qu'une API ?", position = 0, is_chatgpt = False)
    db.add(q0)
    db.commit()
    db.refresh(q0)
    r00= models.Choices(choice_text = "Un recette de cuisine" ,is_correct = False, question_id = q0.id)
    r01= models.Choices(choice_text = "Un programme permettant à deux applications de communiquer entre elles." ,is_correct = True, question_id = q0.id)
    r02= models.Choices(choice_text = "Une Application Pour les Italiens." ,is_correct = False, question_id = q0.id)
    r03= models.Choices(choice_text = "Je sais pas ça sert a rien." ,is_correct = False, question_id = q0.id)
    db.add(r00)
    db.add(r01)
    db.add(r02)
    db.add(r03)
    db.commit()
    q1= models.Questions(question_text = "A quoi sert Docker ?", position = 1, is_chatgpt = False)
    db.add(q1)
    db.commit()
    db.refresh(q1)
    r10= models.Choices(choice_text = "A rien." ,is_correct = False, question_id = q1.id)
    r11= models.Choices(choice_text = "Au départ ou à l'arrivée des bateaux c'est lui qui s'occupe de charger ou décharger les cargaisons." ,is_correct = False, question_id = q1.id)
    r12= models.Choices(choice_text = "Développer des applications faciles à assembler, à maintenir et à déplacer." ,is_correct = True, question_id = q1.id)
    r13= models.Choices(choice_text = "A programmer." ,is_correct = False, question_id = q1.id)
    db.add(r10)
    db.add(r11)
    db.add(r12)
    db.add(r13)
    db.commit()
    q2= models.Questions(question_text = "C'est quoi le principe CRUD ?", position = 2, is_chatgpt = False)
    db.add(q2)
    db.commit()
    db.refresh(q2)
    r20= models.Choices(choice_text = "Create, Read, Update, Delete." ,is_correct = True, question_id = q2.id)
    r21= models.Choices(choice_text = "Ne pas cuire un aliment." ,is_correct = False, question_id = q2.id)
    r22= models.Choices(choice_text = "A rien on s'en fiche." ,is_correct = False, question_id = q2.id)
    r23= models.Choices(choice_text = "Manger plein de crudités." ,is_correct = False, question_id = q2.id)
    db.add(r20)
    db.add(r21)
    db.add(r22)
    db.add(r23)
    db.commit()
    u0 = models.Users(username = "mercierj", clerk_id = "user_2YX6QAdQGXXLSNRngvgcoBtZIjX", best_score = 2)    
    db.add(u0)
    db.commit()

# Verification de l'état de la base de donnée
def is_table_empty():
    session = SessionLocal()
    try:
        result = session.query(models.Questions).first()
        return result is None
    finally:
        session.close()

# Remplissage de la base de données au démarrage de l'application si elle est vide
@app.on_event("startup")
async def startup_event():
    if is_table_empty():
        try:
            fill_database_chatgpt()
            print("La base de données est remplie par ChatGPT")
        except Exception as chatgpt_error:
            print(f"Erreur lors du remplissage avec fill_database_chatgpt : {chatgpt_error}")
            print("Tentative de remplissage avec fill_database_auto()")
            try:
                fill_database_auto()
                print("La base de données est remplie automatiquement")
            except Exception as auto_error:
                print(f"Erreur lors du remplissage avec fill_database_auto : {auto_error}")
                print("Aucune méthode de remplissage de la base de données n'a réussi.")
    else:
        print("La table n'est pas vide au démarrage.")

# Récupération des informations du quiz
@app.get("/quiz_infos")
async def quiz_infos(db: db_dependency):
    size = db.query(models.Questions).count()
    scores = db.query(models.Users).order_by(models.Users.best_score.desc()).limit(5).all()
    scores_data = [{"username": user.username, "score": user.best_score} for user in scores]
    return {"size": size, "scores": scores_data}

# Récupération d'une question en fonction de sa position dans le quiz
@app.get('/questions/{position}')
async def get_question(position: int, db : db_dependency):
    question = db.query(models.Questions).filter(models.Questions.position == position).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    answers =db.query(models.Choices).filter(models.Choices.question_id == question.id).all()
    return question, answers

# Ajout d'une participation au quiz d'un utilisateur dans la base de données
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
        new_user = models.Users(clerk_id=user_id, best_score=score, username = user_name)
        db.add(new_user)
        db.commit()
    elif score > user_record.best_score:
        user_record.best_score = score
        db.commit()
    participation = models.Participation(score=score, clerk_id = user_id)
    db.add(participation)
    db.commit()
    db.refresh(participation)
    return participation
