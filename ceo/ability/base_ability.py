class BaseAbility(object):
    def __init__(self, name: str, description: str | dict, parameters: dict | str, returns: any):
        self._name = name
        self._description = description
        self._parameters = parameters
        self._returns = returns

    def to_dict(self) -> dict: ...

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
