import tiktoken
from consts import consts


def count_tokens(text, model=consts().OPENAI_MODEL):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    token_count = len(tokens)
    return token_count


def tokenize_and_count(text, model=consts().OPENAI_MODEL):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    token_count = len(tokens)
    return tokens, token_count
