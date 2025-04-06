import json
import logging

from langchain_core.language_models import BaseChatModel

from autono.ability.ability import Ability
from autono.prompt.prompt import Prompt

log = logging.getLogger('autono.prompt')

END = '--END--'


class SchedulerPrompt(Prompt):
    def __init__(self, request: str, abilities: list[Ability], ext_context: str = ''):
        self.abilities = abilities
        prompt = dict()
        for ability in self.abilities:
            ability_dict = ability.to_dict()
            if isinstance(ability_dict['description'], dict):
                try:
                    desc_dict = ability_dict['description']
                    if isinstance(desc_dict, str):
                        desc_dict = json.loads(desc_dict)
                    if isinstance(desc_dict, dict):
                        if 'parameters' in desc_dict.keys():
                            del desc_dict['parameters']
                        if 'returns' in desc_dict.keys():
                            del desc_dict['returns']
                        ability_dict['description'] = desc_dict
                except json.JSONDecodeError:
                    pass
            del ability_dict['parameters_required']
            prompt[ability.name] = ability_dict
        prompt = json.dumps({
            "precondition": "In <abilities> are the abilities you have. "
                            f'And there is a <user_request>.',
            "limitation": "You can only use abilities in <abilities>.",
            "user_request": request,
            "task": "What you need to do is to plan your workflow based on the <abilities> and <user_request>.",
            "description": "<user_request> might contains many steps, "
                           "think carefully about every step and plan your workflow "
                           "based on your abilities in <abilities>.",
            "hint_for_ability_choosing": "Some of the abilities may be irrelevant to <user_request>. "
                                         "Make sure to choose abilities properly and wisely.",
            "abilities": prompt,
            "output_format": "{thinking_process}\n"
                             "schedule:{schedule_as_a_list_of_ability_names}\n"
                             f"{END}",
            "hint_for_output": 'Firstly, output your thinking process step by step clear and organized. '
                               'Secondly, outputs a list of names of abilities, surrounded by "[ ]", split by ", ".',
            "limitation_for_thinking_process": 'Your thinking process should be brief, concise, and short enough.',
            "limitation_for_output": 'You must strictly follow the format in <output_format>!! '
                                     'You should refer to example in <output_example>!!',
            "output_example": "1.First, I need to determine which ingredients to purchase, "
                              "which requires checking a recipe or personal preferences to decide.\n"
                              "2.After determining the ingredients, "
                              "I need to go to the market or supermarket to buy the required ingredients.\n"
                              "3.After purchasing the ingredients, I need to bring them home.\n"
                              "4.Once home, I need to wash and prepare the ingredients.\n"
                              "5.After preparation, I start cooking.\n"
                              "6.After cooking is complete, I need to arrange the dishes on the dining table.\n"
                              "schedule:"
                              "[go_to_market, payment_purchase, go_home, do_wash, do_cook, arrange_dished_on_table]\n"
                              f"{END}",
            "limitation_for_end_pattern": f'The "{END}" pattern marks the end of your whole response, '
                                          f'no more words are allowed after "{END}" pattern. '
                                          f'The "{END}" pattern is absolutely important, do not forget to place it '
                                          'in the end of your response.'
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'SchedulerPrompt: {self.prompt}')

    def invoke(self, model: BaseChatModel) -> list[Ability]:
        results = model.invoke(self.prompt).content
        log.debug(f'SchedulerResponse: {results}')
        results = results[results.rfind('['):results.rfind(']') + 1][1:-1].split(',')
        results = [result
                   .replace('\n', '')
                   .replace('\"', '')
                   .replace('\'', '').strip()
                   for result in results]
        _fin_results = list()
        for _a_result in results:
            for ability in self.abilities:
                if ability.name == _a_result:
                    _fin_results.append(ability)
        return _fin_results
