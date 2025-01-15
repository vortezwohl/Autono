import asyncio
import inspect
import threading
from typing import Callable

from ceo.message.base_massage import BaseMessage
from ceo.brain.base_agent import BaseAgent


class BaseHook(Callable[[BaseAgent, BaseMessage], BaseMessage]):

    def __init__(self, function: Callable[[BaseAgent, BaseMessage], BaseMessage]):
        self._function = function

    def __call__(self, agent: BaseAgent, message: BaseMessage):
        if inspect.iscoroutinefunction(self._function):
            __res = None

            def __func(loop: asyncio.AbstractEventLoop):
                nonlocal __res, agent, message
                try:
                    __res = loop.run_until_complete(self._function(agent, message))
                finally:
                    loop.close()

            __thread = threading.Thread(
                target=__func,
                args=(asyncio.new_event_loop(),)
            )
            __thread.start()
            __thread.join(timeout=None)
            return __res
        return self._function(agent, message)

    @staticmethod
    def do_nothing() -> Callable:
        return lambda agent, msg: msg
