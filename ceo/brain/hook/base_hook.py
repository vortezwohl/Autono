from typing import Callable

from ceo.message.base_massage import BaseMessage


class BaseHook(Callable[[BaseMessage], BaseMessage]):
    def __call__(self, agent: any, message: BaseMessage):
        super.__call__(self, agent, message)

    @staticmethod
    def do_nothing() -> Callable:
        return lambda _in: _in
