from model.AnswerExtractor import AnswerExtractor
from model.NERExtractor import NERExtractor
from haystack import BaseComponent
from haystack.schema import Document
from typing import List, Tuple, Dict
from kiwipiepy import Kiwi
from tqdm import tqdm


class TextPreprocessor(BaseComponent):
    outgoing_edges = 1

    def __init__(self, num_of_sents=4):
        self.kiwi = Kiwi()
        self.num_of_sents=num_of_sents


    def run(self, korean_documents: List[Document]) -> Tuple[Dict, str]:
        doc_data = []
        for doc in tqdm(korean_documents, desc="Split Documents"):
            sents = [sent.text for sent in self.kiwi.split_into_sents(doc.content)]
            for i in range(0,len(sents),self.num_of_sents):
                doc_data.append(Document(content=" ".join(sents[i:i+self.num_of_sents]), content_type="text"))

        output ={
            'fine_documents':doc_data
        }
        return output, "output_1"

    # 구현 필요
    def run_batch(self, queries: List[str]) -> Tuple[Dict, str]:
        '''
        추후 구현 필요
        '''

        output = {
            "keywords": []
        }

        return output, "output_1"