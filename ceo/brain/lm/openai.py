import langchain_openai
from langchain_core.language_models import BaseChatModel

DEFAULT_TMP = 0.1
DEFAULT_TOP_P = 0.1


def get_lm(key: str, name: str, temp: float = DEFAULT_TMP, top_p: float = DEFAULT_TOP_P, stream: bool = False) -> BaseChatModel:
    return langchain_openai.ChatOpenAI(
        api_key=key,
        model=name,
        top_p=top_p,
        temperature=temp,
        streaming=stream
    )
