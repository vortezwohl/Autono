import logging

from ceo.brain.base_agent import BaseAgent
from ceo.brain.mcp_agent import McpAgent
from ceo.ability.agentic_ability import AgenticAbility
from ceo.ability.mcp_agentic_ability import McpAgenticAbility

log = logging.getLogger('ceo.ability')


def agentic(agent: BaseAgent):
    if isinstance(agent, McpAgent):
        return lambda func: McpAgenticAbility(agent)
    return lambda func: AgenticAbility(agent)
