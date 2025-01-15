import json
from dataclasses import dataclass

from typing_extensions import override

from ceo.message.base_massage import BaseMessage


@dataclass
class AllDoneMessage(BaseMessage):
    success: bool
    conclusion: str
    raw_response: str
    time_used: str | float | int
    step_count: int

    @override
    def to_dict(self):
        return {
            'success': self.success,
            'conclusion': self.conclusion,
            'raw_response': self.raw_response,
            'misc': {
                'time_used': self.time_used,
                'step_count': self.step_count
            }
        }

    @property
    def response_for_agent(self):
        _tmp = {
            'success': self.success,
            'response': self.raw_response
        }
        return json.dumps(_tmp, ensure_ascii=False)
