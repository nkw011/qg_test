from haystack.schema import Document
from haystack import BaseComponent
from typing import List, Tuple, Dict
from utils.korean_preprocess import *
from tqdm import tqdm

from haystack.schema import Document


class KoreanNode(BaseComponent):
    outgoing_edges = 1

    def __init__(self):
        super().__init__()
        self.func_list = [remove_html, remove_email, remove_hashtag, remove_user_mention,
                          remove_url, remove_bad_char, remove_press, clean_punc, remove_bracket_string,
                          remove_repeated_spacing, remove_useless_breacket, remove_extra]

    def run(self, documents: List[Document]) -> Tuple[Dict, str]:
        korean_documents = []
        for doc in tqdm(documents, desc="Korean Preprocessing:"):
            content = doc.content.replace("\n", "")
            for func in self.func_list:
                content = func(content)
            doc.content = content
            korean_documents.append(doc)

        output = {
            'korean_documents': korean_documents
        }

        return output, 'output_1'

    def run_batch(self, documents: List[List[Document]]) -> Tuple[Dict, str]:
        korean_documents = []
        for docs in documents:
            contents = []
            for doc in docs:
                content = doc.content
                for func in self.func_list:
                    content = func(content)
                doc.content = content
                contents.append(doc)
            korean_documents.append(contents)

        output = {
            'korean_documents': korean_documents
        }

        return output, 'output_1'
