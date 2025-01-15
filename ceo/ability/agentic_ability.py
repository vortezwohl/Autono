import json
import logging
from collections import OrderedDict

from typing_extensions import override

from ceo.ability import Ability
from ceo.brain.memory_augment import MemoryAugment

PREFIX = '__AgenticAbility__'

from ceo.brain.hook.after_action_taken import BaseHook
from ceo.brain.base_agent import BaseAgent

log = logging.getLogger('ceo.ability')


class AgenticAbility(Ability):
    def __init__(self, agent: BaseAgent | MemoryAugment):
        try:
            _test_mem = agent.memory
        except AttributeError:
            raise TypeError("The 'agent' of AgenticAbility should be instance of 'ceo.Agent'.")
        self._agent = agent
        self.__name__ = f'{PREFIX}talk_to_{agent.name}'
        self.__doc__ = json.dumps({
            "description": {
                "brief_description": f'Initiates a conversation with "{agent.name}" to use its abilities.',
                "detailed_description": f"First, carefully consider and explore {agent.name}'s "
                                        "potential abilities in solving your tasks, "
                                        f"then, if you need {agent.name}'s help, "
                                        "you must tell comprehensively, precisely "
                                        f"and exactly what you need {agent.name} to do.",
                f"self_introduction_from_{agent.name}": agent.introduction,
                "hint": f"By reading <self_introduction_from_{agent.name}>, you can learn what {agent.name} can do, "
                        f"and then decide whether to initiates a conversation with {agent.name} "
                        "according to its abilities.",
                "parameters": [{
                    "request": {
                        "name": "request",
                        "type": "str",
                        "description": f"A brief instruction to be processed by {agent.name}."
                    },
                    "request_by_step": {
                        "name": "request_by_step",
                        "type": "str",
                        "description": "A comprehensive, precise and exact instruction "
                                       f"to be processed by {agent.name}."
                    },
                    "memory": {
                        "name": "memory",
                        "type": "dict",
                        "description": "/"
                    }
                }],
                "returns": {
                    "type": "str",
                    "description": f"{agent.name}'s response to your instruction."
                }
            }
        }, ensure_ascii=False)
        super().__init__(self)
        log.debug(f'Agent dispatcher generated. {self.__name__}: {self.__doc__}')

    @override
    def __call__(self, request: str, request_by_step: str, memory: OrderedDict, *args, **kwargs) -> str:
        before_action_taken_hook = kwargs.get('before_action_taken_hook', None)
        after_action_taken_hook = kwargs.get('after_action_taken_hook', None)
        if before_action_taken_hook is None:
            before_action_taken_hook = BaseHook.do_nothing()
        if after_action_taken_hook is None:
            after_action_taken_hook = BaseHook.do_nothing()
        self._agent.relay(request_by_step=request_by_step, request=request)
        self._agent.bring_in_memory(memory)
        return self._agent.just_do_it(before_action_taken_hook, after_action_taken_hook).response_for_agent
