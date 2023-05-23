from haystack import BaseComponent
from typing import List

class ExtClassifier(BaseComponent):
    outgoing_edges = 3

    def run(self, file_paths: List[str]):
        file_ext = file_paths[0][-4:]
        if file_ext == ".pdf":
            return {}, "output_1"
        elif file_ext == ".txt":
            return {}, "output_2"
        else:
            return {}, "output_3"

    def run_batch(self, file_paths: List[str]):
        '''
        추후 구현
        '''
        file_ext = file_paths[0][-4:]
        if file_ext == ".pdf":
            return {}, "output_1"
        else:
            return {}, "output_2"
