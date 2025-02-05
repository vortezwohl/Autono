import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.ability.agentic_ability import PREFIX as AGENTIC_ABILITY_PREFIX
from ceo.ability.ability import Ability
from ceo.message.after_action_taken_message import AfterActionTakenMessage
from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class ExecutorPrompt(Prompt):
    def __init__(self, args: dict, action: Ability, ext_context: str = ''):
        self.action = action
        self.args = dict()
        tmp_args = dict()
        for _k in args:
            self.args[_k] = args[_k]
            tmp_args[_k] = args[_k]
        if self.action.name.startswith(AGENTIC_ABILITY_PREFIX):
            tmp_args = {'arguments': 'Ask for a favor.'}
        prompt = json.dumps({
            "precondition": "Below is an ability shown at <ability> "
                            "and your arguments for using the <ability> is shown at <arguments>.",
            "task": "Explain what you are going to do.",
            "output_datatype": "text",
            "output_example": "I am trying to open calculator.",
            "ability": self.action.to_dict(),
            "arguments": tmp_args
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'ExecutorPrompt (before): {self.prompt}')

    def explain(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        resp = model.invoke(self.prompt).content
        log.debug(f'ExecutorResponse (before): {resp}')
        return resp

    def invoke(self, model: BaseChatModel, max_retry: int = 3) -> AfterActionTakenMessage:
        result = self.action.__call__(**self.args)
        tmp_args = self.args
        if self.action.name.startswith(AGENTIC_ABILITY_PREFIX):
            tmp_args = {'arguments': 'Ask for a favor.'}
        prompt = json.dumps({
            "precondition": "Below is an ability shown at <ability>, "
                            "your arguments for the <ability> is shown at <arguments>, "
                            "result of your using of this <ability> is shown at <result>.",
            "task": "Summarize what you have done according to <ability>, <arguments>, and <result> "
                    "accurately, comprehensively, and briefly.",
            "ability": self.action.to_dict(),
            "arguments": tmp_args,
            "result": str(result),
            "output_datatype": "text",
            "output_example": "I used the wechat_sender ability to wrote a wechat message which says 'Bonjour', "
                              "the result shows 'success' which indicates success of wechat message sending."
        }, ensure_ascii=False)
        if len(self.ext_context) > 0:
            prompt = Prompt.construct_prompt(prompt, self.ext_context)
        log.debug(f'ExecutorPrompt (after): {prompt}')
        return AfterActionTakenMessage(
            ability=self.action.name,
            arguments=tmp_args,
            returns=str(result),
            summarization=model.invoke(prompt).content
        )
