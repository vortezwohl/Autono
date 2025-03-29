from collections import OrderedDict

from typing_extensions import Callable, override
from langchain_core.language_models import BaseChatModel
from mcp import ClientSession

from ceo.ability.agentic_ability import Ability
from ceo.ability.mcp_ability import McpAbility
from ceo.brain.agent import Agent
from ceo.enum import Personality
from ceo.util.synchronized_call import synchronized_call


class McpAgent(Agent):
    def __init__(self, session: ClientSession,
                 brain: BaseChatModel, name: str = '',
                 personality: Personality = Personality.PRUDENT,
                 request: str = '', memory: OrderedDict | None = None):
        super().__init__(abilities=[], brain=brain,
                         name=name, personality=personality,
                         request=request, memory=memory)
        session.initialize()
        self._session = session
        self.fetch_abilities()

    def fetch_abilities(self):
        async def __fetch() -> list[McpAbility]:
            _tmp_tools = (await self.session.list_tools()).tools
            mcp_tools = [McpAbility(mcp_tool=_tool, session=self.session) for _tool in _tmp_tools]
            return mcp_tools

        self.grant_abilities(synchronized_call(__fetch))

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

    @property
    def session(self) -> ClientSession:
        return self._session
