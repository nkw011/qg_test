from typing import Union
from fastapi import FastAPI, UploadFile, File, Request
from starlette.middleware import Middleware


from pipelines.question_generation_pipeline import QGPipeline
from pipelines.keyword_generation_pipeline import KeyGenPipeline
from pipelines.summary_pipeline import SummaryPipeline
from node import Quiz, QuizSet
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = FastAPI(middleware=middleware)


keyword_pipeline = KeyGenPipeline()
qg_pipeline = QGPipeline()
summary_pipeline = SummaryPipeline()

FILE_NAME = "dummy.txt"
UPLOADFILE_DIR = "upload_file_directory"

@app.post("/upload")
async def upload_file(data: UploadFile = File(...)):
    global FILE_NAME

    if not data:
        return False

    FILE_NAME = data.filename
    file_data = await data.read()

    with open(os.path.join(UPLOADFILE_DIR, FILE_NAME), "wb") as fp:
        fp.write(file_data)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT'
        },
        'body': True
    }


@app.get("/quiz/")
def make_quiz():
    global FILE_NAME
    if not FILE_NAME:
        return "파일이 업로드되지 않았습니다."

    quiz_set = []
    total_keywords = []
    prev_length = 0

    result = keyword_pipeline.generate(os.path.join(UPLOADFILE_DIR, FILE_NAME))
    summary = summary_pipeline.summary(result["korean_documents"])
    for doc, keyword in zip(result["fine_documents"], result["keywords"]):
        total_keywords += keyword.keywords

        out = qg_pipeline.generate(keyword=keyword.keywords, doc_content=doc.content)
        out = out['qg_outputs'][0]
        for j, (q, a) in enumerate(zip(out.questions, out.answers)):
            quiz_set.append(Quiz(id=prev_length+j, question=q, answer=a))
        prev_length += len(out.answers)

    quiz = QuizSet(summary=summary, keyword=total_keywords, quiz=quiz_set)
    return quiz

@app.get("/")
async def hello():
    return {"hello, world"}


if __name__ == "__main__":
    if not os.path.exists(UPLOADFILE_DIR):
        os.mkdir(UPLOADFILE_DIR)

    uvicorn.run(app, host="0.0.0.0", port=8000)