import asyncio
import inspect
import json
import threading

from typing_extensions import Callable
from ceo.ability.base_ability import BaseAbility


class Ability(BaseAbility):
    def __init__(self, function: Callable):
        signature = inspect.signature(function)
        doc_str = inspect.getdoc(function)
        if doc_str is None:
            doc_str = json.dumps({
                'src': inspect.getsource(function)
            }, ensure_ascii=False)
        self._function: Callable = function
        _description: str | dict = str()
        _parameters: dict = dict()
        for name, param in signature.parameters.items():
            _parameters[name] = str(param.annotation)
        try:
            _description = json.loads(doc_str)
            _description = _description.get('description', _description)
        except json.decoder.JSONDecodeError:
            _description = doc_str
        super().__init__(
            name=function.__name__,
            description=_description,
            parameters=_parameters,
            returns=signature.return_annotation
        )

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __str__(self):
        return self.__repr__()

    def __call__(self, *args, **kwargs):
        if inspect.iscoroutinefunction(self._function):
            __res = None

            def __func(loop: asyncio.AbstractEventLoop):
                nonlocal __res, args, kwargs
                try:
                    __res = loop.run_until_complete(self._function(*args, **kwargs))
                finally:
                    loop.close()

            __thread = threading.Thread(
                target=__func,
                args=(asyncio.new_event_loop(),)
            )
            __thread.start()
            __thread.join(timeout=None)
            return __res
        return self._function(*args, **kwargs)

    def to_dict(self) -> dict:
        param_list: list = list()
        unnecessary_params: tuple = ('args', 'kwargs')
        for name, _ in self._parameters.items():
            if name not in unnecessary_params:
                param_list.append(name)
        return {
            'ability_name': self._name,
            'description': self._description,
            'parameters_required': param_list,
            'returns': str(self._returns)
        }

    @property
    def function(self) -> Callable:
        return self._function
