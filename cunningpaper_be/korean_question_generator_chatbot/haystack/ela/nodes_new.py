from haystack.pipelines import Pipeline
import ela.eladocu


def Chatbot_pipeline(query : str, boundscore : int) :
    return_list = []

    first_pipeline = Pipeline()
    first_pipeline.add_node(component=ela.eladocu.Embedding_retriever, name="Retriever", inputs=["Query"])
    first_pipeline.add_node(component=ela.eladocu.doc_to_answers, name="Docs2Answers", inputs=["Retriever"])

    result_faq = first_pipeline.run(query=query, params={"Retriever": {"top_k": 10}})

    if result_faq["answers"][0].score >= boundscore :
        #return answer
        return result_faq

    else : #score < boundscore
        document_list = []
        noun_list = ela.eladocu.mecab.nouns( query )

        for i in range(0, len(noun_list)) :
            result_retriever = ela.eladocu.BM25_retriever.retrieve( query=noun_list[i], top_k=5 )
            document_list.extend( result_retriever )

        result_reader = ela.eladocu.reader2.predict(query = query, documents=document_list, top_k=9 )
        return result_reader

