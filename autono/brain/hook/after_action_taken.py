from typing import Callable

from typing_extensions import override

from autono.brain.hook.base_hook import BaseHook
from autono.message.after_action_taken_message import AfterActionTakenMessage


class AfterActionTaken(BaseHook):
    def __init__(self, function: Callable):
        super().__init__(function)

    @override
    def __call__(self, agent: any, message: AfterActionTakenMessage):
        return super().__call__(agent, message)
