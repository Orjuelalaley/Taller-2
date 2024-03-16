from fastapi import FastAPI, HTTPException, Depends, Request, Response
from pydantic import BaseModel
from fastapi import XMLResponse
from typing import Callable, List, Annotated
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models
import xmltodict


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class ChoiseBase(BaseModel):
    choice_text: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiseBase]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@app.post('/questions/', response_class=XMLResponse)
async def create_question(request: Request, db: db_dependency):
    body = await parse_xml_body(request)()
    # Aquí deberías convertir el XML a tu modelo Pydantic o a un dict directamente
    question_data = body['question']  # Asegúrate de que este path sea correcto según tu XML
    question_text = question_data['question_text']
    choices = question_data['choices']
    db_question = models.Question(question=question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    for choice in choices['choice']:
        db_choice = models.Choice(choice_text=choice['choice_text'],
                                  is_correct=choice['is_correct'],
                                  question_id=db_question.id)
        db.add(db_choice)
    db.commit()
    
    # Preparar la respuesta como XML
    response_dict = {"response": "Pregunta creada con éxito"}  # Ajusta esto según necesites
    return XMLResponse(content=response_dict)

def parse_xml_body(request: Request) -> Callable:
    async def _parse():
        body = await request.body()
        return xmltodict.parse(body.decode("utf-8"))
    return _parse

class XMLResponse(Response):
    media_type = "application/xml"
    def render(self, content: dict) -> bytes:
        xml_content = xmltodict.unparse(content, pretty=True)
        return xml_content.encode("utf-8")