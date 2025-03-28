import asyncio
import threading

from mcp import ClientSession
from mcp.types import Tool
from typing_extensions import override

from ceo.ability.base_ability import BaseAbility

DEFAULT_RETURNS = "<class 'str'>"
NONE = '/'


class McpAbility(BaseAbility):
    def __init__(self, mcp_tool: Tool, mcp_client_session: ClientSession):
        self._mcp_client_session = mcp_client_session
        _descr = {
            'brief_description': mcp_tool.description,
            'parameters': [
                {'parameter_name': k, 'type': v.get("type", DEFAULT_RETURNS),
                 'description': v.get('description', NONE)}
                for k, v in mcp_tool.inputSchema.get('properties', dict()).items()
            ]
        }
        super().__init__(
            name=mcp_tool.name,
            description=_descr,
            parameters=mcp_tool.inputSchema.get('properties', dict()),
            returns=DEFAULT_RETURNS
        )

    async def call_mcp_tool(self, *args, **kwargs):
        return await self._mcp_client_session.call_tool(name=self.name, arguments=kwargs)

    @override
    def __call__(self, *args, **kwargs):
        __res = None

        def __func(loop: asyncio.AbstractEventLoop):
            nonlocal __res, args, kwargs
            try:
                __res = loop.run_until_complete(self.call_mcp_tool(*args, **kwargs))
            finally:
                loop.close()

        __thread = threading.Thread(
            target=__func,
            args=(asyncio.new_event_loop(),)
        )
        __thread.start()
        __thread.join(timeout=None)
        return __res

    @property
    def session(self):
        return self._mcp_client_session
