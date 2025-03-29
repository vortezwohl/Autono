from collections import OrderedDict

from typing_extensions import Callable, override
from langchain_core.language_models import BaseChatModel
from mcp import StdioServerParameters, stdio_client, ClientSession

from ceo.ability.agentic_ability import Ability
from ceo.ability.stdio_mcp_ability import StdioMcpAbility
from ceo.brain.agent import Agent
from ceo.enum import Personality
from ceo.util.synchronized_call import synchronized_call


class StdioMcpAgent(Agent):
    def __init__(self, mcp_config: StdioServerParameters,
                 brain: BaseChatModel, name: str = '',
                 personality: Personality = Personality.PRUDENT,
                 request: str = '', memory: OrderedDict | None = None):
        super().__init__(abilities=[], brain=brain,
                         name=name, personality=personality,
                         request=request, memory=memory)
        self._mcp_config = mcp_config
        self.fetch_abilities(self.mcp_config)

    def fetch_abilities(self, mcp_config: StdioServerParameters):
        async def __fetch() -> list[StdioMcpAbility]:
            nonlocal mcp_config
            mcp_tools = list()
            async with stdio_client(mcp_config) as rw:
                async with ClientSession(*rw) as session:
                    await session.initialize()
                    _tmp_tools = (await session.list_tools()).tools
                    mcp_tools = [StdioMcpAbility(mcp_tool=_tool, mcp_config=mcp_config) for _tool in _tmp_tools]
            return mcp_tools

        self.grant_abilities(synchronized_call(__fetch))

    @override
    def grant_ability(self, ability: Callable | Ability | StdioMcpAbility, update_introduction: bool = True):
        if isinstance(ability, StdioMcpAbility):
            self._abilities.append(ability)
            self.introduce(update=update_introduction)
        else:
            super().grant_ability(ability, update_introduction=update_introduction)

    @override
    def grant_abilities(self, abilities: list[Callable | Ability | StdioMcpAbility]):
        super().grant_abilities(abilities=abilities)

    @override
    def deprive_ability(self, ability: Callable | Ability | StdioMcpAbility, update_introduction: bool = True):
        removed = False
        if isinstance(ability, StdioMcpAbility):
            if ability in self.abilities:
                self._abilities.remove(ability)
                removed = True
            self.introduce(update=(removed and update_introduction))
        else:
            super().deprive_ability(ability, update_introduction=update_introduction)

    @override
    def deprive_abilities(self, abilities: list[Callable | Ability | StdioMcpAbility]):
        super().deprive_abilities(abilities=abilities)

    @property
    def mcp_config(self):
        return self._mcp_config
