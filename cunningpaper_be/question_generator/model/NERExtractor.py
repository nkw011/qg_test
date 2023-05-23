import torch
import torch.nn as nn
from transformers import ElectraTokenizer, ElectraForTokenClassification

class NERExtractor(nn.Module):
    def __init__(self, model_path="monologg/koelectra-base-v3-naver-ner"):
        super().__init__()
        self.model = ElectraForTokenClassification.from_pretrained(model_path)
        self.tokenizer = ElectraTokenizer.from_pretrained(model_path)
        self.id2label = self.model.config.id2label
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = 384

    def predict(self, text):
        encoding = self.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            output = self.model(**encoding)

        input_ids = encoding["input_ids"].squeeze().numpy()
        logits = output.logits.squeeze().argmax(dim=-1).numpy()

        ners = []
        ner = []
        for token, logit in zip(input_ids[1:-1], logits[1:-1]):
            label = self.id2label[logit]
            if label == "O":
                ners.append(self.tokenizer.decode(ner))
                ner = []
            else:
                ner.append(token)

        if len(ner) != 0:
            text = self.tokenizer.decode(ner)
            ners.append(text)

        return [ner_ext for ner_ext in ners if len(ner_ext) != 0]