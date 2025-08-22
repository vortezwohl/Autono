import os

import langchain_openai
from langchain_core.language_models import BaseChatModel

DEFAULT_TMP = 0.125
DEFAULT_TOP_P = 1.00
DEFAULT_GPT = 'gpt-5-nano'


def get_lm(key: str = None, model_name: str = DEFAULT_GPT, temp: float = DEFAULT_TMP, top_p: float = DEFAULT_TOP_P,
           base_url: str = None, stream: bool = False) -> BaseChatModel:
    if key is None:
        key = os.getenv('OPENAI_API_KEY', None)
    _kwargs = {
        'api_key': key,
        'model': model_name,
        'top_p': top_p,
        'temperature': temp,
        'streaming': stream
    }
    if base_url is not None:
        _kwargs['base_url'] = base_url
    return langchain_openai.ChatOpenAI(**_kwargs)
