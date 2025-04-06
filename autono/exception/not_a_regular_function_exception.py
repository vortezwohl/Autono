from typing import Callable


class NotARegularFunctionException(TypeError):
    def __init__(self, func: Callable):
        super().__init__(f'"{func.__qualname__}" is not a regular function. Abilities can only be regular functions.')
