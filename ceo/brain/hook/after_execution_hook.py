from typing import Callable

from typing_extensions import override

from ceo.brain.hook.base_hook import BaseHook
from ceo.message.after_execution_message import AfterExecutionMessage


class AfterExecutionHook(BaseHook):
    def __init__(self, function: Callable):
        super().__init__(function)

    @override
    def __call__(self, agent: any, message: AfterExecutionMessage):
        return super().__call__(agent, message)
