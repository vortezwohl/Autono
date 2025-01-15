from typing import Callable

from ceo.message.base_massage import BaseMessage
from ceo.brain.base_agent import BaseAgent


class BaseHook(Callable[[BaseAgent, BaseMessage], BaseMessage]):

    def __init__(self, function: Callable[[BaseAgent, BaseMessage], BaseMessage]):
        self._function = function

    def __call__(self, agent: BaseAgent, message: BaseMessage):
        return self._function(agent, message)

    @staticmethod
    def do_nothing() -> Callable:
        return lambda agent, msg: msg
