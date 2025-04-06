import json
import logging

from langchain_core.language_models import BaseChatModel

from autono.prompt.prompt import Prompt

log = logging.getLogger('autono.prompt')


class RequestResolverPrompt(Prompt):
    def __init__(self, request: str, ext_context: str = ''):
        prompt = json.dumps({
            "precondition": 'There is a user request shown below at <user_request>',
            "user_request": request,
            "task": "What you need to do is to tell user's intention based on <user_request>.",
            "additional_important": "For any details mentioned in <user_request>, you should preserve them in full, "
                                    "especially specific information with accuracy requirements "
                                    "such as all numbers occur, parameter, location, "
                                    "date/time, name, proper noun, entity, etc...",
            "hint_for_thinking": "Deduce and analyse the <user_request> step by step. "
                                 "Keep track of the steps' interdependence and orderliness.",
            "output_format": {
                "step_{n}": "({condition_for_step_{n}}) {action_of_step_{n}}"
            },
            "hint_1_for_output": "Break user's intention(s) down into possible steps. "
                                 "Keep track of the steps' interdependence and orderliness.",
            "hint_2_for_output": 'You must strictly follow the format in <output_format>! '
                                 'You can refer to example in <output_example>!',
            "limitation_1_for_output": 'Make your output brief, concise, accurate and short enough.',
            "limitation_2_for_output": 'Thought process is not required.',
            "output_example": {
                "step_1": "(Start) Open the door",
                "step_2": "(After: door opened) Go into the room",
                "step_3": "(After: walked in the room) Find the toys in the room",
                "step_...": "(After: found toys)..."
            }
        }, ensure_ascii=False)
        self.__request = request
        super().__init__(prompt, ext_context)
        log.debug(f'RequestResolverPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> tuple[str, str]:
        _dont_do_anything = "Don't do anything."
        if self.__request == '':
            return _dont_do_anything, _dont_do_anything
        user_request_by_step = model.invoke(self.prompt).content
        log.debug(f'RequestResolverResponse: {user_request_by_step}')
        return self.__request, user_request_by_step
