from typing import Optional, List
from pydantic import BaseModel

class Quiz(BaseModel):
    id:int
    question: str
    answer: str

class QuizSet(BaseModel):
    summary: str
    keyword: List[str]
    quiz: List[Quiz]