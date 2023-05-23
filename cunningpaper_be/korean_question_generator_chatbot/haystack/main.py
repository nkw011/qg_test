#haystack
import os
from haystack.pipelines import TextIndexingPipeline

# FastAPI
import ela.eladocu
import ela.nodes
import ela.nodes_new

# chatbot
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Union, List


outputfile_dir = "/home/ernati/PycharmProjects/haystack/abc/share/data/pdf/testdir_pdf_kr_to_txt/"
outputfile_en_dir = "/home/ernati/PycharmProjects/haystack/abc/share/data/pdf/testdir_pdf_en_to_txt/"

files_to_index = [outputfile_dir + f for f in os.listdir(outputfile_dir)]
files_to_index2 = [outputfile_en_dir + f for f in os.listdir(outputfile_en_dir)]
document_store = ela.eladocu.document_store

indexing_pipeline = TextIndexingPipeline(document_store)
indexing_pipeline.run_batch(file_paths=files_to_index)
indexing_pipeline.run_batch(file_paths=files_to_index2)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class Question(BaseModel):
    question: str = "..."


class ChatbotAnswer(BaseModel):
    answer: str = "..."
    score: float = "0.00"


def query_to_Question(ques: Question, qr: str):
    ques.question = qr


# def QA_to_ChatbotAnswer(deli_list, res: dict):
#     deli = ChatbotAnswer()
#     if res['node_id'] == 'FAQ':
#         deli.answer = res["answers"][0] + " -FAQ- "
#         deli_list.append(deli)
#     else:  # "node_id' == 'JoinResults'
#         if len(res["answers"]) == 0:
#             deli.answer = "no answer"
#             deli_list.append(deli)
#         else:
#             for i in range( 0,len(res["answers"]) ):
#                 deli.answer = res["answers"][i].answer
#                 deli.score = res["answers"][i].score
#                 deli_list.append(deli)
#                 deli = ChatbotAnswer()

def QA_to_ChatbotAnswer(deli_list, res: dict):
    deli = ChatbotAnswer()
    if res["answers"][0].type == 'other':
        deli.answer = res["answers"][0].answer + " -FAQ- "
        deli_list.append(deli)
    else:  # "type" == extractive
        if len(res["answers"]) == 0:
            deli.answer = "no answer"
            deli_list.append(deli)
        else:
            for i in range( 0,len(res["answers"]) ):
                deli.answer = res["answers"][i].answer
                deli.score = res["answers"][i].score
                deli_list.append(deli)
                deli = ChatbotAnswer()



@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}


@app.get("/chatbot/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("query.html", {"request": request})

# @app.post("/chatbot/", response_class=HTMLResponse)
# async def answer_question(request: Request):
#     # Let's say I received a question as a Question Instance.
#     form = await request.form()
#     query = form["query"]
#
#     deliver_list = []
#
#     result = ela.nodes_new.Chatbot_pipeline(query, 0.90)
#     QA_to_ChatbotAnswer(deliver_list, result)
#
#     return templates.TemplateResponse("answer.html", {"request": request, "query": query, "score": deliver_list[0].score,
#                                                       "answers": deliver_list})

@app.post("/chatbot/")
async def answer_question(thing : Question) -> List[ChatbotAnswer]:
    # Let's say I received a question as a Question Instance.

    query = thing.question

    deliver_list = []
    result = ela.nodes_new.Chatbot_pipeline(query,0.90)
    QA_to_ChatbotAnswer(deliver_list, result)

    return deliver_list


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
