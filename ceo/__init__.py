import logging

from .brain.lm import (
    get_openai_model,
    get_dashscope_model,
    get_deepseek_model
)
from .brain.agent import Agent
from .ability import Ability, AgenticAbility
from .util import ability, agentic
from .enum import Personality

__AUTHOR__ = '吴子豪 / Vortez Wohl'
__EMAIL__ = 'vortez.wohl@gmail.com'
__VERSION__ = '0.12.0-preview'

logger = logging.getLogger('ceo')
logger.setLevel(logging.ERROR)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(name)s : %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

logger = logging.getLogger('ceo.prompt')
logger.setLevel(logging.ERROR)
logger = logging.getLogger('ceo.ability')
logger.setLevel(logging.ERROR)
logger = logging.getLogger('ceo.agent')
logger.setLevel(logging.ERROR)
