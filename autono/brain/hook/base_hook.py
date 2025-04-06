from typing import Callable

from autono.message.base_massage import BaseMessage
from autono.brain.base_agent import BaseAgent
from autono.util.synchronized_call import synchronized_call


class BaseHook(Callable[[BaseAgent, BaseMessage], BaseMessage]):

    def __init__(self, function: Callable[[BaseAgent, BaseMessage], BaseMessage]):
        self._function = function

    def __call__(self, agent: BaseAgent, message: BaseMessage):
        return synchronized_call(self._function, agent, message)

    @staticmethod
    def do_nothing() -> Callable:
        return lambda agent, msg: msg
