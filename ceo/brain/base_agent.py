import abc
import hashlib
import inspect
import json
import logging
import random
import time
from typing import Callable

from langchain_core.language_models import BaseChatModel

from ceo.ability.agentic_ability import Ability, PREFIX as AGENTIC_ABILITY_PREFIX
from ceo.ability.mcp_ability import McpAbility
from ceo.message.all_done_message import AllDoneMessage
from ceo.prompt import (
    SchedulerPrompt,
    RequestResolverPrompt,
    SelfIntroducePrompt
)

log = logging.getLogger('ceo')
SYSTEM_ABILITY_PREFIX = '__SystemAbility__'


class BaseAgent:
    def __init__(self, abilities: list[Callable], brain: BaseChatModel, name: str = '', request: str = ''):
        self._abilities = list()
        self._act_count = 0
        self._name = name
        self._model = brain
        self._request = self._request_by_step = str()
        if request is not None and request != '':
            self._request, self._request_by_step = RequestResolverPrompt(request).invoke(self._model)
        if self._name is None or len(self._name) < 1:
            self._name = self._generate_name()
        self.__prev_results = list()
        self.__schedule = list()
        self._introduction = str()
        self.grant_abilities(abilities)

    @property
    def abilities(self) -> list[Ability]:
        return self._abilities

    @property
    def name(self) -> str:
        return self._name

    @property
    def introduction(self) -> str:
        return self._introduction

    @property
    def brain(self) -> BaseChatModel:
        return self._model

    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __str__(self):
        return self.__repr__()

    def _generate_name(self) -> str:
        __abilities_ls = [ability.to_dict() for ability in self.abilities]
        __tmp_bytes = f'{__abilities_ls}{time.time()}{random.uniform(0, 10 ** 3)}'.encode('utf-8')
        __tmp_str = hashlib.md5(__tmp_bytes).hexdigest()
        __sample_str = ''.join(random.sample(__tmp_str, 6))
        return f'智能體{__sample_str}型號'

    def to_dict(self) -> dict:
        __model_dict = self._model.dict()
        model_name = __model_dict.get('model_name', __model_dict.get('_type', 'unknown'))
        return {
            "name": self.name,
            "brain": model_name,
            "abilities": [ability.to_dict() for ability in self.abilities]
        }

    def introduce(self, update: bool = True) -> str:
        # noinspection PyUnusedLocal
        def get_your_info(*args, **kwargs) -> dict:
            """
            What does this ability do: To get your personal information.
            In any case, the [__SystemAbility__get_your_info] ability can only be used once!!
            :return: All information of yourself.
            """
            _info_dict = self.to_dict()
            if 'brain' in _info_dict:
                del _info_dict['brain']
            return {
                'success': True,
                'info': _info_dict
            }

        get_your_info.__name__ = f'{SYSTEM_ABILITY_PREFIX}{get_your_info.__name__}'
        self.grant_ability(get_your_info, update_introduction=False)
        if update:
            self._introduction = SelfIntroducePrompt(agent=self).invoke(self._model)
        return self._introduction

    def grant_ability(self, ability: Callable | Ability, update_introduction: bool = True):
        abilities_except_mcp = [_a for _a in self._abilities if not isinstance(_a, McpAbility)]
        if isinstance(ability, Ability):
            for _ability in abilities_except_mcp:
                both_agentic = (_ability.name.startswith(AGENTIC_ABILITY_PREFIX)
                                and ability.name.startswith(AGENTIC_ABILITY_PREFIX))
                both_not_agentic = (not _ability.name.startswith(AGENTIC_ABILITY_PREFIX)
                                    and not ability.name.startswith(AGENTIC_ABILITY_PREFIX))
                if both_agentic:
                    if ability.name == _ability.name:
                        return
                elif both_not_agentic:
                    if inspect.getsource(ability.function) == inspect.getsource(_ability.function):
                        return
            self._abilities.append(ability)
        else:
            for _ability in abilities_except_mcp:
                if not _ability.name.startswith(AGENTIC_ABILITY_PREFIX):
                    if inspect.getsource(ability) == inspect.getsource(_ability.function):
                        return
            self._abilities.append(Ability(ability))
        self.introduce(update=update_introduction)

    def grant_abilities(self, abilities: list[Callable | Ability]):
        prev_size = len(self.abilities)
        for ability in abilities:
            self.grant_ability(ability, update_introduction=False)
        self.introduce(update=(prev_size != len(self.abilities)))

    def deprive_ability(self, ability: Callable | Ability, update_introduction: bool = True):
        abilities_except_mcp = [_a for _a in self._abilities if not isinstance(_a, McpAbility)]
        removed = False
        if not isinstance(ability, Ability):
            ability = Ability(ability)
        for _ability in abilities_except_mcp:
            both_agentic = (_ability.name.startswith(AGENTIC_ABILITY_PREFIX)
                            and ability.name.startswith(AGENTIC_ABILITY_PREFIX))
            both_not_agentic = (not _ability.name.startswith(AGENTIC_ABILITY_PREFIX)
                                and not ability.name.startswith(AGENTIC_ABILITY_PREFIX))
            if both_agentic:
                if _ability.name == ability.name:
                    self._abilities.remove(_ability)
                    removed = True
            elif both_not_agentic:
                if inspect.getsource(_ability.function) == inspect.getsource(ability.function):
                    self._abilities.remove(_ability)
                    removed = True
        self.introduce(update=(removed and update_introduction))

    def deprive_abilities(self, abilities: list[Callable | Ability]):
        prev_size = len(self.abilities)
        for ability in abilities:
            self.deprive_ability(ability, update_introduction=False)
        self.introduce(update=(prev_size != len(self.abilities)))

    def plan(self, _log: bool = True) -> list:
        scheduling = SchedulerPrompt(request=self._request_by_step, abilities=self._abilities)
        self.__schedule = scheduling.invoke(self._model)
        if _log:
            log.debug(f'Agent: {self._name}; Schedule: {[_.name for _ in self.__schedule]}; Request: "{self._request}";')
        return self.__schedule

    def reposition(self):
        self.__prev_results = list()
        self.__schedule = list()
        self._act_count = 0
        return self

    def assign(self, request: str):
        self._request, self._request_by_step = (
            RequestResolverPrompt(request=request).invoke(self._model))
        return self.reposition()

    def reassign(self, request: str):
        return self.assign(request)

    def relay(self, request: str, request_by_step: str):
        self._request = request
        self._request_by_step = request_by_step
        return self.reposition()

    @abc.abstractmethod
    def just_do_it(self, *args, **kwargs) -> AllDoneMessage: ...
