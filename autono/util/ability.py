import inspect
import json
import logging
import os
from typing import Callable

from langchain_core.language_models import BaseChatModel

from autono.brain.lm import get_openai_model
from autono.prompt import DocstringPrompt
from autono.exception.not_a_regular_function_exception import NotARegularFunctionException

log = logging.getLogger('autono.ability')


def ability(brain: BaseChatModel, cache: bool = True, cache_dir: str = ''):
    # noinspection PyShadowingNames
    def docstring_generator(func: Callable, brain: BaseChatModel, cache: bool, cache_dir: str) -> Callable:
        func.__doc__ = DocstringPrompt(func).invoke(brain)
        log.debug(f'Docstring generated for {func.__name__}. Docstring: "{func.__doc__}"')
        if cache:
            cache_function(func, cache_dir)
        return func

    # noinspection PyShadowingNames
    def make_cache_filename(func: Callable, cache_dir: str, create_path: bool = False) -> str:
        func_source_file_long = inspect.getfile(func)
        func_source_file_short = os.path.basename(func_source_file_long)
        func_source_file_short = func_source_file_short[:func_source_file_short.rfind('.py')]
        func_source_path = os.path.dirname(func_source_file_long)
        cache_path = os.path.join(func_source_path, cache_dir)
        if create_path and not os.path.exists(cache_path):
            os.mkdir(cache_path)
        return os.path.join(cache_path, f'{func_source_file_short}.{func.__name__}.cache')

    def get_source(func: Callable) -> str:
        source_lines = inspect.getsourcelines(func)[0]
        for i, line in enumerate(source_lines):
            if f'@{ability.__name__}' in line:
                del source_lines[i]
                break
        return str().join(source_lines)

    # noinspection PyShadowingNames
    def cache_function(func: Callable, cache_dir: str) -> Callable:
        cache_file = make_cache_filename(func, cache_dir, create_path=True)
        func_doc = inspect.getdoc(func)
        try:
            func_doc = json.loads(func_doc)
        except json.decoder.JSONDecodeError:
            pass
        cache_data: dict = {
            'src': get_source(func),
            'doc': func_doc
        }
        with open(cache_file, 'wb') as f:
            cache_data_str = json.dumps(cache_data, ensure_ascii=False)
            cache_data_bytes = cache_data_str.encode('utf-8')
            f.write(cache_data_bytes)
        return func

    # noinspection PyShadowingNames
    def read_cache(func: Callable, cache_dir: str) -> dict:
        cache_file = make_cache_filename(func, cache_dir)
        cache_data: dict = dict()
        if not os.path.exists(cache_file):
            return cache_data
        with open(cache_file, 'rb') as f:
            cache_data_bytes = f.read()
            cache_data = json.loads(cache_data_bytes)
        return cache_data

    def check_if_function_is_method(func: Callable) -> Callable:
        if '.' in func.__qualname__:
            raise NotARegularFunctionException(func)
        return func

    if cache_dir in ('', None):
        cache_dir = '.cache'

    if callable(brain) and not isinstance(brain, BaseChatModel):
        # noinspection DuplicatedCode
        def decorator(func):
            func = check_if_function_is_method(func)
            cache_func = read_cache(func, cache_dir)
            if cache and cache_func.get('src', None) == get_source(func):
                func.__doc__ = json.dumps(cache_func.get('doc'), ensure_ascii=False)
                return func
            return docstring_generator(func, get_openai_model(), cache, cache_dir)
        return decorator(brain)

    # noinspection DuplicatedCode
    def decorator(func):
        func = check_if_function_is_method(func)
        cache_func = read_cache(func, cache_dir)
        if cache and cache_func.get('src', None) == get_source(func):
            func.__doc__ = json.dumps(cache_func.get('doc'), ensure_ascii=False)
            return func
        return docstring_generator(func, brain, cache, cache_dir)
    return decorator
