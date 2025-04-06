import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from autono.exception.too_dumb_exception import TooDumbException
from autono.prompt.prompt import Prompt

log = logging.getLogger('autono.prompt')

END = '--END--'
SUCCESS = '--SUCCESS--'
FAILED = '--FAILED--'
THOUGHT_PROCESS = '--THOUGHT-PROCESS--'
CONCLUSION = '--CONCLUSION--'

OUTPUT_EXAMPLE = THOUGHT_PROCESS + """
(Start) [Grocery shopping]: Alex bought carrots and chicken breasts from the supermarket. """ + f'({SUCCESS})' + """
(After: Grocery shopping) [Cooking the meal]: I cooked the chicken with the carrots and garlic in a pan. """ + f'({SUCCESS})' + """
(After: Cooking the meal) [Plating the dish]: Sara plated the chicken and vegetables. """ + f'({SUCCESS})' + """
(After: Plating the dish) [Eating the meal]: There is no record in <history> indicating that someone sat down to eat the meal. """ + f'({FAILED})' + """
Based on above assessments, here is my conclusion:
""" + CONCLUSION + ("\nYour request has not been fully achieved. "
                    "I asked Alex to buy carrots and chicken breasts from the supermarket, "
                    "I cooked the chicken with the carrots and garlic in a pan, "
                    "Then I asked Sara to plate the chicken and vegetables, "
                    "but the meal was not eaten by anyone.\n") + END


class IntrospectionPrompt(Prompt):
    def __init__(self, request: str, history: dict | list, self_info: str | dict, ext_context: str = ''):
        prompt = json.dumps({
            "precondition": "Below in <history> are actions have been performed to achieve <request>. ",
            "request": request,
            "your_identity": self_info,
            "hint_for_your_identity": 'You can know your identity from <your_identity>.',
            "task": "Think step by step concisely whether <request> has been fully achieved "
                    "according to <history> and <request>. "
                    "Then, provide the detailed results mentioned in <history> accurately. "
                    "Finally, if the <request> has not been fully achieved, explain why failed?",
            "history": history,
            "output_datatype": "text",
            "output_format": f'{THOUGHT_PROCESS}\n'
                             '({condition_for_action_1}) [{action_1_to_take}]: {record_of_action_1_from_history} ({success_or_failed})\n'
                             '({condition_for_action_2}) [{action_2_to_take}]: {record_of_action_2_from_history} ({success_or_failed})\n'
                             '({condition_for_action_{n}}) [{action_{n}_to_take}]: {record_of_action_{n}_from_history} ({success_or_failed})\n'
                             'Based on above assessments, here is my conclusion:\n'
                             f'{CONCLUSION}\n'
                             '{conclusion}{results_of_actions}\n'
                             f'{END}',
            "output_example": OUTPUT_EXAMPLE,
            "limitation_1_for_output": 'You must strictly follow the format in <output_format>!! '
                                       'You should refer to example in <output_example>!!',
            "limitation_2_for_output": "Provide thought process (briefly and concisely) before conclusion.",
            "limitation_3_for_output": "Output should be concise, accurate, and short enough.",
            "limitation_for_conclusion": "In <conclusion> you must provide all the detailed results of all actions performed "
                                         "to achieve the <request>.",
            "hint_for_thought_process_pattern": f'The "{THOUGHT_PROCESS}" pattern marks the start of your thought process, '
                                                'do not forget to place it before your thought process.',
            "hint_for_thought_conclusion_pattern": f'The "{CONCLUSION}" pattern marks the start of your conclusion, '
                                                   'do not forget to place it before your conclusion.',
            "hint_for_end_pattern": f'The "{END}" pattern marks the end of your whole response, '
                                    f'no more words are allowed after "{END}" pattern. '
                                    f'The "{END}" pattern is absolutely important, do not forget to place it '
                                    'in the end of your response.'
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'IntrospectionPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel, stream: bool = False, max_retry: int = 6) -> tuple[str, str] | Iterator:
        if stream:
            return model.stream(self.prompt)
        count: int = 0
        exclamation = '!'
        tmp_prompt = self.prompt
        while True:
            # noinspection DuplicatedCode
            if count > 0:
                if count <= max_retry:
                    log.warning(f'IntrospectionPromptWarn: incorrectly formatted. Retry: {count}')
                else:
                    log.warning(f'IntrospectionPromptWarn: max retry exceeded.')
                    raise TooDumbException(model)
            count += 1
            resp = model.invoke(tmp_prompt).content
            log.debug(f"Introspection thought process: \n{resp}")
            if resp.count(THOUGHT_PROCESS) == 1 and resp.count(CONCLUSION) == 1 and resp.count(END) == 1:
                break
            tmp_prompt = (f'{self.prompt}Attention_{count}: '
                          f'You must strictly follow the format in <output_format>{count * 2 * exclamation} '
                          f'You should refer to example in <output_example>{count * 2 * exclamation}')
        log.debug(f'IntrospectionResponse: {resp}')
        _conclusion = resp[resp.rfind(CONCLUSION) + len(CONCLUSION):resp.rfind(END)].strip().strip('\n').strip('\r')
        return _conclusion, resp
