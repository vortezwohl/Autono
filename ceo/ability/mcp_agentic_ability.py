import inspect

from typing_extensions import override

from ceo.ability.agentic_ability import AgenticAbility
from ceo.brain.base_agent import BaseAgent


class McpAgenticAbility(AgenticAbility):
    def __init__(self, agent: BaseAgent):
        super().__init__(agent)

    @override
    async def __call__(self, *args, **kwargs) -> str:
        if inspect.iscoroutinefunction(self._agent.just_do_it):
            all_done = await self._agent.just_do_it(*self.relay(*args, **kwargs))
        else:
            all_done = self._agent.just_do_it(*self.relay(*args, **kwargs))
        return all_done.response_for_agent
