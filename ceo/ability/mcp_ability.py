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

    @override
    async def __call__(self, *args, **kwargs):
        _res = await self.session.call_tool(name=self.name, arguments=kwargs)
        _status = 'SUCCESSFUL' if not _res.isError else 'FAILED'
        return (f'McpAbility(mcp_tool="{self.name}") was {_status}.\n'
                f'Result: "{_res.content}"')

    @property
    def session(self):
        return self._mcp_client_session
