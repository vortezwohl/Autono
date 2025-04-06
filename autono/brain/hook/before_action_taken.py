from typing import Callable

from typing_extensions import override

from autono.brain.hook.base_hook import BaseHook
from autono.message.before_action_taken_message import BeforeActionTakenMessage


class BeforeActionTaken(BaseHook):
    def __init__(self, function: Callable):
        super().__init__(function)

    @override
    def __call__(self, agent: any, message: BeforeActionTakenMessage):
        return super().__call__(agent, message)
