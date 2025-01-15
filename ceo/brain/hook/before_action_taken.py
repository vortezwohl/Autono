from typing import Callable

from typing_extensions import override

from ceo.brain.hook.base_hook import BaseHook
from ceo.message.before_action_taken_message import BeforeActionTakenMessage


class BeforeActionTaken(BaseHook):
    def __init__(self, function: Callable):
        super().__init__(function)

    @override
    def __call__(self, agent: any, message: BeforeActionTakenMessage):
        return super().__call__(agent, message)
