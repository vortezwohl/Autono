from .openai import get_lm as __get_openai_model, BaseChatModel
from .dashscope import get_lm as __get_dashscope_model
from .deepseek import get_lm as __get_deepseek_model


def get_openai_model(*args, **kwargs) -> BaseChatModel:
    return __get_openai_model(*args, **kwargs)


def get_dashscope_model(*args, **kwargs) -> BaseChatModel:
    return __get_dashscope_model(*args, **kwargs)


def get_deepseek_model(*args, **kwargs) -> BaseChatModel:
    return __get_deepseek_model(*args, **kwargs)
