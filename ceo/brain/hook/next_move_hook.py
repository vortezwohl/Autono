from typing_extensions import override

from ceo.brain.hook.base_hook import BaseHook
from ceo.message.next_move_message import NextMoveMessage


class NextMoveHook(BaseHook):
    @override
    def __call__(self, agent: any, message: NextMoveMessage):
        return super.__call__(self, agent, message)
