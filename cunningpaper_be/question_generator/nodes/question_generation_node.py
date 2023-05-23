from tqdm import tqdm
from typing import List, Tuple, Dict
from haystack import BaseComponent
from haystack.schema import Document
from dataclasses import dataclass
from nodes.keyword_generation_node import KeywordOutput
from transformers import BartForConditionalGeneration, PreTrainedTokenizerFast
import torch
from kiwipiepy import Kiwi

@dataclass
class QuestionGenerationOutput:
    questions: List[str]
    answers: List[str]

class BartForQGNode(BaseComponent):
    outgoing_edges = 1

    def __init__(self, model_path):
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained("hyunwoongko/kobart")
        self.model = BartForConditionalGeneration.from_pretrained(model_path)
        self.sent_tok = Kiwi()

    def run(self, keywords: List[str], doc_content: str) -> Tuple[Dict, str]:

        texts = [self.focus_answer(doc_content, answer) for answer in keywords]
        questions = [ self.generate(text) for text in tqdm(texts, desc="Question Generaiton")]
        qg_output =[QuestionGenerationOutput(questions=questions, answers=keywords)]

        output = {
            "qg_outputs": qg_output
        }

        return output, "output_1"

    def run_batch(self, queries: List[str], answers: List[List[str]]) -> Tuple[Dict, str]:

        qg_outputs = []
        for query, answer_list in zip(queries, answers):
            questions = [self.tokenize(answer, query) for answer in answer_list]
            qg_outputs.append(QuestionGenerationOutput(question=questions, answer=answer_list))

        output = {
            "qg_outputs": qg_outputs
        }

        return output, "output_1"

    def insert_token(self, src, index, token):
        return src[:index] + token + src[index:]

    def focus_answer(self, context, answer, truncate=True, start_token="<unused0>", end_token="<unused1>",
                     max_len=384):
        answer_start_idx = context.find(answer)
        assert answer_start_idx != -1, "answer가 context내에 존재하지 않습니다."

        answer_end_idx = answer_start_idx + len(answer) + len(start_token)
        context = self.insert_token(context, answer_start_idx, start_token)
        context = self.insert_token(context, answer_end_idx, end_token)

        sentences = [sent.text for sent in self.sent_tok.split_into_sents(context)]

        answer_sentence_idx = None
        for i, sent in enumerate(sentences):
            if start_token in sent:
                answer_sentence_idx = i
        i, j = answer_sentence_idx, answer_sentence_idx
        truncated_context = [sentences[answer_sentence_idx]]

        while (len(" ".join(truncated_context)) < max_len):
            prev_context_length = len(" ".join(truncated_context))
            i -= 1
            j += 1

            if i > 0:
                truncated_context = [sentences[i]] + truncated_context
            if j < len(sentences):
                truncated_context = truncated_context + [sentences[j]]
            if len(" ".join(truncated_context)) == prev_context_length:
                break

        return " ".join(truncated_context)

    def generate(self, texts):
        tokenized = self.tokenize(texts)
        input_ids = tokenized["input_ids"]
        attention_mask = tokenized["attention_mask"]

        sampling_topk = -1
        sampling_topp = -1
        bad_words_ids = None

        generated = self.model.generate(
            input_ids,
            attention_mask=attention_mask,
            use_cache=True,
            early_stopping=False,
            decoder_start_token_id=self.tokenizer.bos_token_id,
            num_beams=5,
            do_sample=False,
            temperature=1.0,
            top_k=sampling_topk if sampling_topk > 0 else None,
            top_p=sampling_topp if sampling_topk > 0 else None,
            no_repeat_ngram_size=4,
            bad_words_ids=[[self.tokenizer.convert_tokens_to_ids("<unk>")]] if not bad_words_ids else bad_words_ids + [
                [self.tokenizer.convert_tokens_to_ids("<unk>")]],
            length_penalty=1.0,
            max_length=1 * len(input_ids[0]) + 50,
        )

        return self.tokenizer.decode(generated.squeeze()).replace('<s>','').replace('</s>','').strip()

    def add_bos_eos_tokens(self, tokens, eos_list):
        input_ids = tokens["input_ids"]
        attention_mask = tokens["attention_mask"]
        token_added_ids, token_added_masks = [], []

        for input_id, atn_mask, eos in zip(
                input_ids,
                attention_mask,
                eos_list,
        ):
            maximum_idx = [
                i for i, val in enumerate(input_id)
                if val != self.tokenizer.convert_tokens_to_ids("<pad>")
            ]

            if len(maximum_idx) == 0:
                idx_to_add = 0
            else:
                idx_to_add = max(maximum_idx) + 1

            eos = torch.tensor([eos], requires_grad=False)
            additional_atn_mask = torch.tensor([1], requires_grad=False)

            input_id = torch.cat([
                input_id[:idx_to_add],
                eos,
                input_id[idx_to_add:],
            ]).long()

            atn_mask = torch.cat([
                atn_mask[:idx_to_add],
                additional_atn_mask,
                atn_mask[idx_to_add:],
            ]).long()

            token_added_ids.append(input_id.unsqueeze(0))
            token_added_masks.append(atn_mask.unsqueeze(0))

        tokens["input_ids"] = torch.cat(token_added_ids, dim=0)
        tokens["attention_mask"] = torch.cat(token_added_masks, dim=0)
        return tokens

    def tokenize(self, texts, max_len=384):
        if isinstance(texts, str):
            texts = [texts]

        texts = [f"<s> {text}" for text in texts]
        eos = self.tokenizer.convert_tokens_to_ids(self.tokenizer.eos_token)
        eos_list = [eos for _ in range(len(texts))]

        tokens = self.tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            add_special_tokens=False,
            max_length=max_len - 1,
        )

        return self.add_bos_eos_tokens(tokens, eos_list)


class QuestionGenerationNode(BaseComponent):
    outgoing_edges = 1

    def __init__(self, model=None, tokenizer=None):
        model_path = "rycont/KoQuestionBART"
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained(model_path)
        self.model = BartForConditionalGeneration.from_pretrained(model_path)

    def run(self, keywords: List[str], doc_content: str) -> Tuple[Dict, str]:

        questions = [self.chat(answer, doc_content) for answer in tqdm(keywords, desc="Question Generation")]
        qg_output =[QuestionGenerationOutput(questions=questions, answers=keywords)]

        output = {
            "qg_outputs": qg_output
        }

        return output, "output_1"

    # def run(self, keywords: List[KeywordOutput], korean_documents: List[Document]) -> Tuple[Dict, str]:
    #
    #     qg_output = []
    #     for keyword, doc in tqdm(zip(keywords, korean_documents), desc='question generation', total=len(keywords)):
    #         questions = [self.chat(answer, doc.content) for answer in keyword.noun_keywords[:5]]
    #         qg_output.append(QuestionGenerationOutput(question=questions, answer=keyword.noun_keywords[:5]))
    #
    #     output = {
    #         "qg_outputs": qg_output
    #     }
    #
    #     return output, "output_1"

    def run_batch(self, queries: List[str], answers: List[List[str]]) -> Tuple[Dict, str]:

        qg_outputs = []
        for query, answer_list in zip(queries, answers):
            questions = [self.chat(answer, query) for answer in answer_list]
            qg_outputs.append(QuestionGenerationOutput(question=questions, answer=answer_list))

        output = {
            "qg_outputs": qg_outputs
        }

        return output, "output_1"

    def chat(self, keyword: str, context: str) -> str:
        text = f"질문 생성: {keyword}<unused0>{context}"
        input_ids = [self.tokenizer.bos_token_id] + self.tokenizer.encode(text) + [self.tokenizer.eos_token_id]
        res_ids = self.model.generate(
            torch.tensor([input_ids]),
            max_length=512,
            num_beams=6,
            eos_token_id=self.tokenizer.eos_token_id,
            bad_words_ids=[[self.tokenizer.unk_token_id]]
        )
        a = self.tokenizer.batch_decode(res_ids.tolist())[0]
        return a.replace('<s>', '').replace('</s>', '').strip()