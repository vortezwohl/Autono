from dataclasses import dataclass

from typing_extensions import override

from ceo.ability.ability import Ability
from ceo.message.base_massage import BaseMessage


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
