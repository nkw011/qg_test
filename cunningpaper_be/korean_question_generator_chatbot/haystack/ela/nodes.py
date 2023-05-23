from typing import List
from haystack import BaseComponent
from haystack.nodes.query_classifier.base import BaseQueryClassifier
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from haystack.nodes import FARMReader
from haystack.pipelines import Pipeline
from haystack.nodes import JoinAnswers
import ela.eladocu

sentence_transformer_model = SentenceTransformer('jhgan/ko-sbert-nli')

class CustomQueryClassifier(BaseComponent):
    outgoing_edges = 2

    def run(self, query: str):
        if "?" in query:
            return {}, "output_2"
        else:
            return {}, "output_1"

    def run_batch(self, queries: List[str]):
        split = {"output_1": {"queries": []}, "output_2": {"queries": []}}
        for query in queries:
            if "?" in query:
                split["output_2"]["queries"].append(query)
            else:
                split["output_1"]["queries"].append(query)

        return split, "split"

class CHECK_similarity_faq(BaseQueryClassifier):
    outgoing_edges = 2

    def run(self, query: str):
        data = pd.read_csv("/home/ernati/PycharmProjects/haystack/venv/share/data/FAQ_csv/question_answer.csv")

        faq_dict = list()
        question_list = list()

        for i in range(0, 9):
            faq_temp = dict()
            question = data["question"][i]
            question_list.append(question)
            faq_temp[question] = data["answer"][i]
            faq_dict.append(faq_temp)

        question_list.append(query)
        # embeddings = sentence_transformer_model.encode(question_list)

        embeddings = sentence_transformer_model.encode(question_list, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(embeddings, embeddings)

        cosine_scores_list = cosine_scores[-1].tolist()

        max_cosine_question_index = int()
        max = 0

        for i in range(0, len(cosine_scores_list) - 1):
            if i == 0:
                max = cosine_scores_list[i]
                continue
            if max < cosine_scores_list[i]:
                max = cosine_scores_list[i]
                max_cosine_question_index = i

        if max > 0.95:
            return {}, "output_1"

        else:
            return {}, "output_2"

    def run_batch(self, queries: List[str]):
        split = {"output_1": {"queries": []}, "output_2": {"queries": []}}
        for query in queries:
            if "?" in query:
                split["output_2"]["queries"].append(query)
            else:
                split["output_1"]["queries"].append(query)

        return split, "split"

class FAQ(BaseComponent):
    outgoing_edges = 1

    def run(self, query: str):
        results = {"answers": []}

        data = pd.read_csv("/home/ernati/PycharmProjects/haystack/venv/share/data/FAQ_csv/question_answer.csv")

        faq_dict = list()
        question_list = list()

        for i in range(0, 9):
            faq_temp = dict()
            question = data["question"][i]
            question_list.append(question)
            faq_temp[question] = data["answer"][i]
            faq_dict.append(faq_temp)

        # model = SentenceTransformer('jhgan/ko-sbert-nli')

        question_list.append(query)
        # embeddings = sentence_transformer_model.encode(question_list)

        embeddings = sentence_transformer_model.encode(question_list, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(embeddings, embeddings)

        cosine_scores_list = cosine_scores[-1].tolist()

        max_cosine_question_index = int()
        max = 0
        for i in range(0, len(cosine_scores_list) - 1):
            if i == 0:
                max = cosine_scores_list[i]
                continue
            if max < cosine_scores_list[i]:
                max = cosine_scores_list[i]
                max_cosine_question_index = i
        answer = faq_dict[max_cosine_question_index][question_list[max_cosine_question_index]]

        results["answers"].append(answer)
        return results, "output"

    def run_batch(self, queries: List[str]):
        split = {"output_1": {"queries": []}, "output_2": {"queries": []}}

        return split, "split"

reader = FARMReader( model_name_or_path = "monologg/koelectra-base-v3-finetuned-korquad", use_gpu=True )

my_pipeline = Pipeline()
my_pipeline.add_node(component=CustomQueryClassifier(), name="QueryClassifier", inputs=["Query"])
# 1. question -> check_similarity_faq
my_pipeline.add_node(component=CHECK_similarity_faq(), name="CHECK_similarity_faq", inputs=["QueryClassifier.output_2"])
# 1-1. check_similarity_faq -> Faq
my_pipeline.add_node(component=FAQ(), name="FAQ", inputs=["CHECK_similarity_faq.output_1"])
# 1-2. check_similarity_faq -> retriever -> Reader
# 2. not question -> retriever -> Reader
my_pipeline.add_node(component=ela.eladocu.BM25_retriever, name="BM25retriever",
                     inputs=["QueryClassifier.output_1", "CHECK_similarity_faq.output_2"])
my_pipeline.add_node(component=reader, name="FARMReader", inputs=["BM25retriever"])
# 3. join answer
my_pipeline.add_node(component=JoinAnswers(join_mode="concatenate"), name="JoinResults", inputs=["FARMReader", "FAQ"])