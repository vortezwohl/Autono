import logging

from autono.brain.base_agent import BaseAgent
from autono.brain.mcp_agent import McpAgent
from autono.ability.agentic_ability import AgenticAbility
from autono.ability.mcp_agentic_ability import McpAgenticAbility

log = logging.getLogger('autono.ability')


def agentic(agent: BaseAgent):
    if isinstance(agent, McpAgent):
        return lambda func: McpAgenticAbility(agent)
    return lambda func: AgenticAbility(agent)
