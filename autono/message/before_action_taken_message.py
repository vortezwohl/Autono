from dataclasses import dataclass

from typing_extensions import override

from autono.ability.ability import Ability
from autono.message.base_massage import BaseMessage


@dataclass
class BeforeActionTakenMessage(BaseMessage):
    ability: Ability
    arguments: dict

    @override
    def to_dict(self):
        return {
            'ability': self.ability.to_dict(),
            'args': self.arguments
        }
