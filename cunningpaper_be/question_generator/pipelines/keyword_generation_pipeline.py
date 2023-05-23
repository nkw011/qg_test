from haystack.pipelines import Pipeline
from haystack.nodes import TextConverter, PreProcessor, PDFToTextConverter
from nodes.korean_node import KoreanNode
from nodes.TextPreprocessor import TextPreprocessor
from nodes.keyword_generation_node import KeywordNode
from nodes.ExtClassifier import ExtClassifier

class KeyGenPipeline:
    def __init__(self):
        txt_converter = TextConverter(
            remove_numeric_tables=True,
            valid_languages=["ko", "en"]
        )
        pdf_converter = PDFToTextConverter(
            remove_numeric_tables=True,
            valid_languages=["de","en", "ko"]
        )
        ext_classifier = ExtClassifier()

        korean = KoreanNode()
        preprocessor = TextPreprocessor()
        keyword_node = KeywordNode()

        self.pipeline = Pipeline()

        self.pipeline.add_node(component=ext_classifier, name="ExtClassifier", inputs=["File"])
        self.pipeline.add_node(component=pdf_converter, name="PDFConverter", inputs=["ExtClassifier.output_1"])
        self.pipeline.add_node(component=txt_converter, name="TextConverter", inputs=["ExtClassifier.output_2"])
        self.pipeline.add_node(component=korean, name="Korean", inputs=["PDFConverter","TextConverter"])
        self.pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["Korean"])
        self.pipeline.add_node(component=keyword_node, name="Keyword", inputs=["PreProcessor"])

    def generate(self, file_path):
        return self.pipeline.run(file_paths=[file_path])