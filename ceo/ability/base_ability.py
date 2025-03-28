import json

from typing_extensions import Callable


class BaseAbility(Callable):
    def __init__(self, name: str, description: str | dict, parameters: dict | str, returns: any):
        self._name = name
        self._description = description
        self._parameters = parameters
        self._returns = returns

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __str__(self):
        return self.__repr__()

    def __call__(self, *args, **kwargs): ...

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
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str | dict:
        return self._description

    @property
    def parameters(self) -> dict:
        return self._parameters

    @property
    def returns(self) -> any:
        return self._returns
