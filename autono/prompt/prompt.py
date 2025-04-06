import abc
import datetime
import hashlib
import json
import random

from langchain_core.language_models import BaseChatModel


class Prompt:
    def __init__(self, prompt: str, ext_context: str = ''):
        self.prompt = Prompt.construct_prompt(prompt, ext_context)
        self.ext_context = ext_context

    @abc.abstractmethod
    def invoke(self, model: BaseChatModel): ...

    @staticmethod
    def construct_prompt(prompt: str, ext_context: str) -> str:
        __now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S.%f')
        __hash = hashlib.md5(f'{prompt}{__now}{random.uniform(0, 10 ** 3)}'.encode('utf-8')).hexdigest()
        __misc = {
            "__current_timestamp": __now,
            "__prompt_id": __hash,
        }
        prompt_json_part = prompt[prompt.find('{'):prompt.rfind('}') + 1]
        __prompt_dict = {
            '__misc': __misc,
            'prompt': json.loads(prompt_json_part)
        }
        prompt_addition = prompt[prompt.rfind('}') + 1:]
        if len(prompt_addition) > 0:
            __prompt_dict['additional_prompt'] = prompt_addition
        if len(ext_context) > 0:
            __prompt_dict['__ext_context'] = ext_context
        return json.dumps(__prompt_dict, ensure_ascii=False)
