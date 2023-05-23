import torch
import torch.nn as nn
from transformers import ElectraModel, AutoTokenizer

class AnswerExtractor(nn.Module):
    def __init__(self, model_path="monologg/koelectra-small-v3-discriminator"):
        super().__init__()
        self.model = ElectraModel.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.hidden_size = self.model.config.hidden_size
        self.qa_outputs = nn.Linear(self.hidden_size, 2)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = 384

    def forward(self, data):
        output = self.model(**data)  # (batch_size, max_len, emb_len)
        sentence_output = output[0]

        logits = self.qa_outputs(sentence_output)
        start_logits, end_logits = logits.split(1, dim=-1)

        start_logits = start_logits.squeeze(-1).contiguous()
        end_logits = end_logits.squeeze(-1).contiguous()

        return start_logits, end_logits

    def load_from_pretrained(self, path):
        self.load_state_dict(torch.load(path, map_location=self.device))

    def predict(self, context):
        tokens = self.tokenizer(context, max_length=self.max_length, padding=True, return_tensors='pt')

        self.to(self.device)
        tokens = {k: v.to(self.device) for k, v in tokens.items()}

        with torch.no_grad():
            start_logits, end_logits = self(tokens)

        start_logits = start_logits.squeeze().contiguous()
        end_logits = end_logits.squeeze().contiguous()

        start = start_logits.argmax().item()
        mask = (torch.arange(start_logits.size(0), dtype=torch.long, device=self.device) >= start)
        end = (mask * end_logits).argmax().item()

        answer = self.tokenizer.decode(tokens['input_ids'][0][start:end])

        return answer