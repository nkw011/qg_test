import kss

class SummaryPipeline:

    def summary(self, korean_documents):
        contents = [ doc.content for doc in korean_documents]
        contents = " ".join(contents)
        output = kss.summarize_sentences(contents, max_sentences=5)

        return " ".join(output)