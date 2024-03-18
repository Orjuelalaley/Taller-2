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