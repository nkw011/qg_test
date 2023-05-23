from nodes.question_generation_node import BartForQGNode
from haystack import Pipeline

class QGPipeline:
    def __init__(self):
        model_path = "checkpoint/qg_5000"
        node = BartForQGNode(model_path=model_path)
        self.pipeline = Pipeline()

        self.pipeline.add_node(component=node, name="QuestionGeneration", inputs=["Query"])

    def generate(self, doc_content, keyword):
        result = self.pipeline.run(params={"QuestionGeneration": {"keywords": keyword,
                                                                "doc_content": doc_content}})
        return result