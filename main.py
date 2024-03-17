from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import xmltodict
import models


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/questions/all")
async def get_all_questions(db: db_dependency):
    questions = db.query(models.Question).all()
    response_data = {
        "response": {
            "questions": {
                "question": [
                    {
                        "question_text": question.question_text
                    }
                    for question in questions
                ]
            }
        }
    }
    xml_response = xmltodict.unparse(response_data)
    return Response(content=xml_response, media_type='application/xml')


@app.post("/questions/")
async def create_question(question: Request, db: db_dependency):
    body = await question.body()
    try:
        data = xmltodict.parse(body)
        if 'question' not in data or 'question_text' not in data['question'] not in data['question']:
            raise HTTPException(status_code=400, detail="Malformed XML.")
        question_text = data['question']['question_text']
        db_question = models.Question(question_text=question_text)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        db.commit()
        response_data = {
            "response": {
                "message": "XML recibido correctamente.",
                "data": data
            }
        }
        xml_response = xmltodict.unparse(response_data)
        return Response(content=xml_response, media_type='application/xml')

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
