import logging

from .brain.lm import (
    get_openai_model,
    get_dashscope_model,
    get_deepseek_model
)
from .brain.agent import Agent
from .brain.mcp_agent import McpAgent
from .util.agentic import agentic
from .util.ability import ability
from .enum import Personality
from .util.synchronized_call import synchronized_call, sync_call
from .ability import (
    Ability,
    McpAbility,
    AgenticAbility,
    McpAgenticAbility
)
from .util.mcp_session import (
    StdioMcpConfig,
    SseMcpConfig,
    WebsocketMcpConfig,
    mcp_session
)

__AUTHOR__ = '吴子豪 / Vortez Wohl'
__EMAIL__ = 'vortez.wohl@gmail.com'
__VERSION__ = '1.0.0'
__GITHUB__ = 'https://github.com/vortezwohl'
__BLOG__ = 'https://vortezwohl.github.io'

logger = logging.getLogger('autono')
logger.setLevel(logging.ERROR)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(name)s : %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger = logging.getLogger('autono.prompt')
logger.setLevel(logging.ERROR)
logger = logging.getLogger('autono.ability')
logger.setLevel(logging.ERROR)
logger = logging.getLogger('autono.agent')
logger.setLevel(logging.ERROR)
