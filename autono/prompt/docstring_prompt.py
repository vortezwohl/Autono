import inspect
import json
import logging
from collections.abc import Iterator
from typing import Callable

from langchain_core.language_models import BaseChatModel

from autono.prompt.prompt import Prompt

log = logging.getLogger('autono.prompt')


class DocstringPrompt(Prompt):
    def __init__(self, function: Callable, ext_context: str = ''):
        signature = inspect.signature(function)
        f_name: str = function.__name__
        f_parameters: dict = dict()
        f_returns: str = str(signature.return_annotation)
        for name, param in signature.parameters.items():
            f_parameters[name] = str(param.annotation)
        function_repr = {
            'name': f_name,
            'parameters': f_parameters,
            'returns': f_returns,
            'source_code': inspect.getsource(function)
        }
        docstring_format = {
            "description": {
                "brief_description": "{Brief and accurate description of the function, "
                                     "including its input and output, main logic, algorithm used, "
                                     "precautions mentioned, and any other relevant information.}",
                "parameters": [{
                        "{name of param_1}": {
                            "name": "{name of param_1}",
                            "type": "{data type of param_1}",
                            "description": "{Brief and accurate description of param_1, "
                                           "including its role in the function "
                                           "and the constraints for it.}"
                        }
                    }, {
                        "{name of param_2}": {
                            "name": "{name of param_2}",
                            "type": "{data type of param_2}",
                            "description": "{Brief and accurate description of param_2, "
                                           "including its role in the function "
                                           "and the constraints for it.}"
                        }
                    }, {
                        "{name of param_...}": {
                            "name": "{name of param_...}",
                            "type": "{data type of param_...}",
                            "description": "{Brief and accurate description of param_..., "
                                           "including its role in the function "
                                           "and the constraints for it.}"
                        }
                    }
                ],
                "returns": {
                    "type": "{data type of the return value}",
                    "description": "{Brief and accurate description of the return value, "
                                   "including its meaning.}"
                }
            }
        }
        prompt = json.dumps({
            "objective": "Generate description for the <function>.",
            "function": function_repr,
            "hint_for_function_understanding": "The <source_code> provides the unabridged definition of the <function>."
                                               "You can fully understand the <function> by reading <source_code>.",
            "output_format": "json",
            "hint_for_output_format": docstring_format
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'DocstringPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> str | Iterator:
        # noinspection DuplicatedCode
        raw_docstring = model.invoke(self.prompt).content
        log.debug(f'DocstringResponse: {raw_docstring}')
        if not raw_docstring.startswith('{'):
            raw_docstring = raw_docstring[raw_docstring.find('{'):]
        if not raw_docstring.endswith('}'):
            raw_docstring = raw_docstring[:raw_docstring.rfind('}') + 1]
        return raw_docstring.replace('\n', '')
