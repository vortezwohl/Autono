from typing_extensions import override

from ceo.brain.hook.base_hook import BaseHook
from ceo.message import AfterExecutionMessage


class AfterExecutionHook(BaseHook):
    @override
    def __call__(self, agent: any, executor_response: AfterExecutionMessage):
        super.__call__(self, agent, executor_response)
