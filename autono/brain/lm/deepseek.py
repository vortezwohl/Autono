import os

import langchain_openai
from langchain_core.language_models import BaseChatModel

DEFAULT_TMP = 0.125
DEFAULT_TOP_P = 1.00
DEFAULT_DEEPSEEK = 'deepseek-chat'
BASE_URL = "https://api.deepseek.com/v1"


def get_lm(key: str = None, model_name: str = DEFAULT_DEEPSEEK, temp: float = DEFAULT_TMP, top_p: float = DEFAULT_TOP_P,
           base_url: str = BASE_URL, stream: bool = False) -> BaseChatModel:
    if key is None:
        key = os.getenv('DEEPSEEK_API_KEY', os.getenv('OPENAI_API_KEY', None))
    _kwargs = {
        'api_key': key,
        'model': model_name,
        'top_p': top_p,
        'temperature': temp,
        'streaming': stream,
        'base_url': base_url
    }
    return langchain_openai.ChatOpenAI(**_kwargs)
