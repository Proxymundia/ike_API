# chunkers/token_chunker.py
import tiktoken  # Optional library for tokenization

class TokenChunker:
    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("gpt2")

    def chunk(self, content, max_tokens=100):
        tokens = self.tokenizer.encode(content)
        chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
        return [self.tokenizer.decode(chunk) for chunk in chunks]
