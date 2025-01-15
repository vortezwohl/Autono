from dataclasses import dataclass

from typing_extensions import override

from ceo.message.base_massage import BaseMessage


@dataclass
class AfterActionTakenMessage(BaseMessage):
    ability: str
    arguments: str | dict
    returns: str
    summarization: str

    @override
    def to_dict(self):
        return {
            'ability': self.ability,
            'choice': self.arguments,
            'returns': self.returns,
            'summarization': self.summarization,
        }
