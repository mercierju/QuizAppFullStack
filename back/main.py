from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from typing_extensions import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func

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

def is_table_empty():
    session = SessionLocal()
    try:
        result = session.query(models.Questions).first()
        return result is None
    finally:
        session.close()

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    if is_table_empty():
        print("La table est vide au démarrage.")
        q0= models.Questions(question_text = "Qu'est-ce qu'une API ?", position = 0)
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

        q1= models.Questions(question_text = "A quoi sert Docker ?", position = 1)
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

        q2= models.Questions(question_text = "C'est quoi le principe CRUD ?", position = 2)
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

        q3= models.Questions(question_text = "A quoi sert un Dockerfile ?", position = 3)
        db.add(q3)
        db.commit()
        db.refresh(q3)
        r30= models.Choices(choice_text = "C'est juste un fichier dans le langage docker." ,is_correct = False, question_id = q3.id)
        r31= models.Choices(choice_text = "A raconter une histoire." ,is_correct = False, question_id = q3.id)
        r32= models.Choices(choice_text = "Faire l'inventaire de la marchandise." ,is_correct = False, question_id = q3.id)
        r33= models.Choices(choice_text = "Fichier texte qui contient les instructions nécessaires à la création d'une image." ,is_correct = True, question_id = q3.id)
        db.add(r30)
        db.add(r31)
        db.add(r32)
        db.add(r33)
        db.commit()

        q4= models.Questions(question_text = "C'est quoi un SSO ?", position = 4)
        db.add(q4)
        db.commit()
        db.refresh(q4)
        r40= models.Choices(choice_text = "C'est pas SSO mais OSS117." ,is_correct = False, question_id = q4.id)
        r41= models.Choices(choice_text = "Je sais pas." ,is_correct = False, question_id = q4.id)
        r42= models.Choices(choice_text = "Méthode permettant à un utilisateur d'accéder à plusieurs applications en ne procédant qu'à une seule authentification." ,is_correct = True, question_id = q4.id)
        r43= models.Choices(choice_text = "J'ai pas compris." ,is_correct = False, question_id = q4.id)
        db.add(r40)
        db.add(r41)
        db.add(r42)
        db.add(r43)
        db.commit()   

        u0 = models.Users(username = "mercierj", clerk_id = "user_2YX6QAdQGXXLSNRngvgcoBtZIjX", best_score = 4)    
        db.add(u0)
        db.commit()
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
    participation = models.Participation(score=score, clerk_id = user_id )
    db.add(participation)
    db.commit()
    db.refresh(participation)
    return participation
