import json
import logging
from collections import OrderedDict

from langchain_core.language_models import BaseChatModel

from ceo.ability import Ability
from ceo.ability.agentic_ability import PREFIX as AGENTIC_ABILITY_PREFIX
from ceo.message.before_action_taken_message import BeforeActionTakenMessage
from ceo.prompt.prompt import Prompt
from ceo.exception.too_dumb_exception import TooDumbException

log = logging.getLogger('ceo.prompt')

SEPARATOR = '--SEP--'
END = '--END--'
MISSION_COMPLETE = '-mission-complete-'
MISSION_FAILED = '-mission-failed-'
MAKE_FINAL_RESPONSE = '-make-final-response-'

OUTPUT_EXAMPLE = """
[step1] In the provided history, events related to the user's request are listed chronologically:
    1. Steve calculated the radius of the sphere using the expression "(3 * 174.9 / 15.9 * 2.77)", resulting in a radius of 91.41 cm.
    2. Steve then calculated the surface area of the sphere using the formula "4 * 3.14159 * (91.41^2)", resulting in a surface area of 105001.841348316 cm².
[step2] According to the history, the radius and surface area have been calculated, but the volume calculation and file writing have not been completed, therefore the user request has not been fully and properly accomplished.
[step3] The unfinished parts of the user request are the calculation of the volume and writing the results to 'result.txt'. The abilities I possess include "calculator" for performing calculations and "write_file" for writing content to a file. 
[step4] Since the user's request is not fully accomplished, and I have the ability to calculate the volume and write to a file, my next move is to use the "calculator" ability with the expression "(4/3) * 3.14159 * (91.41^3)" to compute the volume of the sphere.
[step5] This step is not applicable because the user request has not been fully accomplished, and I have the ability to continue progressing.
[step6] This step is not applicable because the user request has not been fully accomplished.
""" + SEPARATOR + """
args:{
  "{name_of_param}": "(4/3) * 3.14159 * (91.41^3)"
}
ability:[calculator]
""" + END


class NextMovePrompt(Prompt):
    def __init__(self, request: str | dict,
                 abilities: list[Ability],
                 history: OrderedDict | None = None,
                 ext_context: str = ''):
        self.abilities = abilities
        self.__ability_names = [MISSION_COMPLETE, MISSION_FAILED, MAKE_FINAL_RESPONSE]
        for ability in self.abilities:
            self.__ability_names.append(ability.name)
        abilities_dict: dict = {
            MISSION_COMPLETE: {
                'ability_name': MISSION_COMPLETE,
                'description': 'To be chosen only when mission is considered completed.',
                'parameters_required': [],
                'returns': None
            },
            MISSION_FAILED: {
                'ability_name': MISSION_FAILED,
                'description': 'To be chosen only when mission is considered failed.',
                'parameters_required': [],
                'returns': None
            },
            MAKE_FINAL_RESPONSE: {
                'ability_name': MAKE_FINAL_RESPONSE,
                'description': 'After ALL previous actions performed SUCCESSFULLY, '
                               'you can make the final response to user.',
                'parameters_required': [],
                'returns': None
            }
        }
        # noinspection PyUnusedLocal
        latest_progress = None
        for ability in self.abilities:
            abilities_dict[ability.name] = ability.to_dict()
        if history in ('', '[]', '()', '{}', {}, [], (), None) or len(history.keys()) == 0:
            latest_progress = history = "Nothing happened before you."
        else:
            latest_progress = history[list(history.keys())[-1]]
        prompt_dict = {
            "precondition": "In <abilities> are abilities you have, and there is a <user_request>. "
                            "<history> shows events happened before you, "
                            "<latest_progress> shows the latest progress of <user_request>.",
            "instructions_you_must_follow_step_by_step": [{
                    "step": 1,
                    "action": "List events from <history> and <latest_progress> "
                              "which could be related to <user_request> (respectively and chronologically).",
                    # "second_action": "Extract and list all information related to <user_request> from <history> "
                    #                  "formatted one by one respectively.",
                    "additional": "For all details mentioned in <history> about <user_request>, "
                                  "you should preserve them in full, "
                                  "especially specific information with accuracy requirements "
                                  "such as datas, numbers, dates, names, etc.",
                    "limitation_for_step1": "Make it brief, concise and accurate."
                }, {
                    "step": 2,
                    "action": "Analyse whether the <user_request> has been fully and properly accomplished "
                              "according to your report in <step_1>, "
                              "and provide your analysis process and basis briefly.",
                    "limitation_for_step2": "Make it brief, concise and accurate."
                }, {
                    "step": 3,
                    "condition": "If the <user_request> has not been fully properly accomplished",
                    "action": "Analyse whether your <abilities> can complete the unfinished part of the <user_request>, "
                              "and provide the basis briefly according to information provided in <step_1>."
                }, {
                    "step": 4,
                    "condition": "If the <user_request> has not been fully properly accomplished and "
                                 "there is an ability in your <abilities> "
                                 "that can further advance the accomplishment of the <user_request> based on <history>.",
                    "first_action": "Plan and explain your next move briefly based on <history> "
                                    "for further advancing the <user_request>.",
                    "second_action": "Choose and provide the ability according to your next move"
                                     "(only one single ability can be chosen)",
                    "third_action": "After you have chosen the ability as next move, "
                                    "generate arguments for the ability(function) to achieve <next move>, "
                                    "before you generate arguments, explain why you give these arguments briefly."
                }, {
                    "step": 5,
                    "condition": "If the <user_request> has not been fully properly accomplished and "
                                 "there is no ability in your <abilities> "
                                 "that can further advance the accomplishment of the <user_request>",
                    "action": f'Provide the special ability called "{MISSION_FAILED}" '
                              'with "args:{}".'
                }, {
                    "step": 6,
                    "condition": "If the <user_request> has been fully and properly accomplished "
                                 "according to <history> and <user_request>",
                    "action": f'Provide the special ability called "{MISSION_COMPLETE}" '
                              'with "args:{}".'
                }
            ],
            "be_aware_of_sequence_of_movements": 'Ensure that actions be taken in the proper order '
                                                 'according to <user_request>.',
            "output_format": "{step1_thought_process}\n{step2_thought_process}\n"
                             "{step3_thought_process}\n{step4_thought_process}\n"
                             "{step5_thought_process}\n{step6_thought_process}\n"
                             f"{SEPARATOR}\n"
                             'args:{'
                             '"{name_of_param_1}":{value_for_param_1},'
                             '"{name_of_param_2}":{value_for_param_2},'
                             '"{name_of_param_{n}}":{value_for_param_{n}}'
                             '}\n'
                             f'ability:[ability.name]\n{END}',
            "limitation_for_thought_process_output": "Thought processes of all steps(from 1 to 6) should be provided.",
            "limitation_for_args_output_format": f'The "{SEPARATOR}" pattern should be after '
                                                 f'all the thought processes and before the <args and ability>.'
                                                 f'The <args> should be after the "{SEPARATOR}" pattern.'
                                                 'The <args> should be well formatted in JSON!!'
                                                 'In <args> you only gives the arguments for the chosen one ability.'
                                                 'The <ability> should be after <args>.',
            "hint_for_separation_pattern": f'The "{SEPARATOR}" pattern which separates <thought processes> and '
                                           '<args and ability> is absolutely important, do not forget to place it.',
            "hint_for_end_pattern": f'The "{END}" pattern marks the end of your whole response, '
                                    f'no more words are allowed after "{END}" pattern. '
                                    f'The "{END}" pattern is absolutely important, do not forget to place it '
                                    'in the end of your response.',
            "output_example": OUTPUT_EXAMPLE,
            "hint_for_output": 'You must strictly follow the format in <output_format>! '
                               'You should refer to example in <output_example>!',
            "user_request": request,
            "history": history,
            "latest_progress": latest_progress,
            "hint_for_latest_progress": "The <latest_progress> shows the previous move.",
            "abilities": abilities_dict,
            "limitation_1_for_ability_choosing": "Only one ability can be chosen.",
            "limitation_2_for_ability_choosing": "You can only use the abilities listed in <abilities>.",
            "limitation_for_ability_output_format": 'The ability should be after the args. '
                                                    'The ability name should be surrounded by "[ ]".',
            "limitation_for_args": f'You must make sure the parameter_names you provide '
                                   f'for <args> are real and correct according to <abilities>!'
        }
        prompt = json.dumps(prompt_dict, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'NextMovePrompt: {self.prompt}')

    # noinspection PyUnusedLocal,DuplicatedCode
    def invoke(self, model: BaseChatModel, max_retry: int = 6) -> BeforeActionTakenMessage | bool:
        result: str = str()
        count: int = 0
        exclamation = '!'
        tmp_prompt = self.prompt
        while True:
            # noinspection DuplicatedCode
            if count > 0:
                if count <= max_retry:
                    log.warning(f'NextMovePromptWarn: incorrectly formatted. Retry: {count}')
                else:
                    log.warning(f'NextMovePromptWarn: max retry exceeded.')
                    raise TooDumbException(model)
            count += 1
            result = model.invoke(tmp_prompt).content
            log.debug(f"Next move thought process: \n{result}")
            _accurate_action_str = result[result.rfind(SEPARATOR) + len(SEPARATOR):result.rfind(END)]
            if (result.count(SEPARATOR) == 1
                    and result.count(END) == 1
                    and _accurate_action_str.count('ability:') == 1
                    and _accurate_action_str.count('args:') == 1):
                tmp_prompt_dict = None
                if isinstance(tmp_prompt, str):
                    tmp_prompt_dict = json.loads(tmp_prompt)
                tmp_prompt_dict_prompt_str = json.dumps(tmp_prompt_dict.get('prompt'), ensure_ascii=False)
                __additional_prompt = tmp_prompt_dict.get('additional_prompt', '')
                if len(__additional_prompt) > 0:
                    __additional_prompt += f"\n{'-' * 5}\n"
                tmp_prompt_dict_prompt_str += f"{__additional_prompt}"
                result = _accurate_action_str
                args = json.loads(result[result.find('{'):result.rfind('}') + 1].strip())
                result = result[result.rfind('}') + 1:]
                ability_name: str = result[result.find('['):result.rfind(']') + 1].strip()[1:-1]
                if ability_name not in self.__ability_names:
                    tmp_prompt = (f'{tmp_prompt_dict_prompt_str}There is no ability called "{ability_name}", '
                                  f'These abilities are available for you to choose: {self.__ability_names}.')
                    tmp_prompt = Prompt.construct_prompt(tmp_prompt, '')
                    continue
                if (ability_name.startswith(AGENTIC_ABILITY_PREFIX)
                        or MISSION_COMPLETE in ability_name or ability_name in MISSION_COMPLETE
                        or MISSION_FAILED in ability_name or ability_name in MISSION_FAILED
                        or MAKE_FINAL_RESPONSE in ability_name or ability_name in MAKE_FINAL_RESPONSE):
                    break
                _ability = None
                _wrong_param = False
                _wrong_param_names = list()
                for ability in self.abilities:
                    if ability.name == ability_name:
                        _ability = ability
                if _ability is not None:
                    for _k in args.keys():
                        if _k not in _ability.parameters.keys():
                            _wrong_param = True
                            _wrong_param_names.append(_k)
                if not _wrong_param:
                    break
                else:
                    tmp_prompt = (f'{tmp_prompt_dict_prompt_str}For ability called "{ability_name}", '
                                  f'these parameter_names are incorrect: {_wrong_param_names}, '
                                  f"correct parameter_names: {_ability.to_dict().get('parameters_required', [])};")
                    tmp_prompt = Prompt.construct_prompt(tmp_prompt, '')
                    continue
            tmp_prompt = (f'{self.prompt}Attention_{count}: '
                          f'You must strictly follow the format in <output_format>{count * 2 * exclamation} '
                          f'You should refer to example in <output_example>{count * 2 * exclamation}')
            tmp_prompt = Prompt.construct_prompt(tmp_prompt, '')
        if ability_name.__contains__(MISSION_COMPLETE) or ability_name.__contains__(MAKE_FINAL_RESPONSE):
            return True
        for ability in self.abilities:
            if ability.name == ability_name:
                return BeforeActionTakenMessage(ability=ability, arguments=args)
        return False
