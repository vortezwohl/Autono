import inspect
import json

from typing_extensions import Callable, override

from autono.util.synchronized_call import synchronized_call
from autono.ability.base_ability import BaseAbility


class Ability(BaseAbility):
    def __init__(self, function: Callable):
        signature = inspect.signature(function)
        doc_str = inspect.getdoc(function)
        if doc_str is None:
            doc_str = json.dumps({
                'src': inspect.getsource(function)
            }, ensure_ascii=False)
        _description: str | dict = str()
        self._function: Callable = function
        _parameters: dict = dict()
        for name, param in signature.parameters.items():
            _parameters[name] = str(param.annotation)
        try:
            _description = json.loads(doc_str)
            _description = _description.get('description', _description)
        except json.decoder.JSONDecodeError:
            _description = doc_str
        except AttributeError:
            _description = doc_str
        super().__init__(
            name=function.__name__,
            description=_description,
            parameters=_parameters,
            returns=signature.return_annotation
        )

    @override
    def __call__(self, *args, **kwargs):
        return synchronized_call(self.function, *args, **kwargs)

    @property
    def function(self) -> Callable:
        return self._function
