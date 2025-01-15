import hashlib
import json
import logging
import random
import datetime
import time
from typing import Callable
from typing_extensions import override
from collections import OrderedDict

from langchain_core.language_models import BaseChatModel

from ceo.ability.agentic_ability import PREFIX as AGENTIC_ABILITY_PREFIX
from ceo.brain.base_agent import BaseAgent
from ceo.brain.hook.before_action_taken import BeforeActionTaken
from ceo.brain.hook.after_action_taken import AfterActionTaken
from ceo.brain.hook.base_hook import BaseHook
from ceo.brain.memory_augment import MemoryAugment
from ceo.enum.Personality import Personality
from ceo.message.all_done_message import AllDoneMessage
from ceo.message.after_action_taken_message import AfterActionTakenMessage
from ceo.prompt import (
    NextMovePrompt,
    ExecutorPrompt,
    IntrospectionPrompt
)

PRUDENT_P = 0.25
PRUDENT_BETA = 1.45
INQUISITIVE_P = 0.05
INQUISITIVE_BETA = 1.25
log = logging.getLogger('ceo')


class Agent(BaseAgent, MemoryAugment):
    def __init__(self, abilities: list[Callable],
                 brain: BaseChatModel, name: str = '',
                 personality: Personality = Personality.PRUDENT,
                 request: str = '', memory: OrderedDict | None = None):
        BaseAgent.__init__(self, abilities=abilities, brain=brain, name=name, request=request)
        MemoryAugment.__init__(self, memory=memory)
        self.__expected_step = 0
        if personality == Personality.PRUDENT:
            self._p = self.__base_p = PRUDENT_P
            self._beta = PRUDENT_BETA
        elif personality == Personality.INQUISITIVE:
            self._p = self.__base_p = INQUISITIVE_P
            self._beta = INQUISITIVE_BETA

    @property
    def p(self) -> float:
        return self._p

    @property
    def base_p(self) -> float:
        return self.__base_p

    @property
    def beta(self) -> float:
        return self._beta

    @override
    def bring_in_memory(self, memory: OrderedDict):
        self._memory.update(memory)
        log.debug(f'Agent: {self._name}; '
                  f'Memory brought in: {len(memory.keys())};')
        return self

    @override
    def reposition(self):
        BaseAgent.reposition(self)
        self._memory = OrderedDict()
        self.__expected_step = 0
        self._p = self.__base_p
        return self

    @override
    def assign(self, request: str):
        BaseAgent.assign(self, request)
        return self.reposition()

    @override
    def reassign(self, request: str):
        return self.assign(request)

    @override
    def relay(self, request: str, request_by_step: str):
        self._request = request
        self._request_by_step = request_by_step
        return self.reposition()

    @override
    def just_do_it(self, *args, **kwargs) -> AllDoneMessage:
        __after_action_taken_hook: AfterActionTaken | Callable = BaseHook.do_nothing()
        __before_action_taken_hook: BeforeActionTaken | Callable = BaseHook.do_nothing()
        for _arg in args:
            if isinstance(_arg, AfterActionTaken):
                __after_action_taken_hook = _arg
            if isinstance(_arg, BeforeActionTaken):
                __before_action_taken_hook = _arg
        # todo __before_action_taken_hook implementation
        __start_time = time.perf_counter()
        if self.__expected_step < 1:
            self.estimate_step()
        log.debug(f'Agent: {self._name}; Expected steps: {self.__expected_step}; Request: "{self._request}";')
        stop = False
        while True:
            if self._act_count > self.__expected_step:
                stop = self.stop()
                self.penalize()
            next_move = False
            if not stop:
                combined_request = {
                    'raw_request': self._request,
                    'request_by_step': self._request_by_step
                }
                next_move = NextMovePrompt(
                    request=combined_request,
                    abilities=self._abilities,
                    history=self.memory
                ).invoke(self._model)
                if not isinstance(next_move, bool):
                    action, args = next_move
                    if action.name.startswith(AGENTIC_ABILITY_PREFIX):
                        args = {
                            'request': self._request,
                            'request_by_step': self._request_by_step,
                            'memory': self.memory,
                            'after_action_taken_hook': __after_action_taken_hook
                        }
                    __after_execution_msg = ExecutorPrompt(args=args, action=action).invoke(model=self._model)
                    self.memorize(__after_action_taken_hook(self, __after_execution_msg))
                    self._act_count += 1
                    continue
            brief_conclusion, response = IntrospectionPrompt(
                request=self._request,
                history=self.memory,
                self_info=self.introduction
            ).invoke(self._model)
            __time_used = time.perf_counter() - __start_time
            __step_count = self._act_count
            self.reposition()
            log.debug(f'Agent: {self._name}; Conclusion: {brief_conclusion};')
            log.debug(f'Agent: {self._name}; Step count: {__step_count}; Time used: {__time_used} seconds;')
            return AllDoneMessage(
                success=next_move,
                conclusion=brief_conclusion,
                raw_response=response,
                time_used=__time_used,
                step_count=__step_count
            )

    def assign_with_memory(self, request: str, memory: OrderedDict):
        return self.assign(request).bring_in_memory(memory)

    def estimate_step(self):
        if self._request_by_step == '':
            self.__expected_step = 0
            return
        self.__expected_step = len(self.plan(_log=False))
        return self

    def set_expected_step(self, expected_step: int):
        self.__expected_step = expected_step
        return self

    def memorize(self, action_taken: AfterActionTakenMessage):
        if action_taken is None:
            return self
        now = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S.%f')
        _tmp_action_taken = action_taken.to_dict()
        if 'summarization' in _tmp_action_taken.keys():
            del _tmp_action_taken['summarization']
        if _tmp_action_taken.get('ability', str()).startswith(AGENTIC_ABILITY_PREFIX):
            if 'choice' in _tmp_action_taken.keys():
                _tmp_action_taken['choice'] = 'Ask for a favor.'
        new_memory = {
            "timestamp": now,
            "agent_name": self._name,
            f"message_from_{self._name}": action_taken.summarization,
            f'action_taken_by_{self._name}': _tmp_action_taken
        }
        mem_hash = hashlib.md5(json.dumps(new_memory, ensure_ascii=False).encode()).hexdigest()
        self._memory[f"agent:[{self._name}] at:[{now}] hash:[{mem_hash}]"] = new_memory
        log.debug(f'Agent: {self._name}; Memory size: {len(self._memory.keys())}; Memory update: {action_taken.summarization};')
        return self

    def stop(self) -> bool:
        resample = 3
        log.debug(f'Agent: {self._name}; Termination Probability(p): {self._p}; Penalty Rate(beta): {self._beta};')
        rand_sum = 0.0
        for i in range(resample):
            rand_sum += random.uniform(0, 1)
        rand_avg = rand_sum / resample
        if rand_avg > self._p:
            return False
        return True

    def penalize(self):
        self._p = (self._beta * self._p) % 1.0
        return self

    def set_penalty(self, p: float, beta: float):
        self._p = self.__base_p = p
        self._beta = beta
        return self

    def change_personality(self, personality: Personality):
        if personality == Personality.PRUDENT:
            return self.set_penalty(p=PRUDENT_P, beta=PRUDENT_BETA)
        elif personality == Personality.INQUISITIVE:
            return self.set_penalty(p=INQUISITIVE_P, beta=INQUISITIVE_BETA)
        return self
