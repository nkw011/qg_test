import os
import logging
from haystack.utils import launch_es
import time
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import BM25Retriever,EmbeddingRetriever
from haystack.nodes.other.docs2answers import Docs2Answers
from mecab import MeCab
import pandas as pd
from haystack.nodes import FARMReader

os.environ['CUDA_LAUNCH_BLOCKING'] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

launch_es()

time.sleep(10)

document_store = ElasticsearchDocumentStore(
        host="127.0.0.1",
        username="",
        password="",
        index="document",
        embedding_field="question_emb",
        embedding_dim=384,
        excluded_meta_data=["question_emb"],
        similarity="cosine",
)
BM25_retriever = BM25Retriever(document_store=document_store)
Embedding_retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    use_gpu=True,
    scale_score=False,
)

df = pd.read_csv("/home/ernati/PycharmProjects/haystack/abc/share/data/FAQ_csv/question_answer.csv")
df.fillna(value="", inplace=True)
df["question"] = df["question"].apply(lambda x: x.strip())

questions = list(df["question"].values)
df["question_emb"] = Embedding_retriever.embed_queries(queries=questions).tolist()
df = df.rename(columns={"question": "content"})

docs_to_index = df.to_dict(orient="records")
document_store.write_documents(docs_to_index)

reader2 = FARMReader( model_name_or_path = "monologg/koelectra-base-v3-finetuned-korquad", use_gpu=True )

doc_to_answers = Docs2Answers()
mecab = MeCab()

