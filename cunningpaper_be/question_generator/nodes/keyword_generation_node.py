from model.AnswerExtractor import AnswerExtractor
from model.NERExtractor import NERExtractor
from haystack import BaseComponent
from haystack.schema import Document
from typing import List, Tuple, Dict
from kiwipiepy import Kiwi
from dataclasses import dataclass
from tqdm import tqdm
from utils.postprocess import keyword_post_process

MODEL_CHECKPOINT={
    "full_trained": "checkpoint/answer_extractor-small-train_epoch_6_full_data.pt",
    "best_valid": "checkpoint/answer_extractor2-small-f1.pt"
}

@dataclass
class KeywordOutput:
    keywords: List[str]


class KeywordNode(BaseComponent):
    outgoing_edges = 1

    def __init__(self):
        self.full_trained_model = AnswerExtractor()
        self.best_valid_model = AnswerExtractor()
        # self.ner_model = NERExtractor()
        self.tagger = Kiwi()

        self.full_trained_model.load_from_pretrained(MODEL_CHECKPOINT["full_trained"])
        self.best_valid_model.load_from_pretrained(MODEL_CHECKPOINT["best_valid"])

        self.threshold = 25


    def run(self, fine_documents: List[Document]) -> Tuple[Dict, str]:

        keywords = []

        for doc in tqdm(fine_documents, desc="Keyword Generation"):
            print(doc.content)
            full_trained_keyword: str= self.full_trained_model.predict(doc.content)
            best_valid_keyword: str = self.best_valid_model.predict(doc.content)
            # ner_keywords:List[str] = self.ner_model.predict(doc.content)

            keyword = set()
            # for t in ner_keywords:
            #     t = keyword_post_process(self.tagger, t)
            #     if len(t) > 1:
            #         keyword.add(t)

            if len(full_trained_keyword) > self.threshold:
                full_trained_keyword= keyword_post_process(self.tagger, full_trained_keyword)
            if len(best_valid_keyword) > self.threshold:
                best_valid_keyword = keyword_post_process(self.tagger, best_valid_keyword)

            keyword.add(full_trained_keyword)
            keyword.add(best_valid_keyword)

            keywords.append(KeywordOutput(keywords=list(keyword)))

        output = {
            "keywords": keywords
        }

        return output, "output_1"

    # 구현 필요
    def run_batch(self, queries: List[str]) -> Tuple[Dict, str]:

        keywords = []
        for query in queries:
            ner_keywords = ""
            noun_keywords = set(self.find_nouns(query))

            if self.ner:
                ner_keywords = set(self.ner_text(query))

            keyword = KeywordOutput(ner_keywords=list(ner_keywords),
                                    noun_keywords=list(noun_keywords))
            keywords.append(keyword)

        output = {
            "keywords": keywords
        }

        return output, "output_1"