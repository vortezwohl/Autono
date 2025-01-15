from typing import Callable

from ceo.message.base_massage import BaseMessage


class BaseHook(Callable[[BaseMessage], BaseMessage]):
    def __call__(self, executor_response: BaseMessage):
        super.__call__(self, executor_response)

    @staticmethod
    def do_nothing() -> Callable:
        return lambda _in: _in
