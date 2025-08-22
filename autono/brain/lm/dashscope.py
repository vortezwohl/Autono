import os

import langchain_community.chat_models.tongyi
from langchain_core.language_models import BaseChatModel

DEFAULT_TMP = 0.125
DEFAULT_TOP_P = 0.001
DEFAULT_QWEN = 'qwen-plus'


def get_lm(key: str = None, model_name: str = DEFAULT_QWEN, temp: float = DEFAULT_TMP, top_p: float = DEFAULT_TOP_P, stream: bool = False) -> BaseChatModel:
    if key is None:
        key = os.getenv('DASHSCOPE_API_KEY', os.getenv('OPENAI_API_KEY', None))
    _kwargs = {
        'dashscope_api_key': key,
        'model': model_name,
        'top_p': top_p,
        'temperature': temp,
        'streaming': stream
    }
    return langchain_community.chat_models.tongyi.ChatTongyi(**_kwargs)
