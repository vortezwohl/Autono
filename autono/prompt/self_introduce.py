import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from autono.prompt.prompt import Prompt

log = logging.getLogger('autono.prompt')


class SelfIntroducePrompt(Prompt):
    def __init__(self, agent: any, ext_context: str = ''):
        agent_info_dict = agent.to_dict()
        abilities_of_agent = agent_info_dict.get('abilities', [])
        for ability in abilities_of_agent:
            try:
                if isinstance(ability['description'], dict):
                    del ability['description']['parameters']
                    del ability['description']['returns']
                del ability['parameters_required']
                del ability['returns']
            except KeyError:
                pass
        agent_info_dict['abilities'] = abilities_of_agent
        prompt = json.dumps({
            "task": "Introduce yourself briefly based on the information provided. "
                    "Only tell what you exactly can do based on your abilities.",
            "hint": "Your name is shown in <your_name>",
            "your_name": agent_info_dict.get('name', None),
            "information": agent_info_dict,
            "output_format": "My name is <name>. What can I do: ..."
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'SelfIntroducePrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        resp = model.invoke(self.prompt).content
        log.debug(f'SelfIntroduceResponse: {resp}')
        return resp
