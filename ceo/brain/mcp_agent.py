import logging
import time
from collections import OrderedDict

from typing_extensions import Callable, override
from langchain_core.language_models import BaseChatModel
from mcp import ClientSession

from ceo.ability.agentic_ability import PREFIX as AGENTIC_ABILITY_PREFIX
from ceo.ability.agentic_ability import Ability
from ceo.ability.base_ability import BaseAbility
from ceo.ability.mcp_ability import McpAbility
from ceo.brain.agent import Agent
from ceo.brain.hook import AfterActionTaken, BeforeActionTaken
from ceo.brain.hook.base_hook import BaseHook
from ceo.enum import Personality
from ceo.message import AllDoneMessage, AfterActionTakenMessage, BeforeActionTakenMessage
from ceo.prompt import ExecutorPrompt, IntrospectionPrompt, NextMovePrompt

log = logging.getLogger('ceo')


class McpAgent(Agent):
    def __init__(self, session: ClientSession,
                 brain: BaseChatModel, name: str = '',
                 personality: Personality = Personality.PRUDENT,
                 request: str = '', memory: OrderedDict | None = None):
        super().__init__(abilities=[], brain=brain,
                         name=name, personality=personality,
                         request=request, memory=memory)
        self._session = session

    async def fetch_abilities(self):
        async def __fetch() -> list[McpAbility]:
            _tmp_tools = (await self.session.list_tools()).tools
            mcp_tools = [McpAbility(mcp_tool=_tool, session=self.session) for _tool in _tmp_tools]
            return mcp_tools

        self.grant_abilities(await __fetch())
        return self

    @override
    def grant_ability(self, ability: Callable | Ability | McpAbility, update_introduction: bool = True):
        if isinstance(ability, McpAbility):
            self._abilities.append(ability)
            self.introduce(update=update_introduction)
        else:
            super().grant_ability(ability, update_introduction=update_introduction)

    @override
    def grant_abilities(self, abilities: list[Callable | Ability | McpAbility]):
        super().grant_abilities(abilities=abilities)

    @override
    def deprive_ability(self, ability: Callable | Ability | McpAbility, update_introduction: bool = True):
        removed = False
        if isinstance(ability, McpAbility):
            if ability in self.abilities:
                self._abilities.remove(ability)
                removed = True
            self.introduce(update=(removed and update_introduction))
        else:
            super().deprive_ability(ability, update_introduction=update_introduction)

    @override
    def deprive_abilities(self, abilities: list[Callable | Ability | McpAbility]):
        super().deprive_abilities(abilities=abilities)

    @override
    async def execute(self, args: dict, action: BaseAbility) -> AfterActionTakenMessage:
        return await ExecutorPrompt(action=action, args=args).ainvoke(self.brain)

    @override
    async def just_do_it(self, *args, **kwargs) -> AllDoneMessage:
        __after_action_taken_hook: AfterActionTaken | Callable = BaseHook.do_nothing()
        __before_action_taken_hook: BeforeActionTaken | Callable = BaseHook.do_nothing()
        for _arg in args:
            if isinstance(_arg, AfterActionTaken):
                __after_action_taken_hook = _arg
            if isinstance(_arg, BeforeActionTaken):
                __before_action_taken_hook = _arg
        __start_time = time.perf_counter()
        if self._expected_step < 1:
            self.estimate_step()
        log.debug(f'Agent: {self._name}; Expected steps: {self._expected_step}; Request: "{self._request}";')
        stop = False
        while True:
            if self._act_count > self._expected_step:
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
                if isinstance(next_move, BeforeActionTakenMessage):
                    next_move = __before_action_taken_hook(self, next_move)
                    action, args = next_move.ability, next_move.arguments
                    if action.name.startswith(AGENTIC_ABILITY_PREFIX):
                        args = {
                            'request': self._request,
                            'request_by_step': self._request_by_step,
                            'memory': self.memory,
                            'before_action_taken_hook': __before_action_taken_hook,
                            'after_action_taken_hook': __after_action_taken_hook
                        }
                    __after_execution_msg = await self.execute(args=args, action=action)
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

    @property
    def session(self) -> ClientSession:
        return self._session
