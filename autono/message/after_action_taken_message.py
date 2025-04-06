from dataclasses import dataclass

from typing_extensions import override

from autono.message.base_massage import BaseMessage


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
            'arguments': self.arguments,
            'returns': self.returns,
            'summarization': self.summarization,
        }
